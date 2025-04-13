"""Pure python implementation of the gimp xcf file format.

Currently supports:
	Loading xcf files
	Getting image hierarchy and info
	Getting image for each layer (PIL image)
Currently not supporting:
	Saving
	Programatically alter documents (add layer, etc)
	Rendering a final, compositied image
"""

from __future__ import annotations

from io import BytesIO
from typing import Any, NoReturn, TypeVar

import numpy as np
from blendmodes.blend import BlendType as BlendMode
from blendmodes.blend import blendLayersArray
from PIL import Image

from gimpformats import utils
from gimpformats.binaryiotools import IO
from gimpformats.enums import ImageProperties
from gimpformats.GimpChannel import GimpChannel
from gimpformats.GimpImageHierarchy import GimpImageHierarchy
from gimpformats.GimpIOBase import GimpBlendMode, GimpIOBase, camel_to_pascal_with_spaces
from gimpformats.GimpLayer import GimpLayer
from gimpformats.GimpPrecision import Precision
from gimpformats.utils import repr_indent_lines

T = TypeVar("T")


class GimpGroup:
	def __init__(self, name: Any) -> None:
		self.name: str = str(name)
		self.layer_options: GimpLayer | None = None
		self.children: list[GimpLayer | GimpGroup] = []

	def add_layer(self, layer: GimpLayer | GimpGroup) -> None:
		self.children.append(layer)

	def get_group(self, idx: int) -> GimpGroup:
		try:
			group = self
			group = self.children[idx]
			if not isinstance(group, GimpGroup):
				return self
			return group
		except IndexError:
			return self

	def __repr__(self) -> str:
		"""Get a textual representation of this object."""
		return f"<GimpGroup name={self.name} isGroup=True, numberChildren={len(self.children)}>"


