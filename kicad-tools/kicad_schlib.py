#!/usr/bin/env python
import sys, os
import json, pickle
from schlib import SchLib

# Globals
search_results_dir = 'search-results/'
search_results_ext = '.dat'

library_dir = 'libraries/'
template_dir = 'symbol-templates/'

library_file = library_dir + 'resistor.lib'
template_file = template_dir + 'resistor_0603.lib'

def printDict(dictionary):
	print(json.dumps(dictionary, indent = 4, sort_keys = True))

class ComponentLibManager(object):
	def __init__(self):
		self.version = 'kicadschlib-0.1'

	def GetComponentData(self, ComponentName):
		filename = search_results_dir + ComponentName + search_results_ext

		# Check if file exists
		if not os.path.isfile(filename):
			print('Component search results not found')
			return None

		# Unpickle component data
		file = open(filename, 'rb')
		component_data = pickle.load(file)
		file.close()

		return component_data

	def AddComponentToLib(self, ComponentData, FileLib = library_file, Template = template_file):
		if not os.path.isfile(FileLib):
			print('Check library file path and name')
			return False

		schlib = SchLib(FileLib)
		print('Number of parts in library:', schlib.getComponentCount())

		# Check if part already in library
		for component in schlib.components:
			if component.definition['name'] == ComponentData['partnumber']:
				print('Component already in library')
				return False

		templatelib = SchLib(Template)
		# Load new component
		if templatelib.getComponentCount() == 1:
			for component in templatelib.components:
				new_component = component

		# Update comment, name and definition
		new_component.comments[1] = '# ' + ComponentData['partnumber'] + '\n'
		new_component.name = ComponentData['partnumber']
		new_component.definition['name'] = ComponentData['partnumber']

		# Update documentation
		#printDict(new_component.documentation)
		new_component.documentation['description'] = ComponentData['description']
		new_component.documentation['datasheet'] = ComponentData['datasheet_url']

		# Update fields
		for field_idx in range(len(new_component.fields)):
			if 'name' in new_component.fields[field_idx]:
				#print(field['name'])
				if 'component_part_number' in new_component.fields[field_idx]['name']:
					new_component.fields[field_idx]['name'] = ComponentData['partnumber']
				elif 'component_supplier_name' in new_component.fields[field_idx]['name']:
					for supplier in ComponentData['suppliers']:
						new_component.fields[field_idx]['name'] = supplier
						break
				elif 'component_supplier_number' in new_component.fields[field_idx]['name']:
					for supplier in ComponentData['suppliers']:
						new_component.fields[field_idx]['name'] = ComponentData['suppliers'][supplier]
						break
				elif 'component_manufacturer_name' in new_component.fields[field_idx]['name']:
					new_component.fields[field_idx]['name'] = ComponentData['manufacturer']
				elif 'component_manufacturer_number' in new_component.fields[field_idx]['name']:
					new_component.fields[field_idx]['name'] = ComponentData['partnumber']
				elif 'component_description' in new_component.fields[field_idx]['name']:
					new_component.fields[field_idx]['name'] = ComponentData['description']
				elif 'component_resistance_value' in new_component.fields[field_idx]['name']:
					new_component.fields[field_idx]['name'] = ComponentData['specs']['resistance']
				elif 'component_resistance_tolerance' in new_component.fields[field_idx]['name']:
					new_component.fields[field_idx]['name'] = ComponentData['specs']['resistance_tolerance']
				elif 'component_resistance_power_rating' in new_component.fields[field_idx]['name']:
					new_component.fields[field_idx]['name'] = ComponentData['specs']['power_rating']


		schlib.addComponent(new_component)
		schlib.save()
		print('Component added to Library')

		return True

	def DeleteComponentFromLib(self, ComponentPartNumber, FileLib = library_file):
		if not os.path.isfile(FileLib):
			print('Check library file path and name')
			return False

		schlib = SchLib(FileLib)
		print('Number of parts in library:', schlib.getComponentCount())

		try:
			schlib.removeComponent(ComponentPartNumber)
			schlib.save()
			print('Component', ComponentPartNumber, 'was removed from the library')
			return True
		except:
			print('Component', ComponentPartNumber, 'not found in library (no delete)')
			return False

# MAIN
# if __name__ == '__main__':
# 	CompLibMngr = ComponentLibManager()
# 	ComponentData = CompLibMngr.GetComponentData('RC0603FR-07110KL')
# 	if ComponentData:
# 		printDict(ComponentData)

# 		CompLibMngr.AddComponentToLib(ComponentData)
# 		#CompLibMngr.DeleteComponentFromLib(ComponentData['partnumber'], library_file)
