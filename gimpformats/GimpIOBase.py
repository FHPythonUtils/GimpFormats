"""A specialized binary file base for Gimp files."""

from __future__ import annotations

import struct
from typing import Any

from aenum import Enum

from gimpformats.binaryiotools import IO
from gimpformats.enums import (
	AllProps,
	CompositeMode,
	CompositeSpace,
	CompressionMode,
	GimpBlendMode,
	TagColor,
	Units,
)
from gimpformats.GimpParasites import GimpParasite
from gimpformats.GimpVectors import GimpVector
from gimpformats.utils import repr_indent_lines


def _prop_cmp(val: int, prop: AllProps | list[AllProps]) -> bool:
	if isinstance(prop, list):
		return any(_prop_cmp(val, p) for p in prop)

	return val == prop.value


def camel_to_pascal_with_spaces(val: str) -> str:
	text = "".join([f" {char}" if char.isupper() else char for char in val])
	return text[0].upper() + text[1:]


class GimpIOBase:
	def __init__(self, parent: Any = None) -> None:
		self.parent = parent
		self.parasites: list[GimpParasite] = []
		self.guidelines: list[tuple[bool, int]] = []
		self.itemPath: list[int] | None = None
		self.vectors: list[GimpVector] = []
		self.colorMap: list[tuple[int, int, int]] = []
		self.userUnits: GimpUserUnits | None = None
		self.samplePoints: list[tuple[int, int]] = []
		self.selected: bool = False
		self.isSelection: bool = False
		self.selectionAttachedTo: int | None = None
		self.blendMode: GimpBlendMode = GimpBlendMode.ADDITION
		self.visible: bool = False
		self.isLinked: bool = False
		self.lockAlpha: bool = False
		self.applyMask: bool = False
		self.editingMask: bool = False
		self.showMask: bool = False
		self.showMasked: bool = False
		self.xOffset: int = 0
		self.yOffset: int = 0
		self.compression: CompressionMode = CompressionMode.None_Compression
		self.horizontalResolution = None
		self.verticalResolution = None
		self.uniqueId = None
		self.units: Units = Units.Inches
		self.textLayerFlags = None
		self.locked = None
		self.isGroup = None
		self.groupItemFlags: int = 0
		self.positionLocked: bool = False
		self.visibilityLocked: bool = False
		self.opacity: float = 1.0
		self.colorTag: TagColor = TagColor.Blue
		self.compositeMode: CompositeMode = CompositeMode.Union
		self.compositeSpace: CompositeSpace = CompositeSpace.RGB_linear
		self.blendSpace = None
		self.color = None
		self.vectorsVersion: int = 0
		self.activeVectorIndex: int = 0
		self.paths = []

	@property
	def pointerSize(self) -> int:
		"""Determine the size of the "pointer" datatype based on the document version.

		NOTE: prior to version 11, it was 32-bit,
			since then it is 64-bit, thus supporting
			larger image files
		"""
		if self.doc.version >= 11:
			return 64
		return 32

	def _pointerDecode(self, ioBuf: IO) -> int:
		if self.pointerSize == 64:
			return ioBuf.u64
		return ioBuf.u32

	def _pointerEncode(self, ptr: int, ioBuf: IO | None = None) -> bytearray:
		if ioBuf is None:
			ioBuf = IO()
		if self.pointerSize == 64:
			ioBuf.u64 = ptr
		else:
			ioBuf.u32 = ptr
		return ioBuf.data

	@property
	def doc(self) -> GimpIOBase:
		item = self
		while item.parent != item:
			item = item.parent
		return item

	@property
	def root(self) -> GimpIOBase:
		"""Get the root of the file object tree (Which is the same as self.doc)."""
		return self.doc

	@property
	def tattoo(self) -> Any | None:
		"""Gimp nomenclature for the item's unique id."""
		return self.uniqueId

	@tattoo.setter
	def tattoo(self, tattoo: Any | None) -> None:
		"""Gimp nomenclature for the item's unique id."""
		self.uniqueId = tattoo

	def _parasitesDecode(self, data: bytearray) -> int:
		"""Decode list of parasites."""
		index: int = 0
		self.parasites = []  # reset
		while index < len(data):
			parasite = GimpParasite()
			index = parasite.decode(data, index)
			self.parasites.append(parasite)
		return index

	def _parasitesEncode(self) -> bytearray:
		"""Encode list of parasites."""
		ioBuf = IO()
		for parasite in self.parasites:
			ioBuf.addbytearray(parasite.encode())
		return ioBuf.data

	def _guidelinesDecode(self, data: bytearray) -> None:
		"""Decode guidelines."""
		index: int = 0
		while index < len(data):
			position = struct.unpack(">I", data[index : index + 4])[0]
			index += 4
			isVertical = struct.unpack(">c", data[index : index + 1])[0] == 2
			index += 1
			self.guidelines.append((isVertical, position))

	def _itemPathDecode(self, data: bytearray) -> None:
		"""Decode item path."""
		index: int = 0
		path = []
		while index < len(data):
			pathElem = struct.unpack(">I", data[index : index + 4])[0]
			index += 4
			path.append(pathElem)
		self.itemPath = path

	def _vectorsDecode(self, data: bytearray) -> None:
		"""Decode vectors."""
		index: int = 0
		self.vectorsVersion = struct.unpack(">I", data[index : index + 4])[0]
		index += 4
		self.activeVectorIndex = struct.unpack(">I", data[index : index + 4])[0]
		index += 4
		numPaths = struct.unpack(">I", data[index : index + 4])[0]
		index += 4
		for _ in range(numPaths):
			gimpV = GimpVector(self)
			gimpV.decode(data)
			self.vectors.append(gimpV)

	@property
	def activeVector(self) -> GimpVector:
		"""Get the vector that is currently active."""
		return self.vectors[self.activeVectorIndex]

	@property
	def expanded(self) -> bool:
		"""Is the group layer expanded."""
		return self.groupItemFlags & 0x00000001 > 0

	@expanded.setter
	def expanded(self, expanded: bool) -> None:
		"""Is the group layer expanded."""
		if expanded:
			self.groupItemFlags |= 0x00000001
		else:
			self.groupItemFlags &= ~0x00000001

	def _colormapDecode(self, data: bytearray | IO, index: int = 0) -> None:
		"""_colormapDecode_.

		:param data: can be bytearray or an IO object

		decode colormap/palette
		"""
		ioObj = None
		if isinstance(data, IO):
			ioObj = data
			index = data.index
			data = data.data
		_ = struct.unpack(">I", data[0:4])[0]  # number of colors
		index += 4
		colors = []
		while index < len(data):
			red = data[index]
			index += 1
			green = data[index]
			index += 1
			blue = data[index]
			index += 1
			colors.append((red, green, blue))
		self.colorMap = colors
		if ioObj is not None:
			ioObj.index = index

	def _userUnitsDecode(self, data: bytearray) -> None:
		"""Decode a set of user-defined measurement units."""
		userUnits = GimpUserUnits()
		userUnits.decode(data)
		self.userUnits = userUnits

	def _samplePointsDecode(self, data: bytearray) -> None:
		"""Decode a series of points."""
		index: int = 0
		samplePoints = []
		while index < len(data):
			x = struct.unpack(">I", data[index : index + 4])[0]
			index += 4
			y = struct.unpack(">I", data[index : index + 4])[0]
			index += 4
			samplePoints.append((x, y))
		self.samplePoints = samplePoints

	def _propertyDecode(self, prop: int, data: bytearray) -> int:
		"""Decode a single property."""
		ioBuf = IO(data, boolSize=32)
		if _prop_cmp(prop, AllProps.PROP_COLORMAP):
			self._colormapDecode(ioBuf)
		elif _prop_cmp(prop, [AllProps.PROP_ACTIVE_LAYER, AllProps.PROP_ACTIVE_CHANNEL]):
			self.selected = True
		elif _prop_cmp(prop, AllProps.PROP_SELECTION):
			self.isSelection = True
		elif _prop_cmp(prop, AllProps.PROP_FLOATING_SELECTION):
			self.selectionAttachedTo = ioBuf.u32
		elif _prop_cmp(prop, AllProps.PROP_OPACITY):
			self.opacity = ioBuf.u32
		elif _prop_cmp(prop, AllProps.PROP_MODE):
			self.blendMode = list(GimpBlendMode)[ioBuf.u32]
		elif _prop_cmp(prop, AllProps.PROP_VISIBLE):
			self.visible = ioBuf.boolean
		elif _prop_cmp(prop, AllProps.PROP_LINKED):
			self.isLinked = ioBuf.boolean
		elif _prop_cmp(prop, AllProps.PROP_LOCK_ALPHA):
			self.lockAlpha = ioBuf.boolean
		elif _prop_cmp(prop, AllProps.PROP_APPLY_MASK):
			self.applyMask = ioBuf.boolean
		elif _prop_cmp(prop, AllProps.PROP_EDIT_MASK):
			self.editingMask = ioBuf.boolean
		elif _prop_cmp(prop, AllProps.PROP_SHOW_MASK):
			self.showMask = ioBuf.boolean
		elif _prop_cmp(prop, AllProps.PROP_SHOW_MASKED):
			self.showMasked = ioBuf.boolean
		elif _prop_cmp(prop, AllProps.PROP_OFFSETS):
			self.xOffset = ioBuf.i32
			self.yOffset = ioBuf.i32
		elif _prop_cmp(prop, AllProps.PROP_COLOR):
			red = ioBuf.byte
			green = ioBuf.byte
			blue = ioBuf.byte
			self.color = [red, green, blue]
		elif _prop_cmp(prop, AllProps.PROP_COMPRESSION):
			self.compression = list(CompressionMode)[int(ioBuf.byte)]
		elif _prop_cmp(prop, AllProps.PROP_GUIDES):
			self._guidelinesDecode(data)
		elif _prop_cmp(prop, AllProps.PROP_RESOLUTION):
			self.horizontalResolution = ioBuf.float32
			self.verticalResolution = ioBuf.float32
		elif _prop_cmp(prop, AllProps.PROP_TATTOO):
			self.uniqueId = data.hex()
		elif _prop_cmp(prop, AllProps.PROP_PARASITES):
			self._parasitesDecode(data)
		elif _prop_cmp(prop, AllProps.PROP_UNIT):
			self.units = list(Units)[ioBuf.u32]
		elif _prop_cmp(prop, AllProps.PROP_PATHS):
			_numPaths = ioBuf.u32
			"""
			for _ in range(numPaths):
				nRead, path = self._pathDecode_(data[index:])
				self.paths.append(path)
				index += nRead
			"""
		elif _prop_cmp(prop, AllProps.PROP_USER_UNIT):
			self._userUnitsDecode(data)
		elif _prop_cmp(prop, AllProps.PROP_VECTORS):
			pass
			# self._vectorsDecode_(data)
		elif _prop_cmp(prop, AllProps.PROP_TEXT_LAYER_FLAGS):
			if isinstance(data, bytearray):
				self.textLayerFlags = int.from_bytes(data, byteorder="big")
			else:
				self.textLayerFlags = int(data)
		elif _prop_cmp(prop, AllProps.PROP_OLD_SAMPLE_POINTS):
			msg = "ERR: old sample points structure not supported"
			raise RuntimeError(msg)
		elif _prop_cmp(prop, AllProps.PROP_LOCK_CONTENT):
			self.locked = ioBuf.boolean
		elif _prop_cmp(prop, AllProps.PROP_GROUP_ITEM):
			self.isGroup = True
		elif _prop_cmp(prop, AllProps.PROP_ITEM_PATH):
			self._itemPathDecode(data)
		elif _prop_cmp(prop, AllProps.PROP_GROUP_ITEM_FLAGS):
			self.groupItemFlags = ioBuf.u32
		elif _prop_cmp(prop, AllProps.PROP_LOCK_POSITION):
			self.positionLocked = ioBuf.boolean
		elif _prop_cmp(prop, AllProps.PROP_LOCK_VISIBILITY):
			self.visibilityLocked = ioBuf.boolean
		elif _prop_cmp(prop, AllProps.PROP_FLOAT_OPACITY):
			self.opacity = ioBuf.float32
		elif _prop_cmp(prop, AllProps.PROP_COLOR_TAG):
			self.colorTag = list(TagColor)[ioBuf.u32]
		elif _prop_cmp(prop, AllProps.PROP_COMPOSITE_MODE):
			self.compositeMode = list(CompositeMode)[abs(ioBuf.i32) - 1]
		elif _prop_cmp(prop, AllProps.PROP_COMPOSITE_SPACE):
			self.compositeSpace = list(CompositeSpace)[abs(ioBuf.i32) - 1]
		elif _prop_cmp(prop, AllProps.PROP_BLEND_SPACE):
			self.blendSpace = ioBuf.u32
		elif _prop_cmp(prop, AllProps.PROP_FLOAT_COLOR):
			red = ioBuf.float32
			green = ioBuf.float32
			blue = ioBuf.float32
			self.color = [red, green, blue]
		elif _prop_cmp(prop, AllProps.PROP_SAMPLE_POINTS):
			self._samplePointsDecode(data)
		else:
			msg = f"Unknown property id {prop}"
			raise RuntimeError(msg)
		return ioBuf.index

	def _propertyEncode(self, prop: int) -> bytearray:
		"""Encode a single property."""
		ioBuf = IO(boolSize=32)
		if _prop_cmp(prop, AllProps.PROP_COLORMAP):
			# uint32  n        Number of colors in the color map should be <256
			# ,------------    Repeat n times
			# | byte  r        Red component of a color map color
			# | byte  g        Green component of a color map color
			# | byte  b        Blue component of a color map color
			if self.colorMap is not None and 0 < len(self.colorMap) < 256:
				ioBuf.u32 = len(self.colorMap)
				for cm in self.colorMap:
					ioBuf.u32 = cm[0]
					ioBuf.u32 = cm[1]
					ioBuf.u32 = cm[2]
		elif _prop_cmp(
			prop, [AllProps.PROP_ACTIVE_LAYER, AllProps.PROP_ACTIVE_CHANNEL]
		) or _prop_cmp(prop, AllProps.PROP_SELECTION):
			# Has no payload
			pass

		elif _prop_cmp(prop, AllProps.PROP_FLOATING_SELECTION):
			# pointer   ptr    Pointer to the layer or channel the floating selection is
			#        attached to
			if self.selectionAttachedTo is not None:
				ioBuf.u32 = self.selectionAttachedTo

		elif _prop_cmp(prop, AllProps.PROP_OPACITY):
			# uint32  opacity    Opacity on a scale from 0 ,fully transparent, to
			# 	 255 ,fully opaque,
			if self.opacity is not None and not isinstance(self.opacity, float):
				ioBuf.u32 = self.opacity

		elif _prop_cmp(prop, AllProps.PROP_MODE):
			if self.blendMode is not None:
				ioBuf.u32 = list(GimpBlendMode).index(self.blendMode)

		elif _prop_cmp(prop, AllProps.PROP_VISIBLE):
			# uint32  visible    1 if the layer/channel is visible; 0 if not
			ioBuf.u32 = 1 if self.visible else 0

		elif _prop_cmp(prop, AllProps.PROP_LINKED):
			# uint32  linked     1 if the layer is linked; 0 if not
			ioBuf.u32 = 1 if self.isLinked else 0

		elif _prop_cmp(prop, AllProps.PROP_LOCK_ALPHA):
			# uint32  lock_alpha   1 if alpha is locked; 0 if not
			ioBuf.u32 = 1 if self.lockAlpha else 0

		elif _prop_cmp(prop, AllProps.PROP_APPLY_MASK):
			# uint32  apply    1 if the layer mask should be applied, 0 if not
			ioBuf.u32 = 1 if self.applyMask else 0

		elif _prop_cmp(prop, AllProps.PROP_EDIT_MASK):
			if self.editingMask is not None and self.editingMask:
				ioBuf.boolean = self.editingMask
		elif _prop_cmp(prop, AllProps.PROP_SHOW_MASK):
			if self.showMask is not None and self.showMask:
				ioBuf.boolean = self.showMask
		elif _prop_cmp(prop, AllProps.PROP_SHOW_MASKED):
			if self.showMasked is not None:
				ioBuf.boolean = self.showMasked
		elif _prop_cmp(prop, AllProps.PROP_OFFSETS):
			if self.xOffset is not None and self.yOffset is not None:
				ioBuf.i32 = self.xOffset
				ioBuf.i32 = self.yOffset
		elif _prop_cmp(prop, AllProps.PROP_COLOR):
			if (
				self.color is not None
				and not isinstance(self.color[0], float)
				and not isinstance(self.color[1], float)
				and not isinstance(self.color[2], float)
			):
				ioBuf.byte = self.color[0]
				ioBuf.byte = self.color[1]
				ioBuf.byte = self.color[2]
		elif _prop_cmp(prop, AllProps.PROP_COMPRESSION):
			if self.compression is not None:
				ioBuf.byte = list(CompressionMode).index(self.compression)
		elif _prop_cmp(prop, AllProps.PROP_GUIDES):
			if self.guidelines is not None and self.guidelines:
				pass

				# ioBuf.addbytearray(self._guidelinesEncode())
		elif _prop_cmp(prop, AllProps.PROP_RESOLUTION):
			if self.horizontalResolution is not None and self.verticalResolution is not None:
				ioBuf.u32 = int(self.horizontalResolution)
				ioBuf.i32 = int(self.verticalResolution)
		elif _prop_cmp(prop, AllProps.PROP_TATTOO):
			if self.uniqueId is not None:
				ioBuf.u32 = int(self.uniqueId, 16)
		elif _prop_cmp(prop, AllProps.PROP_PARASITES):
			if self.parasites is not None and self.parasites:
				ioBuf.addbytearray(self._parasitesEncode())
		elif _prop_cmp(prop, AllProps.PROP_UNIT):
			if self.units is not None:
				ioBuf.u32 = list(Units).index(self.units)
		elif _prop_cmp(prop, AllProps.PROP_PATHS):
			if self.paths is not None and self.paths:
				pass

				# ioBuf.u32 = len(self.paths)
				# for path in self.paths:
				# 	ioBuf.append(self._pathEncode_(path))
		elif _prop_cmp(prop, AllProps.PROP_USER_UNIT):
			if self.userUnits is not None:
				pass

				# ioBuf.addbytearray(self._userUnitsEncode_())
		elif _prop_cmp(prop, AllProps.PROP_VECTORS):
			if self.vectors is not None and self.vectors:
				pass

				# ioBuf.addbytearray(self._vectorsEncode_())
		elif _prop_cmp(prop, AllProps.PROP_TEXT_LAYER_FLAGS):
			if self.textLayerFlags is not None:
				ioBuf.u32 = self.textLayerFlags
		elif _prop_cmp(prop, AllProps.PROP_OLD_SAMPLE_POINTS):
			pass
		elif _prop_cmp(prop, AllProps.PROP_LOCK_CONTENT):
			if self.locked is not None and self.locked:
				ioBuf.boolean = self.locked
		elif _prop_cmp(prop, AllProps.PROP_GROUP_ITEM):
			# if self.isGroup is not None and self.isGroup:
			pass

		elif _prop_cmp(prop, AllProps.PROP_ITEM_PATH):
			if self.itemPath is not None:
				pass

				# ioBuf.addbytearray(self._itemPathEncode_())
		elif _prop_cmp(prop, AllProps.PROP_GROUP_ITEM_FLAGS):
			if self.groupItemFlags is not None:
				ioBuf.u32 = self.groupItemFlags
		elif _prop_cmp(prop, AllProps.PROP_LOCK_POSITION):
			if self.positionLocked is not None and self.positionLocked:
				ioBuf.boolean = self.positionLocked
		elif _prop_cmp(prop, AllProps.PROP_LOCK_VISIBILITY):
			if self.visibilityLocked is not None and self.visibilityLocked:
				ioBuf.boolean = self.visibilityLocked
		elif _prop_cmp(prop, AllProps.PROP_FLOAT_OPACITY):
			if self.opacity is not None and isinstance(self.opacity, float):
				ioBuf.float32 = self.opacity
		elif _prop_cmp(prop, AllProps.PROP_COLOR_TAG):
			if self.colorTag is not None:
				ioBuf.u32 = list(TagColor).index(self.colorTag)
		elif _prop_cmp(prop, AllProps.PROP_COMPOSITE_MODE):
			if self.compositeMode is not None:
				ioBuf.i32 = list(CompositeMode).index(self.compositeMode) + 1
		elif _prop_cmp(prop, AllProps.PROP_COMPOSITE_SPACE):
			if self.compositeSpace is not None:
				ioBuf.i32 = list(CompositeSpace).index(self.compositeSpace) + 1
		elif _prop_cmp(prop, AllProps.PROP_BLEND_SPACE):
			if self.blendSpace is not None:
				ioBuf.u32 = self.blendSpace
		elif _prop_cmp(prop, AllProps.PROP_FLOAT_COLOR):
			if (
				self.color is not None
				and isinstance(self.color[0], float)
				and isinstance(self.color[1], float)
				and isinstance(self.color[2], float)
			):
				ioBuf.float32 = self.color[0]
				ioBuf.float32 = self.color[1]
				ioBuf.float32 = self.color[2]
		elif _prop_cmp(prop, AllProps.PROP_SAMPLE_POINTS):
			if self.samplePoints is not None and self.samplePoints:
				pass
				# ioBuf.u32 = AllProps.PROP_SAMPLE_POINTS
				# self.addbytearray(self._samplePointsEncode_())
		else:
			msg = f"Unknown property id {prop}"
			raise RuntimeError(msg)
		return ioBuf.data

	def _propertiesDecode(self, ioBuf: IO) -> int:
		"""Decode a list of properties."""
		while True:
			try:
				prop = ioBuf.u32
				dataLength = ioBuf.u32
			except struct.error:  # end of data, so that's that.
				break
			if prop == 0:
				break
			propData = ioBuf.getbytearray(dataLength)
			self._propertyDecode(prop, propData)
		return ioBuf.index

	def _propertiesEncode(self, enum: Enum = AllProps) -> bytearray:
		"""Encode a list of properties.

		uint32  prop_type   	Type identification
		uint32  len(payload)    size of payload
		bytes[] payload

		"""
		ioBuf = IO()
		for prop_type in [x.value for x in enum]:
			encodedProp = self._propertyEncode(prop_type) if prop_type != 0 else b""

			if len(encodedProp) > 0:
				ioBuf.u32 = prop_type
				ioBuf.u32 = len(encodedProp)
				ioBuf.addbytearray(encodedProp)

		# Some props are not in the form specified in the docstring so deal with these separately
		return ioBuf.data

	def __str__(self) -> str:
		"""Get a textual representation of this object."""
		return self.__repr__()

	def __repr__(self) -> str:
		"""Get a textual representation of this object."""
		return (
			f"<GimpIOBase "
			f"uniqueId={self.uniqueId!r}, itemPath={self.itemPath!r}, "
			f"visible={self.visible}, opacity={self.opacity:.2f}, blendMode={self.blendMode}, "
			f"xOffset={self.xOffset}, yOffset={self.yOffset}, positionLocked={self.positionLocked}, "
			f"isGroup={self.isGroup}, groupItemFlags={self.groupItemFlags}, "
			f"locked={self.locked}, lockAlpha={self.lockAlpha}, editingMask={self.editingMask}>"
		)

	def full_repr(self, indent: int = 0) -> str:
		"""Get a textual representation of this object."""
		attrs = [
			"userUnits",
			"selected",
			"isSelection",
			"selectionAttachedTo",
			"blendMode",
			"visible",
			"isLinked",
			"lockAlpha",
			"applyMask",
			"editingMask",
			"showMask",
			"showMasked",
			"xOffset",
			"yOffset",
			"compression",
			"horizontalResolution",
			"verticalResolution",
			"uniqueId",
			"units",
			"textLayerFlags",
			"locked",
			"isGroup",
			"groupItemFlags",
			"positionLocked",
			"opacity",
			"colorTag",
			"compositeMode",
			"compositeSpace",
			"blendSpace",
			"color",
			"vectorsVersion",
			"activeVectorIndex",
			"paths",
		]

		ret = [
			f"{camel_to_pascal_with_spaces(attr)}: {getattr(self, attr)}"
			for attr in attrs
			if getattr(self, attr) is not None
		]

		if self.xOffset is not None:
			ret.append(f"Offset: {self.xOffset} x {self.yOffset}")
		if self.horizontalResolution is not None:
			res = str(self.horizontalResolution) + f"ppi x {self.verticalResolution}ppi"
			ret.append(f"Resolution: {res}")
		if self.color is not None:
			ret.append(f"Color: ({self.color[0]}, {self.color[1]}, {self.color[2]})")
		if self.userUnits is not None:
			ret.append("User Units:")
			ret.append(self.userUnits.full_repr(indent=indent + 1))
		if self.parasites:
			ret.append("Parasites:")
			for item in self.parasites:
				ret.append(item.__repr__())
		if self.guidelines:
			ret.append("Guidelines:")
			for item in self.guidelines:
				ret.append(item.__repr__())
		if self.samplePoints:
			ret.append("Sample Points:")
			for item in self.samplePoints:
				ret.append(f"({item[0]},{item[1]})")
		if self.vectors:
			ret.append("Vectors:")
			for item in self.vectors:
				ret.append(item.full_repr(indent=indent + 1))
		if self.colorMap:
			ret.append("Color Map:")
			for i, color in enumerate(self.colorMap):
				ret.append(str(i) + f": ({color[0]},{color[1]},{color[2]})")
		return repr_indent_lines(indent, ret)


