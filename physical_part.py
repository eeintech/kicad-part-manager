#!/usr/bin/env python
import json, urllib.request

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


# OCTOPART API
class OctopartAPI(object):
	def __init__(self):
		self.ApiKey = 'fff72000bb1d7802b853'
		self.ApprovedSuppliers = ['Digi-Key', 'Mouser']
		self.resistor_specs = ['resistance', 'resistance_tolerance', 'power_rating']

	def SearchPartNumber(self, PartNumber):
		search_results = { 'manufacturer' : '', 'partnumber' : '', 'suppliers' : {}, 'description' : '', 'specs' : {}, 'datasheet_url' : '' }

		url = 'http://octopart.com/api/v3/parts/match?'
		url += '&queries=[{"mpn":"' + PartNumber + '"}]'
		url += '&apikey=' + self.ApiKey
		url += '&include[]=descriptions'
		url += '&include[]=specs'
		url += '&include[]=datasheets'
		
		with urllib.request.urlopen(url) as url:
			data = url.read()
		response = json.loads(data)

		# Manufacturers
		for result in response['results']:
			for item in result['items']:
				# Save manufacturer name and part number
				search_results['manufacturer'] = item['manufacturer']['name']
				search_results['partnumber'] = item['mpn']

				# Save suppliers
				for offer in item['offers']:
					if offer['seller']['name'] in self.ApprovedSuppliers:
						if (int(offer['moq']) == 1) and (int(offer['in_stock_quantity']) > 0):
							supplier = offer['seller']['name']
							number = offer['sku']
							if supplier not in search_results['suppliers']:
								search_results['suppliers'].update({supplier : number})
						#print(offer['packaging'])
				
				# Save description
				for description in item['descriptions']:
					for source in description['attribution']['sources']:
						#printDict(source)
						if 'Digi-Key' in source['name']:
							search_results['description'] = description['value']
							break
							break

				# Save specs
				for spec in item['specs']:
					if spec in self.resistor_specs:
						value = item['specs'][spec]['display_value'].replace(' ','').replace('\u03a9','').replace('\u00b1', '')
						search_results['specs'].update({spec : value})

				# Save datasheet url
				for datasheet in item['datasheets']:
					if datasheet['attribution']['sources']:
						for source in datasheet['attribution']['sources']:
							if 'Digi-Key' in source['name']:
								search_results['datasheet_url'] = datasheet['url']
								break
								break

		return search_results


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

	OctopartAPI = OctopartAPI()
	octopart_results = OctopartAPI.SearchPartNumber('RC0603FR-07110KL')
	printDict(octopart_results)