from readers import list_occupancies, list_volumes

class TrafficReader:
	'''
	Provides an interface to a single .traffic file
	'''
	
	def __init__(self, trafficfile=None):
		'''
		Returns a new TrafficReader, optionally initialized with a specified .traffic file
		'''
	
	def loadfile(
	
	def list_detectors(self):
		'''
		Returns a list of the IDs of all detectors who have records in the current .traffic file
		'''
	
	def occupancies_for_detector(self, detectorID):
		'''
		Returns a list of the occupancy values recorded in this .traffic file for the detector with the specified ID.
		'''
		
	def volumes_for_detector(self, detectorID):
		'''
		Returns a list of the volume values recorded in this .traffic file for the detector with the specified ID.
		'''
	
	