#!/usr/bin/env python
import sys, os
import json, pickle
from schlib import SchLib

# Settings (load from file in the future)
search_results_settings = {	'directory' : 'search-results/', \
							'extension' : '.dat' }
symbol_libraries_directory = 'libraries/'
symbol_libraries_paths = {	'Resistors' : symbol_libraries_directory + 'Resistors_TEST.lib', \
							'Capacitors' : symbol_libraries_directory + 'Capacitors_TEST.lib' }
symbol_templates_directory = 'symbol-templates/'
symbol_templates_paths = {	'Resistors' : symbol_templates_directory + 'resistor-template.lib', \
							'Capacitors' : symbol_templates_directory + 'capacitor-template.lib' }
footprint_lookup_table = {	'Resistors' : {	'0402' : 'Resistors:R0402', \
											'0603' : 'Resistors:R0603' }, \
							'Capacitors' : {	'0402' : 'Capacitors:C0402', \
												'0603' : 'Capacitors:C0603' } }

def printDict(dictionary):
	print(json.dumps(dictionary, indent = 4, sort_keys = True))

class ComponentLibManager(object):
	def __init__(self):
		self.version = 'kicadschlib-0.1'

	def GetComponentData(self, ComponentName):
		filename = search_results_settings['directory'] + ComponentName + search_results_settings['extension']

		# Check if file exists
		if not os.path.isfile(filename):
			print('Component search results not found')
			return None

		# Unpickle component data
		file = open(filename, 'rb')
		component_data = pickle.load(file)
		file.close()

		return component_data

	def AddComponentToLib(self, ComponentData, LibraryPath, TemplatePath):
		if not os.path.isfile(LibraryPath):
			print('Check library file path and name')
			return False

		schlib = SchLib(LibraryPath)
		print('Number of parts in library:', schlib.getComponentCount())

		# Check if part already in library
		for component in schlib.components:
			if component.definition['name'] == ComponentData['partnumber']:
				print('Component already in library')
				return False

		templatelib = SchLib(TemplatePath)
		# Load new component
		if templatelib.getComponentCount() == 1:
			for component in templatelib.components:
				new_component = component
		else:
			print('Found more than 1 component template in template file, aborting')
			return False

		# Update comment, name and definition
		new_component.comments[1] = '# ' + ComponentData['partnumber'] + '\n'
		new_component.name = ComponentData['partnumber']
		new_component.definition['name'] = ComponentData['partnumber']

		# Update documentation
		#printDict(new_component.documentation)
		new_component.documentation['description'] = ComponentData['description']
		new_component.documentation['datasheet'] = ComponentData['datasheet_url']
		new_component.documentation['keywords'] = ComponentData['specs']['resistance'] + ' ' + ComponentData['specs']['case_package']
		#print(new_component.documentation['keywords'])

		# Update fields
		for field_idx in range(len(new_component.fields)):
			if 'name' in new_component.fields[field_idx]:
				#print(field['name'])
				if 'component_part_number' in new_component.fields[field_idx]['name']:
					new_component.fields[field_idx]['name'] = ComponentData['partnumber']
				elif 'component_footprint' in new_component.fields[field_idx]['name']:
					# Look-up matching footprint
					# Find category
					category = None
					if 'Resistors' in ComponentData['categories']:
						category = 'Resistors'
					elif 'Capacitors' in ComponentData['categories']:
						category = 'Capacitors'

					if category:
						package = ComponentData['specs']['case_package']
						footprint = footprint_lookup_table[category][package]
					else:
						# No category match, use default footprint
						footprint = 'REPLACE_WITH_FOOTPRINT'

					new_component.fields[field_idx]['name'] = footprint
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

	def DeleteComponentFromLib(self, ComponentPartNumber, LibraryPath):
		if not os.path.isfile(LibraryPath):
			print('Check library file path and name')
			return False

		schlib = SchLib(LibraryPath)
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

# 		CompLibMngr.AddComponentToLib(ComponentData, symbol_libraries_paths['Resistors'], symbol_templates_paths['Resistors'])
# 		#CompLibMngr.DeleteComponentFromLib(ComponentData['partnumber'], symbol_libraries_paths['Resistors'])
