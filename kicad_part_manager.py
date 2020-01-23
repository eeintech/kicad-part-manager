#!/usr/bin/env python
import os, sys, json, argparse
sys.path.extend(['globals', 'kicad-tools', 'octopart-tools'])
import globals, kicad_schlib, octopart_api

if __name__ == '__main__':
	# Argument handler
	parser = argparse.ArgumentParser(description = """KiCad Part Manager Tool""")
	parser.add_argument("-add_search", required = False, default = "",
						help = "Add part to symbol library using provided part number to fetch data from API")
	parser.add_argument("-add_direct", required = False, default = "",
						help = "Add part to symbol library using provided part number to fetch data from file")
	parser.add_argument("-delete", required = False, default = "",
						help = "Delete part from symbol library using provided part number and part type (-type)")
	parser.add_argument("-type", required = False, default = "",
						help = "Part type or category (needed for part deletion)")

	args = parser.parse_args()

	# Call classes
	OctoApi = octopart_api.OctopartAPI()
	CompLibMngr = kicad_schlib.ComponentLibManager()

	if len(sys.argv) > 1:
		# API search and add
		if args.add_search:
			part_number = args.add_search
			# Fetch data from Octopart
			octopart_results = OctoApi.SearchPartNumber(part_number)

			if octopart_results:
				add_lib = CompLibMngr.AddComponentToLib(octopart_results)
				if add_lib:
					print('Success')
		# Load file data and add
		elif args.add_direct:
			part_number = args.add_direct
			# Get data from file
			component_data = CompLibMngr.GetComponentData(part_number)

			if component_data:
				print('Component search results found')
				add_lib = CompLibMngr.AddComponentToLib(component_data)
				if add_lib:
					print('Success')
			else:
				print('Component search results not found\nTry -add_search instead')
		# Delete part from corresponding library
		elif args.delete:
			if args.type:
				part_number = args.delete
				category = args.type
				del_lib = CompLibMngr.DeleteComponentFromLib(part_number, category)
				if del_lib:
					print('Success')
			else:
				print('-delete requires -type (eg. Resistors, Capacitors)')

		sys.exit(0)
	else:
		print('Missing arguments\nTry --help to start')
		sys.exit(-1)