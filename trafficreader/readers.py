'''
Created on Mar 14, 2012

@author: owenam
'''
from array import array

def list_volumes(volumefile):
	'''
	Reads the binary volume counts from volumefile and returns them as a list.
	'''

	vol_array = array('b', volumefile)
	
	# Confirm that the array read the correct number (2880) of volume measurements
	num_records = vol_array.buffer_info()[1]
	if num_records != 2880:
		raise ValueError('Volume file has length of ' + str(num_records) + ', should be 2880')
	
	return vol_array.tolist()

def list_occupancies(occupancyfile):
	'''
	Reads the binary occupancy ratios from occupancyfile and returns them as a list.
	'''
	occ_array = array('h', volumefile)
	
	# Confirm that the array read the correct number (2880) of volume measurements
	num_records = vol_array.buffer_info()[1]
	if num_records != 2880:
		raise ValueError('Volume file has length of ' + str(num_records) + ', should be 2880')
	
	# MnDOT example shows we need to swap byte order -- does this depend on host OS?
	occ_array.byteswap()
	
	return vol_array.tolist()
