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
		occ_file = self._zipfile.open(name)
		return list_occupancies(occ_file)
		
	def volumes_for_detector(self, detectorID):
		'''
		Returns a list of the 30-second volume values recorded in this .traffic file for the detector with the specified ID.
		'''
		
		name = str(detectorID) + '.v30'
		vol_file = self._zipfile.open(name)
		return list_volumes(vol_file)
	
	def onemin_volumes_for_detector(self, detectorID):
		'''
		Returns a list of 1-minute volume values, one for each minute of the day, starting at 00:00. If both applicable 30-second volumes are valid, they are added together. If one or both 30-second volumes are missing, -1 is reported for that time slot. 
		'''
		
		volumes_30s = self.volumes_for_detector(detectorID)
		volumes_1m = []
		
		for i in range(0, len(volumes_30s), 2):
			if volumes_30s[i] == -1 or volumes_30s[i+1] == -1:
				volumes_1m.append(-1)
			else:
				volumes_1m.append(volumes_30s[i] + volumes_30s[i+1])
		
		return volumes_1m
		
	def onemin_occupancies_for_detector(self, detectorID):
		'''
		Returns a list of 1-minute occupancy ratios, one for each minute of the day, starting at 00:00. If both applicable 30-second occupancies are valud, they are averaged together. If one or both 30-second occupancies are missing, -1 is reported for that time slow.
		'''
		
		occupancies_30s = self.occupancies_for_detector(detectorID)
		occupancies_1m = []
		
		for i in range(0, len(occupancies_30s), 2):
			if occupancies_30s[i] == -1 or occupancies_30s[i+1] == -1:
				occupancies_1m.append(-1)
			else:
				occupancies_1m.append((occupancies_30s[i] + occupancies_30s[i+1]) / 2)
				
		return occupancies_1m
	
	def onemin_speeds_for_detector(self, detectorID, speed_limit=70):
		'''
		Returns a list of 1-minute speeds, one for each minute of the day, starting at 00:00.
		'''
		
		vols = self.onemin_volumes_for_detector(detectorID)
		occs = self.onemin_occupancies_for_detector(detectorID)
		avg_field_length, field_lengths = self.field_lengths(vols, occs, speed_limit)
		free_flow_speed = self.free_flow_speed(vols, occs, avg_field_length)
		
		speeds = []
		
		# given in published report
		theta = 0.15
		
		for i in range(len(occs)):
			if occs[i] < 0:
				speeds.append(-1)
			elif 0 < occs[i] < 0.1:
				speeds.append(free_flow_speed * (1 - ( (occs[i] * avg_field_length) / field_lengths[i]) ) )
			elif 0.1 <= occs[i] <= 0.15:
				speeds.append(free_flow_speed * (1 - occs[i]) )
			else:
				exponent = -1 * (1 / theta) * ((100 * occs[i]) / (100 - theta))
				speeds.append(free_flow_speed * (1 - theta) * exp(exponent) )
		
		return speeds
				
	def field_lengths(self, volumes, occupancies, speed_limit=70):
		'''
		Given a list of volumes, a list of corresponding occupancies, and a speed limit, returns overall average effective field length of the detector.
		'''
		
		lengths = []
		
		for i in range(len(volumes)):
			if 0 <= occupancies[i] < 0.1:
				if volumes[i] == 0 or occupancies[i] == 0:
					lengths.append(-1)
				elif occupancies[i] >= 0.1:
					lengths.append(-2)
				else:
					lengths.append( (speed_limit * occupancies[i] * 5280) / (volumes[i] * 60) )
			else:
				lengths.append(-1)
		
		valid_lengths = []
		
		for i in range(len(lengths)):
			if not (lengths[i] == -1 or lengths[i] == -2):
				valid_lengths.append(lengths[i])
		
		average_length = sum(valid_lengths) / len(valid_lengths)

		return (average_length, lengths)
		
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
			if 0 <= occupancies[i] < 0.1:
				density = (occupancies[i] * 5280) / field_length
				valid_densities.append(density - ((density ** 2) / max_density))
				valid_volumes.append(volumes[i])
		
		return (60 * sum(valid_volumes)) / sum(valid_densities)
