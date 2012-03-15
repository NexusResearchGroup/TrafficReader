'''
Created on Mar 14, 2012

@author: owenam
'''
from array import array

def list_volumes(volumefile):
	'''
	Reads the binary volume counts from volumefile and returns them as a list.
	'''
	
	# Set the array to read single bytes
	vol_array = array('b')
	
	# Load the array from the file. This will raise EOFError if less than 2880 records are found.
	vol_array.fromfile(volumefile, 2880)
	
	vol_list = vol_array.tolist()
	
	# Valid sample ranges for volumes are 0 - 40. If outside this range, set to -1 to indicate bad data.
	for i in range(len(vol_list)):
		if vol_list[i] < 0 or vol_list[i] > 40:
			vol_list[i] = -1
	
	return vol_list

def list_occupancies(occupancyfile):
	'''
	Reads the binary occupancy ratios from occupancyfile and returns them as a list.
	'''
	
	# Set the array to read two bytes at a time
	occ_array = array('h')
	
	# Load the array from the file. This will raise EOFError if less than 2880 records are found.
	occ_array.fromfile(occupancyfile, 2880)
	
	occ_list = occ_array.tolist()
	
	# Valid sample ranges for occupancies are 0 - 1800. If outside this range, set to -1 to indicate bad data.
	for i in range(len(occ_list)):
		if occ_list[i] < 0 or occ_list[i] > 1800:
			occ_list[i] = -1
	
	return occ_list