from __future__ import division
from readers import list_occupancies, list_volumes
from zipfile import ZipFile
from os import path
from math import exp
from collections import deque

class TrafficReader:
	'''
	Provides an interface to a single .traffic file
	'''

	def __init__(self, trafficfile=None):
		'''
		Returns a new TrafficReader, optionally initialized with a specified
		.traffic file
		'''

		if trafficfile != None:
			self.loadfile(trafficfile)

	def loadfile(self, trafficfile):
		'''
		Instructs a TrafficReader instance to load values from the specified
		.traffic file
		'''

		self._trafficfile = trafficfile
		self._zipfile = ZipFile(self._trafficfile)
		self.directory = path.dirname(trafficfile)

	def list_detectors(self):
		'''
		Returns a list of the IDs of all detectors which have records in the
		current .traffic file
		'''

		zipfile = ZipFile(self._trafficfile)

		detlist = []

		for file in zipfile.namelist():
			(id, ext) = path.splitext(file)
			if ext == '.v30':
				detlist.append(id)

		return detlist

	def occupancies_for_detector(self, detectorID):
		'''
		Returns a list of the 30-second occupancy values recorded in this
		.traffic file for the detector with the specified ID.
		'''

		name = str(detectorID) + '.c30'
		try:
			occ_file = self._zipfile.open(name)
			return list_occupancies(occ_file)
		except KeyError:
			return [None] * 2880

	def volumes_for_detector(self, detectorID):
		'''
		Returns a list of the 30-second volume values recorded in this .traffic
		file for the detector with the specified ID.
		'''

		name = str(detectorID) + '.v30'
		try:
			vol_file = self._zipfile.open(name)
			return list_volumes(vol_file)
		except KeyError:
			return [None] * 2880

	def onemin_data_for_detector(self, detectorID):
		'''
		Returns a tuple (vol_list, occ_list) where vol_list is volume data at
		1-minute increments and occ_list is occupancy data at 1-minute
		increments.

		For each 1-minute interval, consider four values:
			- vol(i), vol(i+1)
			- occ(i), occ(i+1)

		All four values must be valid (that is, != None). If any one of these
		values is invalid, both volume and occupancy for time slot i is
		reported as invalid.
		'''

		volume30s = self.volumes_for_detector(detectorID)
		occupancy30s = self.occupancies_for_detector(detectorID)

		volume1m = deque()
		occupancy1m = deque()

		for i in range(0, len(volume30s), 2):
			if (volume30s[i] == None
				or volume30s[i+1] == None
				or occupancy30s[i] == None
				or occupancy30s[i+1] == None):
				volume1m.append(None)
				occupancy1m.append(None)
			else:
				volume1m.append(volume30s[i] + volume30s[i+1])
				occupancy1m.append((occupancy30s[i] + occupancy30s[i+1]) / 2)

		return list(volume1m), list(occupancy1m)

	def onemin_speeds_for_detector(self, detectorID, speed_limit=70,
								   field_length=None):
		'''
		Returns a list of 1-minute speeds, one for each minute of the day,
		starting at 00:00.
		'''

		vols, occs = self.onemin_data_for_detector(detectorID)

		if field_length == None:
		# if we were not given a field length, try to calculate from volume and
		# occupancy
			avg_field_length, field_lengths = self.field_lengths(vols, occs,
																 speed_limit)
		else:
		# if we were given a field length, use it
			avg_field_length = field_length
			field_lengths = [field_length] * 1440

		if avg_field_length == None:
		# if we were not given a field length and we are unable to calculate it,
		# use the speed limit as the free-flow speed
			free_flow_speed = speed_limit
		else:
		# otherwise, calculate the free-flow speed from the volume, occupancy,
		# and field length
			free_flow_speed = self.free_flow_speed(vols, occs, avg_field_length)

		speeds = deque()

		# given in published report
		theta = 0.15

		for i in range(len(occs)):
			if (occs[i] == None
				or free_flow_speed == None
				or avg_field_length == None
				or field_lengths[i] == None):
				speeds.append(None)
			elif 0 < occs[i] < 0.1:
				speeds.append(free_flow_speed * (1 - ( (occs[i] * avg_field_length) / field_lengths[i]) ) )
			elif 0.1 <= occs[i] <= 0.15:
				speeds.append(free_flow_speed * (1 - occs[i]) )
			else:
				exponent = -1 * (1 / theta) * ((100 * occs[i]) / (100 - theta))
				speeds.append(free_flow_speed * (1 - theta) * exp(exponent) )

		return list(speeds)

	def fivemin_speeds_for_detector(self, detectorID, speed_limit=70):
		'''
		Returns a list of 5-minute speeds
		'''

		speeds1m = self.onemin_speeds_for_detector(detectorID)

		speeds5m = deque()

		for i in range(0, len(speeds1m), 5):
			interval_speeds = speeds1m[i:i+4]
			# if any of the speeds in this interval are None, the whole interval
			# gets None
			if interval_speeds.count(None) > 0:
				speeds5m.append(None)
			else:
				speeds5m.append(sum(interval_speeds) / len(interval_speeds))

		return list(speeds5m)

	def field_lengths(self, volumes, occupancies, speed_limit=70):
		'''
		Given a list of volumes, a list of corresponding occupancies, and a
		speed limit, returns overall average effective field length of the detector.
		'''

		lengths = deque()
		valid_lengths = deque()

		for i in range(len(volumes)):
			if 0 < occupancies[i] <= 0.1 and volumes[i] != None and volumes[i] != 0:
				length = (speed_limit * occupancies[i] * 5280) / (volumes[i] * 60)
				lengths.append(length)
				valid_lengths.append(length)
			else:
				lengths.append(None)

		# if there are no valid lengths, return average length of None.
		if len(valid_lengths) != 0:
			average_length = sum(valid_lengths) / len(valid_lengths)
		else:
			average_length = None

		return average_length, list(lengths)

	def free_flow_speed(self, volumes, occupancies, field_length):
		'''
		Returns the free-flow speed calculated from the given conditions by
		looking at times where the occupancy is less than 10%
		'''

		# given in published report
		max_occupancy = 0.98
		max_density = (max_occupancy * 5280) / field_length

		valid_volumes = deque()
		valid_densities = deque()

		for i in range(len(occupancies)):
			if 0 < occupancies[i] < 0.1 and volumes[i] > 0:
				density = (occupancies[i] * 5280) / field_length
				valid_densities.append(density - ((density ** 2) / max_density))
				valid_volumes.append(volumes[i])

		# if there are not valid volumes or densities, return ffs of None
		if sum(valid_volumes) == 0 or sum(valid_densities) == 0:
			return None

		return (60 * sum(valid_volumes)) / sum(valid_densities)

	def print_average_speeds_for_detectors(self, start=0, end=7000):
		avgspeedlist = []
		for d in range(start, end):
			try:
				speedlist = self.fivemin_speeds_for_detector(d)
			except KeyError:
				print "No data for detector " + str(d)
				continue

			speedlist = [speed for speed in speedlist if speed != None]

			speedsum = sum(speedlist)
			speedcount = len(speedlist)

			if speedsum == 0 or speedcount == 0:
				print "Average speed for detector " + str(d) + ": 0"
			else:
				avgspeed = speedsum/speedcount
				print "Average speed for detector " + str(d) + ": " + str(avgspeed)
				avgspeedlist.append(avgspeed)

		print "Overall average: " + str(sum(avgspeedlist) / len(avgspeedlist))
