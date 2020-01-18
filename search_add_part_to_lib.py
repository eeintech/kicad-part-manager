#!/usr/bin/env python
import os, sys, json
sys.path.append('kicad-tools')
from kicad_schlib import ComponentLibManager
sys.path.append('octopart-tools')
from octopart_api import OctopartAPI

def printDict(dictionary):
	print(json.dumps(dictionary, indent = 4, sort_keys = True))

if __name__ == '__main__':
	OctoApi = OctopartAPI()
	CompLibMngr = ComponentLibManager()

	if not len(sys.argv) > 1:
		print('Provide part number to search')
		sys.exit(-1)

	PartNumber = sys.argv[1]

	# Check Octopart
	octopart_results = OctoApi.SearchPartNumber(PartNumber)
	#printDict(octopart_results)

	if octopart_results:
		# Get data (note: could use octopart_results instead)
		component_data = CompLibMngr.GetComponentData(PartNumber)
		#printDict(component_data)

		add_lib = CompLibMngr.AddComponentToLib(component_data)
		if add_lib:
			print('Success')

		# del_lib = CompLibMngr.DeleteComponentFromLib(PartNumber)
		# if del_lib:
		# 	print('Success')