#!/usr/bin/env python
import os, sys
import json, urllib.request, pickle

# Globals
search_results_dir = 'search-results/'
search_results_ext = '.dat'

def printDict(dictionary):
	print(json.dumps(dictionary, indent = 4, sort_keys = True))

# OCTOPART API
class OctopartAPI(object):
	def __init__(self):
		self.ApiKey = 'fff72000bb1d7802b853'
		self.ApprovedSuppliers = ['Digi-Key']#, 'Mouser']
		self.ResistorSpecs = ['resistance', 'resistance_tolerance', 'power_rating']
		self.WriteFile = True

	def SearchPartNumber(self, PartNumber):
		# Define file name
		filename = search_results_dir + PartNumber + search_results_ext

		# Check if search results already exist and return stored data
		if os.path.isfile(filename):
			print("Results Found")
			file = open(filename, 'rb')
			search_results = pickle.load(file)
			file.close
			return search_results

		# Use Octopart API
		print("Octopart API Search")
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
					if spec in self.ResistorSpecs:
						value = item['specs'][spec]['display_value'].replace(' ','').replace('\u03a9','').replace('\u00b1', '').replace('k', 'K')
						search_results['specs'].update({spec : value})

				# Save datasheet url
				for datasheet in item['datasheets']:
					if datasheet['attribution']['sources']:
						for source in datasheet['attribution']['sources']:
							if 'Digi-Key' in source['name']:
								search_results['datasheet_url'] = datasheet['url']
								break
								break

		if search_results and self.WriteFile:
			file = open(filename, 'wb')
			pickle.dump(search_results, file)
			file.close()

		return search_results

# MAIN
# if __name__ == '__main__':
# 	if len(sys.argv) > 1:
# 		OctopartAPI = OctopartAPI()
# 		octopart_results = OctopartAPI.SearchPartNumber(sys.argv[1])
# 		printDict(octopart_results)
