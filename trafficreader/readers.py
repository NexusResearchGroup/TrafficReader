'''
Created on Mar 14, 2012

@author: owenam
'''
from struct import unpack

def list_volumes(volumefile):
	'''
	Reads the binary volume counts from volumefile and returns them as a list.
	'''
	
	# interpret the file as a sequence of 2880 signed chars (single bytes)
	format = 'b' * 2880
	
	vol_list = list(unpack(format, volumefile.read()))
	
	# Valid sample ranges for volumes are 0 - 40. If outside this range, set to -1 to indicate bad data.
	for i in range(len(vol_list)):
		if vol_list[i] < 0 or vol_list[i] > 40:
			vol_list[i] = -1
	
	return vol_list

def list_occupancies(occupancyfile):
	'''
	Reads the binary occupancy ratios from occupancyfile and returns them as a list.
	'''
	
	# interpret the file as a sequence of 2880 short integers (double bytes, big endian)
	format = '>' + ('h' * 2880)
	occ_list = list(unpack(format, occupancyfile.read()))
	
	# Valid sample ranges for occupancies are 0 - 1800. If outside this range, set to -1 to indicate bad data.
	for i in range(len(occ_list)):
		if occ_list[i] < 0 or occ_list[i] > 1800:
			occ_list[i] = -1
	
	return occ_list