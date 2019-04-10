import re
import pandas as pd
import numpy
import os

def TemperatureConverter(temperature, direction=1):
	"""
	direction 1: from fahrenheit to celsius
	direction 2: from celsius to fahrenheit
	"""


	temp = float(temperature)

	if direction == 1:
		result = (temp - 32)*5/9

	elif direction == 2:
		result = 9*temp/5 + 32

	else:
		raise ValueError('Direction is type of integer in 1 or 2')

	return round(result, 1)




def LengthConverter(num, formats = "inch2mm"):
	"""
	Convert length

	inch2mm: inch to mm
	inch2cm: inch to cm
	mm2inch: mm to inch
	cm2inch: cm to inch
	cm2mm: cm to mm
	mm2cm: mm to cm
	"""

	num = float(num)

	if formats == "inch2mm":
		out = num*25.4
	elif formats == "inch2cm":
		out = num*2.54
	elif formats == "mm2inch":
		out = num/25.4
	elif formats == "cm2inch":
		out = num/2.54
	elif formats == "cm2mm":
		out = num*10
	elif formats == "mm2cm":
		out = num/10

	return round(out, 2)


class ZipcodeConvert:

	def __init__(self, filepath):
		self.filepath = filepath

	@staticmethod
	def checkzipcode(code):
		pattern = "^[0-9]{5}$|^$"
		regex = re.compile(pattern)


		checked = True
		if not regex.search(code):
			checked = False

		return checked


	def loadcsv(self, sep=";"):
		self.df = pd.read_csv(self.filepath, sep=sep)
		return self

	def zipcode_to_coords(self, zipcode):

		zipcode = str(zipcode)

		if ZipcodeConvert.checkzipcode(zipcode):

			zipcodes = int(zipcode)
			dff = self.df[self.df['Zip'] == zipcodes]

			return float(dff['Latitude']), float(dff['Longitude'])




# def deleteMapfile(path, newfile):

# 	all_files = os.listdir(path)

# 	max_val = float(newfile.split("-")[-1])

# 	for i in all_files:

# 		if os.path.isfile(i) and i.endswith('.html'):
# 			name = i.replace('.html', '')
# 			val = float(name.split("-")[-1])
# 			if val < max_val:
# 				os.remove(os.path.join(path, i))

