# Author: Xinshuo Weng
# email: xinshuo.weng@gmail.com
import numpy as np

import __init__
from type_check import isstring

class AbstractLayer(object):
	'''
	define an abstract layer for all type of layers
	'''
	def __init__(self, name):
		assert isstring(name), 'the name of input layer should be a string'	
		self._name = name
	
	@property
	def name(self):
		return self._name

	@name.setter
	def name(self, name):
		assert isstring(name), 'the name of a layer should be a string'

	@property
	def data(self):
 		return self._data

	@data.setter
	def data(self, data):
 		raise NotImplementedError

 	@property
	def params(self):
 		return self._params

	@params.setter
	def params(self, params):
 		raise NotImplementedError

	@property
	def paramtype(self):
 		return self._paramtype

	@paramtype.setter
	def paramtype(self, paramtype):
 		assert isstring(paramtype), 'the type of parameter should be a string'
 		assert any(paramtype is item for item in ['uint', 'single', 'double']), 'type of parameter should be one of ''uint8'' ''single'' ''double'' '
 		self._paramtype = paramtype

	@property
	def datatype(self):
 		return self._datatype

	@datatype.setter
	def datatype(self, datatype):
 		assert isstring(datatype), 'the type of data should be a string'
 		assert any(datatype is item for item in ['uint', 'single', 'double']), 'type of data should be one of ''uint8'' ''single'' ''double'' '
 		self._datatype = datatype


	@property
	def type(self):
 		raise NotImplementedError

 	def get_num_param(self):
 		raise NotImplementedError

 	def get_output_blob_shape(self, bottom_shape=None):
 		raise NotImplementedError

	def get_memory_usage_param(self):
 		if self._paramtype == 'single':
 			return self.get_num_param() * 4 	# single has 4 bytes
 		elif self._paramtype == 'double':
 			return self.get_num_param() * 8		# double has 8 bytes
 		elif self._paramtype == 'uint':
 			return self.get_num_param()			# unsigned integer has 1 byte

	def get_memory_usage(self):
		return self.get_memory_usage_param() + self.get_memory_usage_data()


class Input(AbstractLayer):
	'''
	define an input layer which contains info about the input data
	'''
	def __init__(self, name):
		super(Input, self).__init__(name)
		# assert isinstance(data, np.ndarray), 'the input data layer should contains numpy array'
		self._data = None
		self._params = None
		self._paramtype = None
		self._datatype = None
	
	@AbstractLayer.data.setter
	def data(self, data):
		assert isinstance(data, np.ndarray), 'the input data layer should contains numpy array'
		self._data = data

	@AbstractLayer.params.setter
	def params(self, params):
		assert False, 'No parameter can be set in the input layer'

	@property
	def type(self):
 		return 'Input'

 	def get_num_param(self):
 		return 0

 	def get_output_blob_shape(self):
 		return self._data.shape

class Layer(AbstractLayer):
	'''
	define necessary layer parameter and property for deep learning
	'''
	def __init__(self, name, nInputPlane, nOutputPlane, kernal_size=None, stride=None, padding=None, datatype=None, params=None, paramtype=None):
		super(Layer, self).__init__(name)
		assert type(nInputPlane) is int and nInputPlane > 0, 'number of input channel is not correct'
		assert type(nOutputPlane) is int and nOutputPlane > 0, 'number of output channel is not correct'
		assert kernal_size is None or type(kernal_size) is int or len(kernal_size) == 2, 'kernal size is not correct'
		assert stride is None or type(stride) is int or len(stride) == 2, 'stride size is not correct'
		assert padding is None or type(padding) is int or len(padding) == 2, 'padding size is not correct'
		assert params is None or isinstance(params, np.ndarray), 'parameter is not correct'

		if type(kernal_size) is not int and kernal_size is not None:
			assert all(item > 0 and type(item) is int for item in kernal_size), 'kernal size must be positive integer'
		if type(stride) is not int and stride is not None:
			assert all(stride > 0 and type(item) is int for item in stride), 'stride must be positive integer'
		if type(padding) is not int and padding is not None:
			assert all(padding >= 0 and type(item) is int for item in padding), 'padding must be non-negative integer'
		if datatype is not None:
			assert any(datatype == item for item in ['uint', 'single', 'double']), 'type of data should be one of ''uint8'' ''single'' ''double'' '
		else:
			datatype = 'single'
			print 'datatype of the layer is not defined. By default, we use single floating point to save the datas'

		if paramtype is not None:
			assert any(paramtype == item for item in ['uint', 'single', 'double']), 'type of parameter should be one of ''uint8'' ''single'' ''double'' '
		else:
			paramtype = 'single'
			print 'paramtype of the layer is not defined. By default, we use single floating point to save the parameter'

		# set horizontal and vertical parameter as the same if only one dimentional input is obtained
		if type(kernal_size) is int:
			kernal_size = (kernal_size, kernal_size)
		if type(stride) is int:
			stride = (stride, stride)
		if type(padding) is int:
			padding = (padding, padding)

		self._kernal_size = kernal_size
		self._stride = stride
		self._padding = padding
		self._nInputPlane = nInputPlane
		self._nOutputPlane = nOutputPlane
		self._datatype = datatype
		self._paramtype = paramtype
		self._data = None
		self._params = params

	@property
	def nInputPlane(self):
		return self._nInputPlane

	@property
	def nOutputPlane(self):
		return self._nOutputPlane

	@property
	def kernal_size(self):
		return self._kernal_size

	@property
	def stride(self):
		return self._stride

	@property
	def padding(self):
		return self._padding

