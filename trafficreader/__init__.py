from readers import list_occupancies, list_volumes
from zipfile import ZipFile
from os import path
from __future__ import division

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
		Returns a list of the occupancy values recorded in this .traffic file for the detector with the specified ID.
		'''
		
		name = str(detectorID) + '.c30'
		occ_file = self._zipfile.open(name)
		return list_occupancies(occ_file)
		
		
	def volumes_for_detector(self, detectorID):
		'''
		Returns a list of the volume values recorded in this .traffic file for the detector with the specified ID.
		'''
		
		name = str(detectorID) + '.v30'
		vol_file = self._zipfile.open(name)
		return list_volumes(vol_file)