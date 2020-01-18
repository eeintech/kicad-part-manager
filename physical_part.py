#!/usr/bin/env python
import os, sys
import json

def printDict(dictionary):
	print(json.dumps(dictionary, indent = 4, sort_keys = True))


# PHYSICAL PART CLASS
class PhysicalPart(object):
	def __init__(self, part_id):
		self.id = part_id
		self.Manufacturing = Manufacturing()
		# self.Symbol = self.Symbol()
		# self.Footprint = self.Footprint()
		# self.Model3D = self.Model3D()

	def Print(self):
		print('Physical Part ID :', self.id)
		print('Manufacturing :')
		printDict(self.Manufacturing.Manufacturers)

# MANUFACTURING CLASS
class Manufacturing(object):
	def __init__(self):
		self.Manufacturers = {}

	def UpdateManufacturers(self, Manufacturer, PartNumber):
		dPartNumber = { PartNumber : {} }
		if Manufacturer not in self.Manufacturers:
			newMan = { Manufacturer : dPartNumber }
			self.Manufacturers.update(newMan)
		else:
			self.Manufacturers[Manufacturer].update(dPartNumber)

	def UpdateSuppliers(self, Manufacturer, PartNumber, Supplier, Number):
		dSupplierItem = { Supplier : Number }
		if Manufacturer in self.Manufacturers:
			if Supplier not in self.Manufacturers[Manufacturer][PartNumber]:
				self.Manufacturers[Manufacturer][PartNumber].update(dSupplierItem)


# MAIN
if __name__ == '__main__':
	resistor = PhysicalPart('RES SMD 110K OHM 1% 1/10W 0603')

	# resistor.Manufacturing.UpdateManufacturers('Yageo', 'RC0603FR-07110KL')
	# resistor.Manufacturing.UpdateSuppliers('Yageo', 'RC0603FR-07110KL', 'Digikey', '311-110KHRCT-ND')
	# resistor.Manufacturing.UpdateSuppliers('Yageo', 'RC0603FR-07110KL', 'Mouser', '603-RC0603FR-07110KL')

	# resistor.Manufacturing.UpdateManufacturers('Panasonic Electronic Components', 'ERJ-3EKF1103V')
	# resistor.Manufacturing.UpdateSuppliers('Panasonic Electronic Components', 'ERJ-3EKF1103V', 'Digikey', 'P110KHCT-ND')
	# resistor.Manufacturing.UpdateSuppliers('Panasonic Electronic Components', 'ERJ-3EKF1103V', 'Mouser', '667-ERJ-3EKF1103V')

	# resistor.Manufacturing.UpdateManufacturers('Panasonic Electronic Components', 'ERJ-PA3F1103V')
	# resistor.Manufacturing.UpdateSuppliers('Panasonic Electronic Components', 'ERJ-PA3F1103V', 'Digikey', 'P110KBYCT-ND')
	# resistor.Manufacturing.UpdateSuppliers('Panasonic Electronic Components', 'ERJ-PA3F1103V', 'Mouser', '667-ERJ-PA3F1103V')

	# resistor.Print()