class GimpUserUnits:
	"""User-defined measurement units."""

	def __init__(self) -> None:
		self.factor: float = 0
		self.numDigits: int = 0
		self.id = ""
		self.symbol = ""
		self.abbrev = ""
		self.sname = ""
		self.pname = ""

	def decode(self, data: bytearray, index: int = 0) -> int:
		"""Decode a byte buffer.

		Args:
		----
			data (bytearray): data buffer to decode
			index (int, optional): index within the buffer to start at]. Defaults to 0.

		Returns:
		-------
			int: offset

		"""
		ioBuf = IO(data, index)
		self.factor = ioBuf.float32
		self.numDigits = ioBuf.u32
		self.id = ioBuf.sz754
		self.symbol = ioBuf.sz754
		self.abbrev = ioBuf.sz754
		self.sname = ioBuf.sz754
		self.pname = ioBuf.sz754
		return ioBuf.index

	def encode(self) -> bytearray:
		"""Convert this object to raw bytearray."""
		ioBuf = IO()
		ioBuf.float32 = self.factor
		ioBuf.u32 = self.numDigits
		ioBuf.sz754 = self.id
		ioBuf.sz754 = self.symbol
		ioBuf.sz754 = self.abbrev
		ioBuf.sz754 = self.sname
		ioBuf.sz754 = self.pname
		return ioBuf.data

	def __str__(self) -> str:
		"""Get a textual representation of this object."""
		return self.full_repr()

	def full_repr(self, indent: int = 0) -> str:
		"""Get a textual representation of this object."""
		ret = []
		ret.append(f"Factor: {self.factor}")
		ret.append(f"Num Digits: {self.numDigits}")
		ret.append(f"ID: {self.id}")
		ret.append(f"Symbol: {self.symbol}")
		ret.append(f"Abbreviation: {self.abbrev}")
		ret.append(f"Singular Name: {self.sname}")
		ret.append(f"Plural Name: {self.pname}")
		return repr_indent_lines(indent, ret)
