from __future__ import division
from readers import list_occupancies, list_volumes
from zipfile import ZipFile
from os import path
from math import exp

class TrafficReader:
	'''
	Provides an interface to a single .traffic file
	'''
	
	_trafficfile = None
	_zipfile = None
	
	def __init__(self, trafficfile=None):
		'''
		Returns a new TrafficReader, optionally initialized with a specified .traffic file
		'''
		
		if trafficfile != None:
			self.loadfile(trafficfile)
	
	def loadfile(self, trafficfile):
		'''
		Instructs a TrafficReader instance to load values from the specified .traffic file
		'''
		
		self._trafficfile = trafficfile
		self._zipfile = ZipFile(self._trafficfile)
	
	def list_detectors(self):
		'''
		Returns a list of the IDs of all detectors which have records in the current .traffic file
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
		Returns a list of the 30-second occupancy values recorded in this .traffic file for the detector with the specified ID.
		'''
		
		name = str(detectorID) + '.c30'
		try:
			occ_file = self._zipfile.open(name)
			return list_occupancies(occ_file)
		except KeyError:
			return [-1] * 2880
		
	def volumes_for_detector(self, detectorID):
		'''
		Returns a list of the 30-second volume values recorded in this .traffic file for the detector with the specified ID.
		'''
		
		name = str(detectorID) + '.v30'
		try:
			vol_file = self._zipfile.open(name)
			return list_volumes(vol_file)
		except KeyError:
			return [-1] * 2880
	
	def onemin_data_for_detector(self, detectorID):
		'''
		Returns a tuple (vol_list, occ_list) where vol_list is volume data at 1-minute increments and occ_list is occupancy data at 1-minute increments.
		
		For each 1-minute interval, consider four values:
			- vol(i), vol(i+1)
			- occ(i), occ(i+1)
			
		All four values must be valid (that is, != -1). If any one of these values is invalid, both volume and occupancy for time slot i is reported as invalid.
		'''
		
		volume30s = self.volumes_for_detector(detectorID)
		occupancy30s = self.occupancies_for_detector(detectorID)
		
		volume1m = []
		occupancy1m = []
		
		for i in range(0, len(volume30s), 2):
			if volume30s[i] == -1 or volume30s[i+1] == -1 or occupancy30s[i] == -1 or occupancy30s[i+1] == -1:
				volume1m.append(-1)
				occupancy1m.append(-1)
			else:
				volume1m.append(volume30s[i] + volume30s[i+1])
				occupancy1m.append((occupancy30s[i] + occupancy30s[i+1]) / 2)
		
		return volume1m, occupancy1m

	def onemin_speeds_for_detector(self, detectorID, speed_limit=70, field_length=None):
		'''
		Returns a list of 1-minute speeds, one for each minute of the day, starting at 00:00.
		'''
		
		vols, occs = self.onemin_data_for_detector(detectorID)
		if field_length == None:
			avg_field_length, field_lengths = self.field_lengths(vols, occs, speed_limit)
		else:
			avg_field_length = field_length
			field_lengths = [field_length] * 1440
		free_flow_speed = self.free_flow_speed(vols, occs, avg_field_length)
				
		speeds = []
		
		# given in published report
		theta = 0.15
		
		for i in range(len(occs)):
			if occs[i] < 0 or free_flow_speed == -1 or avg_field_length == -1:
				speeds.append(-1)
			elif 0 < occs[i] < 0.1:
				speeds.append(free_flow_speed * (1 - ( (occs[i] * avg_field_length) / field_lengths[i]) ) )
			elif 0.1 <= occs[i] <= 0.15:
				speeds.append(free_flow_speed * (1 - occs[i]) )
			else:
				exponent = -1 * (1 / theta) * ((100 * occs[i]) / (100 - theta))
				speeds.append(free_flow_speed * (1 - theta) * exp(exponent) )
		
		return speeds
		
	def fivemin_speeds_for_detector(self, detectorID, speed_limit=70):
		'''
		Returns a list of 5-minute speeds
		'''
		
		speeds1m = self.onemin_speeds_for_detector(detectorID)
		
		speeds5m = []
		
		for i in range(0, len(speeds1m), 5):
			interval_speeds = speeds1m[i:i+4]
			# if any of the speeds in this interval are -1, the whole interval gets -1
			if interval_speeds.count(-1) > 0:
				speeds5m.append(-1)
			else:
				speeds5m.append(sum(interval_speeds) / len(interval_speeds))
		
		return speeds5m
	
	def field_lengths(self, volumes, occupancies, speed_limit=70):
		'''
		Given a list of volumes, a list of corresponding occupancies, and a speed limit, returns overall average effective field length of the detector.
		'''
		
		lengths = []
		valid_lengths = []
		
		for i in range(len(volumes)):
			if volumes[i] <= 0 or occupancies[i] <= 0:
				lengths.append(-1)
			elif occupancies[i] <= 0.1:
				length = (speed_limit * occupancies[i] * 5280) / (volumes[i] * 60)
				lengths.append(length)
				valid_lengths.append(length)
			else:
				lengths.append(-2)
		
		# if there are no valid lengths, return average length of -1.
		if len(valid_lengths) != 0:
			average_length = sum(valid_lengths) / len(valid_lengths)
		else:
			average_length = -1

		return average_length, lengths
		
	def free_flow_speed(self, volumes, occupancies, field_length):
		'''
		Returns the free-flow speed calculated from the given conditions by looking at times where the occupancy is less than 10%
		'''
		
		# given in published report
		max_occupancy = 0.98
		max_density = (max_occupancy * 5280) / field_length
		
		valid_volumes = []
		valid_densities = []
		
		for i in range(len(occupancies)):
			if 0 < occupancies[i] < 0.1 and volumes[i] > 0:
				density = (occupancies[i] * 5280) / field_length
				valid_densities.append(density - ((density ** 2) / max_density))
				valid_volumes.append(volumes[i])
				
		# if there are not valid volumes or densities, return ffs of -1
		if sum(valid_volumes) == 0 or sum(valid_densities) == 0:
			return -1

		return (60 * sum(valid_volumes)) / sum(valid_densities)

	def print_average_speeds_for_detectors(self, start=0, end=7000):
		avgspeedlist = []
		for d in range(start, end):
			try:
				speedlist = self.fivemin_speeds_for_detector(d)
			except KeyError:
				print "No data for detector " + str(d)
				continue
				
			for invalid in range(speedlist.count(-1)):
				speedlist.remove(-1)
				
			speedsum = sum(speedlist)
			speedcount = len(speedlist)
			
			if speedsum == 0 or speedcount == 0:
				print "Average speed for detector " + str(d) + ": 0"
			else:
				avgspeed = speedsum/speedcount
				print "Average speed for detector " + str(d) + ": " + str(avgspeed)
				avgspeedlist.append(avgspeed)
				
		print "Overall average: " + str(sum(avgspeedlist) / len(avgspeedlist))