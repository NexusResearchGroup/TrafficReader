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
	
	return vol_array.tolist()

def list_occupancies(occupancyfile):
	'''
	Reads the binary occupancy ratios from occupancyfile and returns them as a list.
	'''
	
	# Set the array to read two bytes at a time
	occ_array = array('h')
	
	# Load the array from the file. This will raise EOFError if less than 2880 records are found.
	occ_array.fromfile(occupancyfile, 2880)
	
	return occ_array.tolist()
