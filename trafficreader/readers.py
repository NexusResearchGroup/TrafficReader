from __future__ import division
import struct

def list_volumes(volumefile):
	'''
	Reads the binary volume counts from volumefile and returns them as a list.
	'''

	# interpret the file as a sequence of 2880 signed chars (single bytes)
	format = 'b' * 2880

	try:
		vol_list = list(struct.unpack(format, volumefile.read()))
	# catch files with invalid lengths
	except struct.error:
		vol_list = [-1] * 2880

	# Valid sample ranges for volumes are 0 - 40. If outside this range, set to
	# None to indicate bad data.
	for i in range(len(vol_list)):
		if vol_list[i] < 0 or vol_list[i] > 40:
			vol_list[i] = None
	return vol_list

def list_occupancies(occupancyfile):
	'''
	Reads the binary occupancy ratios from occupancyfile and returns them as a
	list.
	'''

	# interpret the file as a sequence of 2880 short integers (double bytes,
	# big endian)
	format = '>' + ('h' * 2880)

	try:
		occ_list = list(struct.unpack(format, occupancyfile.read()))
	except struct.error:
		occ_list = [-1] * 2880

	# Valid sample ranges for occupancies are 0 - 1800. If outside this range,
	# set to None to indicate bad data. Return valid data as a ratio of 1800.
	for i in range(len(occ_list)):
		if occ_list[i] < 0 or occ_list[i] > 1800:
			occ_list[i] = None
		else:
			occ_list[i] = occ_list[i] / 1800

	return occ_list
