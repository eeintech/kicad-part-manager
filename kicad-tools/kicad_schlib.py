#!/usr/bin/env python
import sys, os
import json, pickle
from schlib import SchLib
sys.path.append('globals')
from globals import search_results_settings, symbol_libraries_paths, symbol_templates_paths, footprint_lookup_table
from globals import printDict

class ComponentLibManager(object):
	def __init__(self):
		self.version = 'kicadschlib-0.1'

	def LoadSettings(self):
		print('Settings')

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

	def GetComponentCategory(self, ComponentData):
		# Load category
		category = None
		if 'Resistors' in ComponentData['categories']:
			category = 'Resistors'
		elif 'Capacitors' in ComponentData['categories']:
			category = 'Capacitors'

		return category

	def GetComponentPackage(self, ComponentData):
		# Load package
		try:
			package = ComponentData['specs']['case_package']
		except:
			package = None

		return package

	def AddComponentToLib(self, ComponentData):
		category = self.GetComponentCategory(ComponentData)
		package = self.GetComponentPackage(ComponentData)
		# Load Library and Template paths
		if category:
			LibraryPath = symbol_libraries_paths[category]
			TemplatePath = symbol_templates_paths[category]
			# Check files exist
			if not os.path.isfile(LibraryPath):
				print('Issue loading library file (', LibraryPath, ')')
				return False
			if not os.path.isfile(TemplatePath):
				print('Issue loading template file (', TemplatePath, ')')
				return False
		else:
			print('Unkown component category: no matching library and template paths')
			return False

		# Load library
		schlib = SchLib(LibraryPath)
		print('Number of parts in library:', schlib.getComponentCount())

		# Check if part already in library
		for component in schlib.components:
			if component.definition['name'] == ComponentData['partnumber']:
				print('Component already in library')
				return False

		# Load template
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
					if (category != None) & (package != None):
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

	def DeleteComponentFromLib(self, ComponentPartNumber):
		category = self.GetComponentCategory(ComponentData)
		# Load Library and Template paths
		if category:
			LibraryPath = symbol_libraries_paths[category]
			# Check file exists
			if not os.path.isfile(LibraryPath):
				print('Issue loading library file (', LibraryPath, ')')
				return False
		else:
			print('Unkown component category: no matching library path')
			return False

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

# 		CompLibMngr.AddComponentToLib(ComponentData)
# 		#CompLibMngr.DeleteComponentFromLib(ComponentData['partnumber'])
