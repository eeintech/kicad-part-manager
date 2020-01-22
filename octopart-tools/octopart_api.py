#!/usr/bin/env python
import os, sys, json
import urllib.request, pickle
if 'globals' not in sys.path:
	# When this file is executed directly
	sys.path.append('globals')
	from globals import search_results_settings, printDict
else:
	# When this file is executed from application
	from globals.globals import search_results_settings, printDict

# Api key file path
apikey_path = 'octopart-tools/octopart_api.key'

# OCTOPART API
class OctopartAPI(object):
	def __init__(self, KeyFile = apikey_path):
		with open(KeyFile, 'r') as octo_api_key:
			self.ApiKey = octo_api_key.readline().replace('\n','')
			#print(self.ApiKey)
		self.ApprovedSuppliers = ['Digi-Key']#, 'Mouser']
		self.Specs = {	'Resistors' : ['resistance', 'resistance_tolerance', 'power_rating', 'case_package'], \
						'Capacitors' : ['capacitance', 'capacitance_tolerance', 'voltage_rating_dc', 'case_package'] }
		self.WriteFile = True

	def SearchPartNumber(self, PartNumber):
		global search_results_settings
		# Define file name
		filename = search_results_settings['directory'] + PartNumber + search_results_settings['extension']

		# Check if search results already exist and return stored data
		if os.path.isfile(filename):
			print("Results Found")
			file = open(filename, 'rb')
			search_results = pickle.load(file)
			file.close()
			return search_results

		# Use Octopart API
		print("Octopart API Search")
		search_results = { 	'manufacturer' : '', 'partnumber' : '', 'suppliers' : {}, 'description' : '', \
							'specs' : {}, 'datasheet_url' : '', 'categories' : [] }

		url = 'http://octopart.com/api/v3/parts/match?'
		url += '&queries=[{"mpn":"' + PartNumber + '"}]'
		url += '&apikey=' + self.ApiKey
		url += '&include[]=descriptions'
		url += '&include[]=specs'
		url += '&include[]=datasheets'
		url += '&include[]=category_uids'
		
		with urllib.request.urlopen(url) as url:
			data = url.read()
		response = json.loads(data)

		#printDict(response)

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

				# Save datasheet url
				for datasheet in item['datasheets']:
					# Check that the sources are listed before enumarating them
					if datasheet['attribution']['sources']:
						for source in datasheet['attribution']['sources']:
							if 'Digi-Key' in source['name']:
								search_results['datasheet_url'] = datasheet['url']
								break
								break

				# TEMPORARY - DELETE
				if search_results['datasheet_url'] == "":
					search_results['datasheet_url'] = "DATASHEET_NOT_FOUND"

				# Save categories uids
				categories_uids = []
				for category_uid in item['category_uids']:
					categories_uids.append(category_uid)

				# Fetch categories names
				url = 'http://octopart.com/api/v3/categories/get_multi'
				url += '?apikey=' + self.ApiKey
				args = []
				for category_uid in categories_uids:
					args.append(('uid[]', category_uid))
				url += "&" + urllib.parse.urlencode(args)

				with urllib.request.urlopen(url) as url:
					data = url.read()
				cat_response = json.loads(data)

				# Save categories names
				for (uid, category) in cat_response.items():
					search_results['categories'].append(category['name'])

				# Save specs
				for spec in item['specs']:
					# Resistors
					if ('Resistors' in search_results['categories']) and (spec in self.Specs['Resistors']):
						value = item['specs'][spec]['display_value'].replace(' ','').replace('\u03a9','').replace('k', 'K')#.replace('\u00b1', '')
						search_results['specs'].update({spec : value})
					# Capacitors
					elif ('Capacitors' in search_results['categories']) and (spec in self.Specs['Capacitors']):
						if spec == 'case_package':
							value = item['specs'][spec]['value'][1]
						else:
							value = item['specs'][spec]['display_value'].replace(' ','').replace('.0', '')
						search_results['specs'].update({spec : value})


		if search_results and self.WriteFile:
			file = open(filename, 'wb')
			pickle.dump(search_results, file)
			file.close()

		return search_results

# MAIN
if __name__ == '__main__':
	if len(sys.argv) > 1:
		OctopartAPI = OctopartAPI()
		octopart_results = OctopartAPI.SearchPartNumber(sys.argv[1])
		printDict(octopart_results)
