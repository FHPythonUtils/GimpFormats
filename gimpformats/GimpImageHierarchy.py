"""
Gets packed pixels from a gimp image

NOTE: This was originally designed to be a hierarchy, like
	an image pyramid, through in practice they only use the
	top level of the pyramid (64x64) and ignore the rest.
"""

from .GimpIOBase import IO, GimpIOBase
from .GimpImageLevel import GimpImageLevel


class GimpImageHierarchy(GimpIOBase):
	"""
	Gets packed pixels from a gimp image

	NOTE: This was originally designed to be a hierarchy, like
		an image pyramid, through in practice they only use the
		top level of the pyramid (64x64) and ignore the rest.
	"""
	def __init__(self, parent, image=None):
		GimpIOBase.__init__(self, parent)
		self.width = 0
		self.height = 0
		self.bpp = 0 # Number of bytes per pixel given
		self._levelPtrs = []
		self._levels = None
		self._data = None
		if image is not None: # NOTE: can override earlier parameters
			self.image = image

	def decode_(self, data, index=0):
		"""
		decode a byte buffer

		:param data: data buffer to decode
		:param index: index within the buffer to start at
		"""
		if not data:
			raise Exception('No data!')
		io = IO(data, index)
		#print 'Decoding channel at',index
		self.width = io.u32
		self.height = io.u32
		self.bpp = io.u32
		if self.bpp < 1 or self.bpp > 4:
			msg = """'Unexpected bytes-per-pixel for image data (""" + str(self.bpp) + """).
				Probably means file corruption."""
			raise Exception(msg)
		while True:
			ptr = self._pointerDecode_(io)
			if ptr == 0:
				break
			self._levelPtrs.append(ptr)
		if self._levelPtrs: # remove "dummy" level pointers
			self._levelPtrs = [self._levelPtrs[0]]
		self._data = data
		return io.index

	def encode_(self):
		"""
		encode this object to a byte buffer
		"""
		dataIO = IO()
		io = IO()
		io.u32 = self.width
		io.u32 = self.height
		io.u32 = self.bpp
		dataIndex = io.index + GimpIOBase._POINTER_SIZE_ * (len(self.levels) + 1)
		for level in self.levels:
			io.addBytes(self._pointerEncode_(dataIndex + dataIO.index)) # TODO: This may be incorrect
			dataIO.addBytes(level.encode_())
		io.addBytes(self._pointerEncode_(0))
		io.addBytes(dataIO.data)
		return io.data

	@property
	def levels(self):
		"""
		Get the levels within this hierarchy

		Presently hierarchy is not really used by gimp,
		so this returns an array of one item
		"""
		if self._levels is None:
			for ptr in self._levelPtrs:
				l = GimpImageLevel(self)
				l.decode_(self._data, ptr)
				self._levels = [l]
		return self._levels

	@property
	def image(self):
		"""
		get a final, compiled image
		"""
		if not self.levels:
			return None
		return self.levels[0].image

	@image.setter
	def image(self, image):
		"""
		set the image
		"""
		self.width = image.width
		self.height = image.height
		if image.mode not in ['L', 'LA', 'RGB', 'RGBA']:
			raise NotImplementedError('Unsupported PIL image type')
		self.bpp = len(image.mode)
		self._levelPtrs = None
		#self._levels = [GimpImageLevel(self, image)]

	def __repr__(self, indent=''):
		"""
		Get a textual representation of this object
		"""
		ret = []
		ret.append('Size: ' + str(self.width) + ' x ' + str(self.height))
		ret.append('Bytes Per Pixel: ' + str(self.bpp))
		return indent + (('\n' + indent).join(ret))