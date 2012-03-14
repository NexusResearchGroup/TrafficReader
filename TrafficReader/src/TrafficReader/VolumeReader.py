'''
Created on Mar 8, 2012

@author: owenx148
'''

from datetime import date, datetime, timedelta

class VolumeReader():
    '''
    Reads volume data from a volume file within a .traffic file
    '''

    def __init__(self, volumefile, date, detector):
        '''
        Constructor
        '''
        
        # Verify that the specified file is of the correct length
        self._volumefile.seek(0,2)
        length = self._volumefile.tell()
        if length != 2880:
            raise ValueError('Volume file has length of ' + str(length) + ', should be 2880')
        
        # file is ok, so attach to it
        self.set_file(volumefile)
        
        self._firstbyte = 0
        self._lastbyte = 2879
        self._fieldbytewidth = 1
        self._fieldtimewidth = timedelta(seconds=30)
        self._min_volvalue = 0
        self._max_volvalue = 40 # Recommended by MnDOT

        
    def set_file(self, volumefile):
        self._volumefile = volumefile
        self._currentbyte = 0
        self._date = date
        self._detector = detector
        self._currenttime = time(0,0,0)
        
        self._volumefile.seek(self._current_byte)
    
    def __iter__(self):
        return self
    
    def __next__(self):
        
        
if __name__ == '__main__':
    pass