class Convolution(Layer):
	'''
	define a 2d convolutional layer
	'''
	def __init__(self, name, nInputPlane, nOutputPlane, kernal_size, stride=None, padding=None, datatype=None, params=None, paramtype=None):
		super(Convolution, self).__init__(name, nInputPlane, nOutputPlane, kernal_size, stride, padding, datatype, params, paramtype)
		if stride is None:
			stride = (1, 1)
		if padding is None:
			padding = (0, 0)

	@AbstractLayer.data.setter
	def data(self, data):
		assert isinstance(data, np.ndarray), 'the data of convolution layer should contains numpy array'
		assert data.ndim == 4, 'the data of convolution layer should be 4-d array'
		assert data.shape(3) == self.nOutputPlane, 'last dimension of data in convolution layer is not correct'
		self._data = data

	@AbstractLayer.params.setter
	def params(self, params):
		assert isinstance(params, np.ndarray), 'the parameter of convolution layer should contains numpy array'
		assert params.ndim == 3, 'the parameter of convolution layer should be 3-d array'
		assert params.shape(0) == self.nInputPlane, 'first dimension of parameter in convolution layer is not correct'
		self._params = params

	@property
	def type(self):
 		return 'Convolution'

	def get_num_param(self):
		return self.kernal_size[0] * self.kernal_size[1] * self.nInputPlane * self.nOutputPlane

	def get_output_blob_shape(self, bottom_shape):
		assert len(bottom_shape) == 1 and len(bottom_shape[0]) == 3, 'bottom blob is not correct'
		assert False

  
class Pooling(Layer):
	'''
	define a 2d pooling layer
	'''
	def __init__(self, name, nInputPlane, nOutputPlane, kernal_size, stride=None, padding=None, datatype=None, paramtype=None):
		super(Pooling, self).__init__(name, nInputPlane, nOutputPlane, kernal_size, stride, padding, datatype, paramtype)
		if stride is None:
			stride = (1, 1)
		if padding is None:
			padding = (0, 0)

	# @AbstractLayer.data.setter
	# def data(self, data):
	# 	# assert isinstance(data, np.ndarray), 'the data of convolution layer should contains numpy array'
	# 	assert data.ndim == 4, 'the data of convolution layer should be 4-d array'
	# 	assert data.shape(3) == self.nOutputPlane, 'last dimension of data in convolution layer is not correct'
	# 	self._data = data

	# @AbstractLayer.params.setter
	# def params(self, params):
	# 	# assert isinstance(params, np.ndarray), 'the parameter of convolution layer should contains numpy array'
	# 	assert params.ndim == 3, 'the parameter of convolution layer should be 3-d array'
	# 	assert params.shape(0) == self.nInputPlane, 'first dimension of parameter in convolution layer is not correct'
	# 	self._params = params

	@property
	def type(self):
 		return 'Pooling'

	def get_num_param(self):
		return 0

	def get_output_blob_shape(self, bottom_shape):
		# assert len(bottom_shape) == 1 and len(bottom_shape[0]) == 3, 'bottom shape is not correct'
		# assert False
		pass







