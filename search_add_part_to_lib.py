#!/usr/bin/env python
import os, sys, json
sys.path.extend(['globals', 'kicad-tools', 'octopart-tools'])
import globals, kicad_schlib, octopart_api

if __name__ == '__main__':
	OctoApi = octopart_api.OctopartAPI()
	CompLibMngr = kicad_schlib.ComponentLibManager()

	if not len(sys.argv) > 1:
		print('Provide part number to search')
		sys.exit(-1)

	part_number = sys.argv[1]

	# Check Octopart
	octopart_results = OctoApi.SearchPartNumber(part_number)
	#printDict(octopart_results)

	if octopart_results:
		# Get data (note: could use octopart_results instead)
		component_data = CompLibMngr.GetComponentData(part_number)
		#printDict(component_data)

		add_lib = CompLibMngr.AddComponentToLib(component_data)
		if add_lib:
			print('Success')

		# del_lib = CompLibMngr.DeleteComponentFromLib(component_data)
		# if del_lib:
		# 	print('Success')