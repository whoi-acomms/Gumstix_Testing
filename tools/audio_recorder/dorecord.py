#!/usr/bin/python
'''
Created on Feb 15, 2012

@author: Eric

There is a good reason we don't use the multiprocessing module.  Trust me.
'''

from time import sleep
import subprocess
from datetime import datetime
import shutil

class DoRecord(object):
    '''
    classdocs
    '''


    def __init__(self):
        self.command_file_path = '/home/acomms/fromshore/recordcmd'
        self.current_mode = "off"
        self.slow_sleep_seconds = 600
        self.recordings_dir = '/home/acomms/recordings'
        
        self.running_process = None
        
    
    def run_loop(self):
        
        while True:        
            # Default to slow recording
            new_mode = 'slow'
            
            try:
                with open(self.command_file_path, 'r') as cmdfile:
                    new_mode = str(cmdfile.read())
            except:
                print("Error reading mode file")
                
            # If we're off, just check again in 10 seconds
            if 'off' in new_mode:
                sleep(10)
                break     
            
            # If we aren't off, we definitely want to make a recording.
            self.make_recording()
                
            if 'slow' in new_mode:
                sleep(self.slow_sleep_seconds)
              

        
    def make_recording(self):
        tempfilename = '/dev/shm/temp.wav'
        timestr = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        commandstr = '/usr/bin/arecord -c 2 -B 30000000 -f S16_LE -d 300 -t wav -r 48000 {0}'.format(tempfilename)
        print("Running: " + commandstr)
        subprocess.call(commandstr, shell=True)
        shutil.move(tempfilename, (self.recordings_dir + '/' + timestr + '.wav'))
    
        
    def __del__(self):
        if self.running_process != None:
            self.running_process.terminate()
        
        
if __name__ == '__main__':
    dorecord = DoRecord()
    
    dorecord.run_loop()