class GimpDocument(GimpIOBase):
	"""Pure python implementation of the gimp file format.

	Has a series of attributes including the following:
	self._layers = None
	self._layerPtr = []
	self._channels = []
	self._channelPtr = []
	self.version = None
	self.width = 0
	self.height = 0
	self.baseColorMode = 0
	self.precision = None # Precision object
	self._data = None


	The image structure always starts at offset 0 in the XCF file.

	byte[9]     "gimp xcf " File type identification
	byte[4]     version     XCF version
	byte        0            Zero marks the end of the version tag.
	uint32      width        Width of canvas
	uint32      height       Height of canvas
	uint32      base_type    Color mode of the image; one of
								0: RGB color; 1: Grayscale; 2: Indexed color
	uint32      precision    Image precision; this field is only present for
							XCF 4 or over (since GIMP 2.10.0).
	property-list        Image properties
	,-----------------   Repeat once for each layer, topmost layer first:
	| pointer lptr       Pointer to the layer structure.
	`--
	pointer   0           Zero marks the end of the array of layer pointers.
	,------------------  Repeat once for each channel, in no particular order:
	| pointer cptr       Pointer to the channel structure.
	`--
	pointer   0           Zero marks the end of the array of channel pointers.
	,------------------  Repeat once for each path, in no particular order:
	| pointer cptr       Pointer to the vectors structure.
	`--
	pointer   0           Zero marks the end of the array of vectors pointers.


	"""

	def __init__(self, fileName: BytesIO | str | None = None) -> None:
		"""Pure python implementation of the gimp file format.

		Has a series of attributes including the following:
		self._layers = None
		self._layerPtr = []
		self._channels = []
		self._channelPtr = []
		self.version = None
		self.width = 0
		self.height = 0
		self.baseColorMode = 0
		self.precision = None # Precision object
		self._data = None

		See:
			https://gitlab.gnome.org/GNOME/gimp/blob/master/devel-docs/xcf.txt
		"""
		GimpIOBase.__init__(self, self)
		self._layers: list[GimpLayer] = []
		self._layerPtr: list[int] = []
		self._channels: list[GimpChannel] = []
		self._channelPtr: list[int] = []
		self.version = 11  # This is the most recent version
		self.width = 0
		self.height = 0
		self.baseColorMode = 0
		self.precision = None  # Precision object
		self._data = None
		self.fileName = None
		if fileName is not None:
			self.load(fileName)

	def load(self, fileName: BytesIO | str) -> None:
		"""Load a gimp xcf and decode the file. See decode for more on this process.

		:param fileName: can be a file name or a file-like object
		"""
		# self.__init__()
		self.fileName, data = utils.fileOpen(fileName)
		self.decode(data)

	def iterablePointerDecoder(self, ioBuf: IO, cls: type[T]) -> tuple[list[int], list[T]]:
		"""Iterate over a pointer as defined in the spec. This method is responsible for
		returning a list of int pointers (representing indexes in the XCF), and a list of types
		representing the data.

		EG.

		,-----------------
		| pointer lptr       layer structure.
		`--
		pointer   0

		:param IO ioBuf: The raw buffer representing the XCF doc
		:param T obj: create instances of this type (and decode into this)
		:return tuple[list[int], list[T]]:  list of int pointers (representing indexes
		in the XCF), and a list of types representing the data.
		"""
		pointers = []
		elems = []
		while True:
			ptr = self._pointerDecode(ioBuf)
			if ptr == 0:
				break
			pointers.append(ptr)
			elem = cls(self)
			elem.decode(ioBuf.data, ptr)
			elems.append(elem)

		return pointers, elems

	def decode(self, data: bytearray | bytes, index: int = 0) -> int:
		"""Decode the XCF Header to a GimpDocument.

		:param bytearray | bytes data: raw bytes representing the GimpDocument/XCF
		:param int index: An optional start index, only set this if you know what you're doing :)

		Note that this decode function is somewhat lazy with what is decoded. For example,
		for the layers, the pointers and basic layer info is decoded, in addition to the
		pointers to the image_hierarchy and masks. However, the actual image data is not loaded.

		Image data will be fetched when when calling descendants `.image` method as
		appropriate

		byte[9]     "gimp xcf "
		byte[4]     version
		byte        0
		uint32      width
		uint32      height
		uint32      base_type
		uint32      precision
		property-list        Image properties
		,-----------------
		| pointer lptr       layer structure.
		`--
		pointer   0
		,------------------
		| pointer cptr       channel structure.
		`--
		pointer   0
		,------------------
		| pointer cptr       vectors structure.
		`--
		pointer   0
		"""
		# Create a new IO buffer
		ioBuf = IO(data, index)
		# Check that the file is a valid gimp xcf
		if ioBuf.getbytearray(9) != b"gimp xcf ":
			msg = "Not a valid GIMP file"
			raise RuntimeError(msg)
		# Grab the file version
		version = ioBuf.cString
		if version == "file":
			self.version = 0
		else:
			self.version = int(version[1:])
		# Grab the width, height, baseColorMode and the precision data
		self.width = ioBuf.u32
		self.height = ioBuf.u32
		self.baseColorMode = ioBuf.u32
		self.precision = Precision()
		self.precision.decode(self.version, ioBuf)

		# Decode the list of properties, as noted in the spec this should be nul terminated
		self._propertiesDecode(ioBuf)

		# Get the layers and add the pointers to them, this should be nul terminated
		self._layerPtr, self._layers = self.iterablePointerDecoder(ioBuf, GimpLayer)

		# Get the channels and add the pointers to them, this should be nul terminated
		self._channelPtr, self._channels = self.iterablePointerDecoder(ioBuf, GimpChannel)

		# Return the offset representing the end of the XCF header
		return ioBuf.index

	def encode(self) -> bytearray:
		"""Encode to bytearray.

		Similarly to decode, we must start by constructing the XCF header, though we must
		then add the bytes returned when calling descendants `.encode` method as
		appropriate


		byte[9]     "gimp xcf "
		byte[4]     version
		byte        0
		uint32      width
		uint32      height
		uint32      base_type
		uint32      precision
		property-list        Image properties
		,-----------------
		| pointer lptr       layer structure.
		`--
		pointer   0
		,------------------
		| pointer cptr       channel structure.
		`--
		pointer   0
		,------------------
		| pointer cptr       vectors structure.
		`--
		pointer   0

		"""
		# Create a new IO buffer
		ioBuf = IO()
		# The file is a valid gimp xcf
		ioBuf.addbytearray("gimp xcf ")
		# Set the file version
		ioBuf.addbytearray(f"v{self.version:03d}\0")
		# Set other attributes as outlined in the spec
		ioBuf.u32 = self.width
		ioBuf.u32 = self.height
		ioBuf.u32 = self.baseColorMode
		# Set precision data using the class and ioBuf buffer
		if self.precision is None:
			self.precision = Precision()
		self.precision.encode(self.version, ioBuf)
		# List of properties
		ioBuf.addbytearray(self._propertiesEncode(ImageProperties))
		dataAreaIdx = (
			ioBuf.index
		)  ## + self.pointerSize * (len(self.raw_layers) + len(self._channels))
		dataAreaIO = IO()
		# Set the layers and add the pointers to them
		for layer in self.raw_layers:
			ioBuf.index = dataAreaIdx + dataAreaIO.index
			dataAreaIO.addbytearray(layer.encode())
		# Set the channels and add the pointers to them
		for channel in self._channels:
			ioBuf.index = dataAreaIdx + dataAreaIO.index
			dataAreaIO.addbytearray(channel.encode())
		ioBuf.addbytearray(dataAreaIO)
		# Return the data
		return ioBuf.data

	def forceFullyLoaded(self) -> None:
		"""Make sure everything is fully loaded from the file."""
		for layer in self.raw_layers:
			layer.forceFullyLoaded()
		# for channel in self._channels:
		# 	channel.forceFullyLoaded()
		# no longer try to get the data from file
		self._layerPtr = None
		self._channelPtr = None
		self._data = None

	@property
	def raw_layers(self) -> list[GimpLayer]:
		"""Decode the image's layers if necessary.

		TODO: need to do the same thing with self.Channels
		"""
		if len(self._layers) == 0:
			self._layers = []
			for ptr in self._layerPtr or []:
				layer = GimpLayer(self)
				layer.decode(self._data, ptr)
				self._layers.append(layer)
			# # add a reference back to this object so it doesn't go away while array is in use
			# self._layers.parent = self
			# # override some internal methods so we can do more with them
			# self._layers._actualDelitem_ = self._layers.__delitem__
			# self._layers.__delitem__ = self.deleteRawLayer
			# self._layers._actualSetitem_ = self._layers.__setitem__
			# self._layers.__setitem__ = self.setRawLayer
		return self._layers

	def getLayer(self, index: int) -> GimpLayer | GimpGroup:
		"""Return a given layer."""

		root_group = self.walkTree()
		
		if -len(root_group.children) < index < len(root_group.children):
			return root_group.children[index]

		msg = f"{index} is out of bounds for GimpDocument [{len(root_group.children)}]"
		raise RuntimeError(msg)

	def setRawLayer(self, index: int, layer: GimpLayer) -> None:
		"""Assign to a given layer."""
		self.forceFullyLoaded()
		self._layerPtr = None  # no longer try to use the pointers to get data
		self.raw_layers._actualSetitem_(index, layer)

	def newLayer(self, name: str, image: Image.Image, index: int = -1) -> GimpLayer:
		"""Create a new layer based on a PIL image.

		Args:
		----
			name (str): a name for the new layer
			image (Image.Image): pil image
			index (int, optional): where to insert the new layer (default=top). Defaults to -1.

		Returns:
		-------
			GimpLayer: newly created GimpLayer object

		"""
		layer = GimpLayer(self, name, image)
		layer.imageHierarchy = GimpImageHierarchy(self, image=image)
		self.insertRawLayer(layer, index)
		return layer

	def insertRawLayer(self, layer: GimpLayer, index: int = -1) -> None:
		"""Insert a layer object at a specific position.

		:param layer: the new layer to insert
		:param index: where to insert the new layer (default=top)
		"""
		self._layers.insert(index, layer)

	def deleteRawLayer(self, index: int) -> None:
		"""Delete a layer."""
		self._layers.pop(index)

	def walkTree(self) -> GimpGroup:
		root_group = GimpGroup(
			name="#",
		)

		for layer in self.raw_layers:
			parent = root_group

			# Determine the correct parent list using itemPath hierarchy
			if layer.itemPath is not None:
				for level_index in layer.itemPath[:-1]:
					parent = parent.get_group(level_index)

			# Append layer to its parent group
			if layer.isGroup:
				group = GimpGroup(name=layer.name)
				parent.add_layer(group)
				group.layer_options = layer
			else:
				parent.add_layer(layer)  # Regular layers are stored as-is

		return root_group

	@property
	def image(self) -> Image.Image:
		"""Generates a final, compiled image by processing layers and groups."""

		root_group = self.walkTree()

		# Flatten the processed hierarchy into a final image
		return self.render(root_group)

	def save(self, filename: str | BytesIO | None = None) -> NoReturn:
		"""Save this gimp image to a file."""

		# Save not yet implemented so for now throw
		# an except so we don't corrupt the file
		# raise NotImplementedError

		self.forceFullyLoaded()
		utils.save(self.encode(), filename or self.fileName)

	def saveNew(self, filename: str | None = None) -> NoReturn:
		"""Save a new gimp image to a file."""

		# Save not yet implemented so for now throw
		# an except so we don't corrupt the file
		raise NotImplementedError

		# utils.save(self.encode(), filename or self.fileName)

	def __str__(self) -> str:
		"""Get a textual representation of this object."""
		return self.__repr__()

	def __repr__(self) -> str:
		"""Get a textual representation of this object."""
		return (
			f"<GimpDocument fileName={self.fileName!r}, version={self.version!r}, "
			f"width={self.width}, height={self.height}, no_layers={len(self.raw_layers)} "
			f"baseColorMode={self.baseColorMode!r}, precision={self.precision!r}>"
		)

	def full_repr(self, indent: int = 0) -> str:
		"""Get a textual representation of this object."""
		attrs = [
			"fileName",
			"version",
			"width",
			"height",
			"baseColorMode",
			"precision",
		]

		ret = [
			f"{camel_to_pascal_with_spaces(attr)}: {getattr(self, attr)}"
			for attr in attrs
			if getattr(self, attr) is not None
		]
		ret.append(super().full_repr())
		if self._layerPtr:
			ret.append("Layers:")
			for layer in self.raw_layers:
				ret.append(layer.full_repr(indent=indent + 1))
		if self._channelPtr:
			ret.append("Channels:")
			for channel in self._channels:
				ret.append(channel.full_repr(indent=indent + 1))

		return repr_indent_lines(indent, ret)

	def render(self, root_group: GimpGroup) -> Image.Image:
		"""Perform the full project render over the current project.

		:return PIL.Image: The fully composited image
		"""
		arr = self._render(root_group)
		return Image.fromarray(np.uint8(np.around(arr, 0)))

	def _render(self, current_group: GimpGroup) -> np.ndarray:
		"""Perform the full project render over the current project.

		:return PIL.Image: The fully composited image
		"""

		merge_onto = pil2np(Image.new("RGBA", (self.width, self.height)))

		all_children: list[GimpLayer | GimpGroup] = current_group.children[::-1]

		for _i, child in enumerate(all_children):
			if isinstance(child, GimpGroup):
				to_merge = pil2np(Image.new("RGBA", (self.width, self.height)))
				lo = child.layer_options
				if lo and lo.visible:
					to_merge = self._render(child)
					if lo.mask:
						to_merge = applyMask(im=to_merge, mask_im=lo.mask.image, offsets=(0, 0))
					merge_onto = blendLayersArray(
						background=merge_onto,
						foreground=to_merge,
						blendType=blendModeLookup(lo.blendMode),
						opacity=lo.opacity,
						offsets=(0, 0),
					)

			else:
				to_merge = pil2np(Image.new("RGBA", (self.width, self.height)))
				if child.visible:
					to_merge = pil2np(child.image)
					if child.mask:
						to_merge = applyMask(
							im=to_merge,
							mask_im=child.mask.image,
							offsets=(child.mask.xOffset, child.mask.yOffset),
						)
					merge_onto = blendLayersArray(
						background=merge_onto,
						foreground=to_merge,
						blendType=blendModeLookup(child.blendMode),
						opacity=child.opacity,
						offsets=(child.xOffset, child.yOffset),
					)

		return merge_onto


