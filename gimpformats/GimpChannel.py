"""
Represents a single channel or mask in a gimp image
"""
from __future__ import annotations
from typing import Optional
from PIL import Image

from binaryiotools import IO
from .GimpIOBase import GimpIOBase
from .GimpImageHierarchy import GimpImageHierarchy

class GimpChannel(GimpIOBase):
	"""
	Represents a single channel or mask in a gimp image
	"""
	def __init__(self, parent, name: str="", image: Optional[Image.Image]=None):
		GimpIOBase.__init__(self, parent)
		self.width = 0
		self.height = 0
		self.name = name
		self._imageHierarchy = None
		self._imageHierarchyPtr = None
		if image is not None: # this is last because image can reset values
			self.image = image
		self._data = None

	def decode(self, data: bytearray, index: int=0):
		"""
		decode a byte buffer

		:param data: data buffer to decode
		:param index: index within the buffer to start at
		"""
		ioBuf = IO(data, index)
		#print 'Decoding channel at',index
		self.width = ioBuf.u32
		self.height = ioBuf.u32
		self.name = ioBuf.sz754
		self._propertiesDecode(ioBuf)
		self._imageHierarchyPtr = self._pointerDecode(ioBuf)
		self._data = ioBuf.data
		return ioBuf.index

	def encode(self):
		"""
		encode this object to a byte buffer
		"""
		ioBuf = IO()
		ioBuf.u32 = self.width
		ioBuf.u32 = self.height
		ioBuf.sz754 = self.name
		ioBuf.addBytes(self._propertiesEncode())
		imgH = self._imageHierarchyPtr
		if imgH is None:
			imgH = 0
		ioBuf.addBytes(self._pointerEncode(imgH))
		return ioBuf.data

	@property
	def image(self) -> Optional[Image.Image]:
		"""
		get a final, compiled image
		"""
		return self.imageHierarchy.image

	@image.setter
	def image(self, image: Image.Image):
		"""
		get a final, compiled image
		"""
		self.width = image.width
		self.height = image.height
		if not self.name and isinstance(image, str):
			# try to use a fileName as the name
			self.name = image.rsplit('\\', 1)[-1].rsplit('/', 1)[-1]
		self._imageHierarchy = GimpImageHierarchy(self, image)

	def _forceFullyLoaded(self):
		"""
		make sure everything is fully loaded from the file
		"""
		_ = self.image # make sure the image is loaded so we can delete the hierarchy nonsense
		self._imageHierarchyPtr = None
		self._data = None

	@property
	def imageHierarchy(self):
		"""
		Get the image hierarchy

		This is mainly used for decoding the image, so
		not much use to you.
		"""
		if self._imageHierarchy is None:
			self._imageHierarchy = GimpImageHierarchy(self)
			self._imageHierarchy.decode(self._data, self._imageHierarchyPtr)
		return self._imageHierarchy

	def __repr__(self, indent: str='') -> str:
		"""
		Get a textual representation of this object
		"""
		ret = []
		ret.append('Name: ' + str(self.name))
		ret.append('Size: ' + str(self.width) + ' x ' + str(self.height))
		ret.append(GimpIOBase.__repr__(self, indent))
		return indent + (('\n' + indent).join(ret))
