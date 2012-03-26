from __future__ import division
from readers import list_occupancies, list_volumes
from zipfile import ZipFile
from os import path

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
	
	def 1m_volumes_for_detector(detectorID):
		'''
		Returns a list of 1-minute volume values, one for each minute of the day, starting at 00:00. If both applicable 30-second volumes are valid, they are added together. If one or both 30-second volumes are missing, -1 is reported for that time slot. 
		'''
		
		30s_volumes = self.volumes_for_detector(detectorID)
		1m_volumes = []
		
		for i in range(0, len(30s_volumes), 2):
			if 30s_volumes[i] == -1 or 30s_volumes[i+1] == -1:
				1m_volumes.append(-1)
			else:
				1m_volumes.append(30s_volumes[i] + 30s_volumes[i+1])
		
		return 1m_volumes
		
	def 1m_occupancies_for_detector(detectorID):
		'''
		Returns a list of 1-minute occupancy ratios, one for each minute of the day, starting at 00:00. If both applicable 30-second occupancies are valud, they are averaged together. If one or both 30-second occupancies are missing, -1 is reported for that time slow.
		'''
		
		30s_occupancies = self.occupancies_for_detector(detectorID)
		1m_occupancies = []
		
		for i in range(0, len(30s_occupancies), 2):
			if 30s_occupancies[i] == -1 or 30s_occupancies[i+1] == -1:
				1m_occupancies.append(-1)
			else:
				1m_occupancies.append((30s_occupancies[i] + 30s_occupancies[i+1]) / 2)
	

		
		