blendLookup = {
	GimpBlendMode.NORMAL_LEGACY: BlendMode.NORMAL,
	GimpBlendMode.MULTIPLY_LEGACY: BlendMode.MULTIPLY,
	GimpBlendMode.SCREEN_LEGACY: BlendMode.SCREEN,
	GimpBlendMode.OLD_BROKEN_OVERLAY: BlendMode.OVERLAY,
	GimpBlendMode.DIFFERENCE_LEGACY: BlendMode.DIFFERENCE,
	GimpBlendMode.ADDITION_LEGACY: BlendMode.ADDITIVE,
	GimpBlendMode.SUBTRACT_LEGACY: BlendMode.NEGATION,
	GimpBlendMode.DARKEN_ONLY_LEGACY: BlendMode.DARKEN,
	GimpBlendMode.LIGHTEN_ONLY_LEGACY: BlendMode.LIGHTEN,
	GimpBlendMode.HUE_HSV_LEGACY: BlendMode.HUE,
	GimpBlendMode.SATURATION_HSV_LEGACY: BlendMode.SATURATION,
	GimpBlendMode.COLOR_HSL_LEGACY: BlendMode.COLOUR,
	GimpBlendMode.VALUE_HSV_LEGACY: BlendMode.LUMINOSITY,
	GimpBlendMode.DIVIDE_LEGACY: BlendMode.DIVIDE,
	GimpBlendMode.DODGE_LEGACY: BlendMode.COLOURDODGE,
	GimpBlendMode.BURN_LEGACY: BlendMode.COLOURBURN,
	GimpBlendMode.HARD_LIGHT_LEGACY: BlendMode.HARDLIGHT,
	GimpBlendMode.SOFT_LIGHT_LEGACY: BlendMode.SOFTLIGHT,
	GimpBlendMode.GRAIN_EXTRACT_LEGACY: BlendMode.GRAINEXTRACT,
	GimpBlendMode.GRAIN_MERGE_LEGACY: BlendMode.GRAINMERGE,
	GimpBlendMode.OVERLAY: BlendMode.OVERLAY,
	GimpBlendMode.HUE_LCH: BlendMode.HUE,
	GimpBlendMode.CHROMA_LCH: BlendMode.SATURATION,
	GimpBlendMode.COLOR_LCH: BlendMode.COLOUR,
	GimpBlendMode.LIGHTNESS_LCH: BlendMode.LUMINOSITY,
	GimpBlendMode.NORMAL: BlendMode.NORMAL,
	GimpBlendMode.MULTIPLY: BlendMode.MULTIPLY,
	GimpBlendMode.SCREEN: BlendMode.SCREEN,
	GimpBlendMode.DIFFERENCE: BlendMode.DIFFERENCE,
	GimpBlendMode.ADDITION: BlendMode.ADDITIVE,
	GimpBlendMode.SUBSTRACT: BlendMode.NEGATION,
	GimpBlendMode.DARKEN_ONLY: BlendMode.DARKEN,
	GimpBlendMode.LIGHTEN_ONLY: BlendMode.LIGHTEN,
	GimpBlendMode.HUE_HSV: BlendMode.HUE,
	GimpBlendMode.SATURATION_HSV: BlendMode.SATURATION,
	GimpBlendMode.COLOR_HSL: BlendMode.COLOUR,
	GimpBlendMode.VALUE_HSV: BlendMode.LUMINOSITY,
	GimpBlendMode.DIVIDE: BlendMode.DIVIDE,
	GimpBlendMode.DODGE: BlendMode.COLOURDODGE,
	GimpBlendMode.BURN: BlendMode.COLOURBURN,
	GimpBlendMode.HARD_LIGHT: BlendMode.HARDLIGHT,
	GimpBlendMode.SOFT_LIGHT: BlendMode.SOFTLIGHT,
	GimpBlendMode.GRAIN_EXTRACT: BlendMode.GRAINEXTRACT,
	GimpBlendMode.GRAIN_MERGE: BlendMode.GRAINMERGE,
	GimpBlendMode.VIVID_LIGHT: BlendMode.VIVIDLIGHT,
	GimpBlendMode.PIN_LIGHT: BlendMode.PINLIGHT,
	GimpBlendMode.EXCLUSION: BlendMode.EXCLUSION,
}


