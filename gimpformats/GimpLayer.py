"""
Represents a single layer in a gimp image
"""
from __future__ import annotations
from typing import Optional
from PIL.Image import Image
from binaryiotools import IO
from .GimpIOBase import GimpIOBase
from .GimpImageHierarchy import GimpImageHierarchy
from .GimpChannel import GimpChannel

class GimpLayer(GimpIOBase):
	"""
	Represents a single layer in a gimp image
	"""

	COLOR_MODES = [
	'RGB color without alpha', 'RGB color with alpha', 'Grayscale without alpha',
	'Grayscale with alpha', 'Indexed without alpha', 'Indexed with alpha']
	PIL_MODE_TO_LAYER_MODE = {'L': 2, 'LA': 3, 'RGB': 0, 'RGBA': 1}

	def __init__(self, parent, name: Optional[str]=None, image: Optional[Image]=None):
		GimpIOBase.__init__(self, parent)
		self.width = 0
		self.height = 0
		self.colorMode = 0
		self.name = name
		self._imageHierarchy = None
		self._imageHierarchyPtr = None
		self._mask = None
		self._maskPtr = None
		self._data = None
		if image is not None:
			self.image = image # done last as it resets some of the above defaults

	def decode(self, data: bytearray, index: int=0):
		"""
		decode a byte buffer

		Steps:
		Create a new IO buffer (array of binary values)
		Grab attributes as outlined in the spec
		List of properties
		Get the image hierarchy and mask pointers
		Return the offset

		:param data: data buffer to decode
		:param index: index within the buffer to start at
		"""
		# Create a new IO buffer (array of binary values)
		ioBuf = IO(data, index)
		# Grab attributes as outlined in the spec
		self.width = ioBuf.u32
		self.height = ioBuf.u32
		self.colorMode = ioBuf.u32 # one of self.COLOR_MODES
		self.name = ioBuf.sz754
		# List of properties
		self._propertiesDecode(ioBuf)
		# Get the image hierarchy and mask pointers
		self._imageHierarchyPtr = self._pointerDecode(ioBuf)
		self._maskPtr = self._pointerDecode(ioBuf)
		self._mask = None
		self._data = data
		# Return the offset
		return ioBuf.index

	def encode(self):
		"""
		encode to byte array

		Steps:
		Create a new IO buffer (array of binary values)
		Set attributes as outlined in the spec
		List of properties
		Set the image hierarchy and mask pointers
		Return the data

		"""
		# Create a new IO buffer (array of binary values)
		dataAreaIO = IO()
		ioBuf = IO()
		# Set attributes as outlined in the spec
		ioBuf.u32 = self.width
		ioBuf.u32 = self.height
		ioBuf.u32 = self.colorMode
		ioBuf.sz754 = self.name
		# Layer properties
		ioBuf.addBytes(self._propertiesEncode())
		# Pointer to the image heirachy structure
		dataAreaIndex = ioBuf.index + self._POINTER_SIZE * 2
		ioBuf.addBytes(self._pointerEncode(dataAreaIndex))
		dataAreaIO.addBytes(self.imageHierarchy.encode())
		#ioBuf.addBytes(self._pointerEncode_(dataAreaIndex))
		# Pointer to the layer mask
		if self.mask is not None:
			dataAreaIO.addBytes(self.mask.encode())
		ioBuf.addBytes(self._pointerEncode(dataAreaIndex + dataAreaIO.index))
		ioBuf.addBytes(dataAreaIO)
		# Return the data
		return ioBuf.data

	@property
	def mask(self):
		"""
		Get the layer mask
		"""
		if self._mask is None and self._maskPtr is not None and self._maskPtr != 0:
			self._mask = GimpChannel(self)
			self._mask.decode(self._data, self._maskPtr)
		return self._mask

	@property
	def image(self) -> Image:
		"""
		get the layer image

		NOTE: can return None!
		"""
		if self.imageHierarchy is None:
			return None
		return self.imageHierarchy.image

	@image.setter
	def image(self, image: Image):
		"""
		set the layer image

		NOTE: resets layer width, height, and colorMode
		"""
		self.height = image.height
		self.width = image.width
		if image.mode not in self.PIL_MODE_TO_LAYER_MODE:
			raise NotImplementedError('No way of handlng PIL image mode "' + image.mode + '"')
		self.colorMode = self.PIL_MODE_TO_LAYER_MODE[image.mode]
		if not self.name and isinstance(image, str):
			# try to use a fileName as the name
			self.name = image.rsplit('\\', 1)[-1].rsplit('/', 1)[-1]
		self._imageHierarchy = GimpImageHierarchy(self)
		self._imageHierarchy.image = image

	@property
	def imageHierarchy(self) -> GimpImageHierarchy:
		"""
		Get the image hierarchy objects

		This is mainly needed for deciphering image, and therefore,
		of little use to you, the user.

		NOTE: can return None if it has been fully read into an image
		"""
		if self._imageHierarchy is None and self._imageHierarchyPtr > 0:
			self._imageHierarchy = GimpImageHierarchy(self)
			self._imageHierarchy.decode(self._data, self._imageHierarchyPtr)
		return self._imageHierarchy

	@imageHierarchy.setter
	def imageHierarchy(self, imgHierarchy):
		""" set the image hierarchy """
		self._imageHierarchy = imgHierarchy


	def _forceFullyLoaded(self):
		"""
		make sure everything is fully loaded from the file
		"""
		if self.mask is not None:
			self.mask._forceFullyLoaded()
		_ = self.image # make sure the image is loaded so we can delete the hierarchy nonsense
		#self._imageHierarchy = None
		#self._data = None

	def __repr__(self, indent=''):
		"""
		Get a textual representation of this object
		"""
		ret = []
		ret.append('Name: ' + str(self.name))
		ret.append('Size: ' + str(self.width) + ' x ' + str(self.height))
		ret.append('colorMode: ' + self.COLOR_MODES[self.colorMode])
		ret.append(GimpIOBase.__repr__(self, indent))
		m = self.mask
		if m is not None:
			ret.append('Mask:')
			ret.append(m.__repr__(indent + '\t'))
		return indent + (('\n' + indent).join(ret))
