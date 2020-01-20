#!/usr/bin/env python
import json

# Settings
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
# Pretty dictionnay print
def printDict(dictionary):
	print(json.dumps(dictionary, indent = 4, sort_keys = True))