def pil2np(image: Image.Image | None) -> np.ndarray:
	if image is None:
		return np.zeros((0, 0, 4), dtype=np.float64)
	return np.array(image.convert("RGBA"))


def make_thumbnail(image: Image.Image) -> None:
	# warning: in place modification
	if image.width > 256 or image.height > 256:
		image.thumbnail((256, 256))


def blendModeLookup(blend_type: GimpBlendMode) -> BlendMode:
	"""Look up the blend mode from the lookup table."""
	return blendLookup.get(blend_type, BlendMode.NORMAL)


def applyMask(
	im: np.ndarray,  # RGBA image as NumPy array
	mask_im: Image.Image | None,  # Grayscale Pillow image
	offsets: tuple[int, int] = (0, 0),
) -> np.ndarray:
	"""Apply a grayscale Pillow mask to an RGBA NumPy image.

	- Black areas in the mask (0) make corresponding image areas transparent.
	- White areas (255) keep the image unchanged.
	- Gray areas (0-255) result in partial transparency.
	"""

	if mask_im is None:
		return im

	# Ensure the mask is in grayscale
	mask_im = mask_im.convert("L")

	# Convert Pillow mask to NumPy array and normalize
	mask = np.array(mask_im, dtype=np.float64) / 255.0

	# Apply offsets
	if offsets[0] > 0:  # Shift right
		mask = np.hstack((np.zeros((mask.shape[0], offsets[0]), dtype=np.float64), mask))
	elif offsets[0] < 0:  # Shift left
		mask = mask[:, -offsets[0] :] if -offsets[0] < mask.shape[1] else np.zeros_like(mask)

	if offsets[1] > 0:  # Shift down
		mask = np.vstack((np.zeros((offsets[1], mask.shape[1]), dtype=np.float64), mask))
	elif offsets[1] < 0:  # Shift up
		mask = mask[-offsets[1] :, :] if -offsets[1] < mask.shape[0] else np.zeros_like(mask)

	# Resize mask to match image dimensions
	mask = mask[: im.shape[0], : im.shape[1]]  # Crop if too large
	if mask.shape[0] < im.shape[0] or mask.shape[1] < im.shape[1]:
		padded_mask = np.zeros((im.shape[0], im.shape[1]), dtype=np.float64)
		padded_mask[: mask.shape[0], : mask.shape[1]] = mask
		mask = padded_mask

	# Expand mask to match image dimensions
	mask = np.expand_dims(mask, axis=-1)

	# Normalize the image
	im = im / 255.0

	# Apply mask to RGB and Alpha channels
	out_rgb = im[..., :3] * mask  # Fade RGB using mask
	out_alpha = im[..., 3] * mask[..., 0]  # Adjust alpha using mask

	# Reassemble and convert back to 0-255 range
	result = np.dstack((out_rgb, out_alpha)) * 255.0
	return np.nan_to_num(result, copy=False)
