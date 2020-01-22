#!/usr/bin/env python
import sys, os
import json, pickle
from schlib import SchLib
if 'globals' not in sys.path:
	# When this file is executed directly
	sys.path.append('globals')
	from globals import	search_results_settings, symbol_libraries_paths, symbol_templates_paths, \
								footprint_lookup_table, printDict
else:
	# When this file is executed from application
	from globals.globals import	search_results_settings, symbol_libraries_paths, symbol_templates_paths, \
								footprint_lookup_table, printDict

# COMPONENT LIBRARY MANAGER
class ComponentLibManager(object):
	def __init__(self):
		self.version = 'kicadschlib-0.1'

	def LoadSettings(self):
		print('Settings')

	def GetComponentData(self, ComponentName):
		filename = search_results_settings['directory'] + ComponentName + search_results_settings['extension']

		# Check if file exists
		if not os.path.isfile(filename):
			return None

		# Unpickle component data
		file = open(filename, 'rb')
		component_data = pickle.load(file)
		file.close()

		return component_data

	def GetComponentCategory(self, ComponentData):
		# Load category
		category = None
		subcategory = None
		if 'Resistors' in ComponentData['categories']:
			category = 'Resistors'
		elif 'Capacitors' in ComponentData['categories']:
			category = 'Capacitors'
			if 'Ceramic Capacitors' in ComponentData['categories']:
				subcategory = 'Ceramic'

		return category, subcategory

	def GetComponentPackage(self, ComponentData):
		# Load package
		try:
			package = ComponentData['specs']['case_package']
		except:
			package = None

		return package

	def GetDocumentationKeywords(self, ComponentData, category):
		if category == 'Resistors':
			return ComponentData['specs']['resistance'] + ' ' + ComponentData['specs']['case_package']
		elif category == 'Capacitors':
			return 	ComponentData['specs']['capacitance'] + ' ' + ComponentData['specs']['voltage_rating_dc'] \
					+ ' ' + ComponentData['specs']['case_package']
		else:
			return ''

	def AddComponentToLib(self, ComponentData):
		category, subcategory = self.GetComponentCategory(ComponentData)
		package = self.GetComponentPackage(ComponentData)
		# Load Library and Template paths
		if category:
			LibraryPath = symbol_libraries_paths[category]
			if subcategory:
				TemplatePath = symbol_templates_paths[category][subcategory]
			else:
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
		library_name = LibraryPath.split('/')[-1]
		print('Number of parts in library ' + library_name + ': ' + str(schlib.getComponentCount()))

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
		new_component.documentation['keywords'] = self.GetDocumentationKeywords(ComponentData, category)
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
				# Datasheet field is unused (in documentation)
				# elif 'component_datasheet' in new_component.fields[field_idx]['name']:
				# 	new_component.fields[field_idx]['name'] = ComponentData['datasheet_url']
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
				else:
					if category == 'Resistors':
						# Resistors specific information
						if 'component_resistance_value' in new_component.fields[field_idx]['name']:
							new_component.fields[field_idx]['name'] = ComponentData['specs']['resistance']
						elif 'component_resistance_tolerance' in new_component.fields[field_idx]['name']:
							new_component.fields[field_idx]['name'] = ComponentData['specs']['resistance_tolerance']
						elif 'component_resistance_power_rating' in new_component.fields[field_idx]['name']:
							new_component.fields[field_idx]['name'] = ComponentData['specs']['power_rating']
					elif category == 'Capacitors':
						# Capacitors specific information
						if 'component_capacitance_value' in new_component.fields[field_idx]['name']:
							new_component.fields[field_idx]['name'] = ComponentData['specs']['capacitance']
						elif 'component_capacitance_tolerance' in new_component.fields[field_idx]['name']:
							new_component.fields[field_idx]['name'] = ComponentData['specs']['capacitance_tolerance']
						elif 'component_capacitance_voltage' in new_component.fields[field_idx]['name']:
							new_component.fields[field_idx]['name'] = ComponentData['specs']['voltage_rating_dc']


		schlib.addComponent(new_component)
		schlib.save()
		print('Component added to library', library_name)

		return True

	def DeleteComponentFromLib(self, PartNumber, Category):
		# Load Library and Template paths
		if Category:
			LibraryPath = symbol_libraries_paths[Category]
			# Check file exists
			if not os.path.isfile(LibraryPath):
				print('Issue loading library file (', LibraryPath, ')')
				return False
		else:
			print('Unkown component type: no matching library path')
			return False

		if not os.path.isfile(LibraryPath):
			print('Check library file path and name')
			return False

		schlib = SchLib(LibraryPath)
		library_name = LibraryPath.split('/')[-1]
		print('Number of parts in library ' + library_name + ': ' + str(schlib.getComponentCount()))

		try:
			schlib.removeComponent(PartNumber)
			schlib.save()
			print('Component', PartNumber, 'was removed from library', library_name)
			return True
		except:
			print('Component', PartNumber, 'was not found in library', library_name, '(no delete)')
			return False

# MAIN
if __name__ == '__main__':
	if len(sys.argv) > 1:
		CompLibMngr = ComponentLibManager()
		ComponentData = CompLibMngr.GetComponentData(sys.argv[1])
		if ComponentData:
			printDict(ComponentData)
			CompLibMngr.AddComponentToLib(ComponentData)
			#CompLibMngr.DeleteComponentFromLib(ComponentData)
