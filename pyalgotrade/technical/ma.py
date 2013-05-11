# PyAlgoTrade
# 
# Copyright 2011 Gabriel Martin Becedillas Ruiz
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#   http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
.. moduleauthor:: Gabriel Martin Becedillas Ruiz <gabriel.becedillas@gmail.com>
"""

from pyalgotrade import technical

def calculate_sma(values, begin, end):
	accum = 0
	for i in xrange(begin, end):
		value = values[i]
		if value is None:
			return None
		accum += value

	ret = accum / float(end - begin)
	return ret

# This is the formula I'm using to calculate the averages based on previous ones.
# 1 2 3 4
# x x x
#   x x x
# 
# avg0 = (a + b + c) / 3
# avg1 = (b + c + d) / 3 
# 
# avg0 = avg1 + x
# (a + b + c) / 3 = (b + c + d) / 3 + x
# a/3 + b/3 + c/3 = b/3 + c/3 + d/3 + x
# a/3 = d/3 + x
# x = a/3 - d/3

# avg1 = avg0 - x 
# avg1 = avg0 + d/3 - a/3

class SMAEventWindow(technical.EventWindow):
	def __init__(self, period):
		assert(period > 0)
		technical.EventWindow.__init__(self, period)
		self.__value = None

	def onNewValue(self, dateTime, value):
		firstValue = None
		if len(self.getValues()) > 0:
			firstValue = self.getValues()[0]
			assert(firstValue != None)

		technical.EventWindow.onNewValue(self, dateTime, value)

		if value != None and len(self.getValues()) == self.getWindowSize():
			if self.__value == None:
				self.__value = calculate_sma(self.getValues(), 0, self.getWindowSize())
			else:
				self.__value = self.__value + value / float(self.getWindowSize()) - firstValue / float(self.getWindowSize())

	def getValue(self):
		return self.__value

class SMA(technical.EventBasedFilter):
	"""Simple Moving Average filter.

	:param dataSeries: The DataSeries instance being filtered.
	:type dataSeries: :class:`pyalgotrade.dataseries.DataSeries`.
	:param period: The number of values to use to calculate the SMA.
	:type period: int.
	"""
	def __init__(self, dataSeries, period):
		technical.EventBasedFilter.__init__(self, dataSeries, SMAEventWindow(period))

class EMAEventWindow(technical.EventWindow):
	def __init__(self, period):
		assert(period > 1)
		technical.EventWindow.__init__(self, period)
		self.__multiplier = (2.0 / (period + 1))
		self.__value = None

	def onNewValue(self, dateTime, value):
		technical.EventWindow.onNewValue(self, dateTime, value)

		# Formula from http://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:moving_averages
		if value != None and len(self.getValues()) == self.getWindowSize():
			if self.__value == None:
				self.__value = calculate_sma(self.getValues(), 0, len(self.getValues()))
			else:
				self.__value = (value - self.__value) * self.__multiplier + self.__value

	def getValue(self):
		return self.__value

class EMA(technical.EventBasedFilter):
	"""Exponential Moving Average filter.

	:param dataSeries: The DataSeries instance being filtered.
	:type dataSeries: :class:`pyalgotrade.dataseries.DataSeries`.
	:param period: The number of values to use to calculate the EMA. Must be an integer greater than 1.
	:type period: int.
	"""

	def __init__(self, dataSeries, period):
		technical.EventBasedFilter.__init__(self, dataSeries, EMAEventWindow(period))

class WMAEventWindow(technical.EventWindow):
	def __init__(self, weights):
		assert(len(weights) > 0)
		technical.EventWindow.__init__(self, len(weights))
		self.__weights = weights

	def getValue(self):
		ret = None
		if len(self.getValues()) == self.getWindowSize():
			accum = 0
			weightSum = 0
			for i, value in enumerate(self.getValues()):
				weight = self.__weights[i]
				accum += value * weight
				weightSum += weight
			ret = accum / float(weightSum)
		return ret

class WMA(technical.EventBasedFilter):
	"""Weighted Moving Average filter.

	:param dataSeries: The DataSeries instance being filtered.
	:type dataSeries: :class:`pyalgotrade.dataseries.DataSeries`.
	:param weights: A list of int/float with the weights.
	:type weights: list.
	"""
	def __init__(self, dataSeries, weights):
		technical.EventBasedFilter.__init__(self, dataSeries, WMAEventWindow(weights))

