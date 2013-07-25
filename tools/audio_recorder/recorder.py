#!/usr/bin/python

import alsaaudio, wave
from time import strftime,gmtime

class recorder():
	card = None
	buffer = ""
	quit = False

	def __init__(self,channels, rate, fmt):
		self.card = alsaaudio.PCM(type=alsaaudio.PCM_CAPTURE, mode=alsaaudio.PCM_NORMAL)
		self.card.setformat(fmt)
		self.card.setchannels(channels)
		self.card.setrate(rate)
		self.card.setperiodsize(32)


	def getNumFrames(self,min, rate):
		return min * 60 * rate

	def readPeriod(self):
		return self.card.read()


if __name__ == "__main__":
	recorder = recorder(channels=1,rate=48000, fmt=alsaaudio.PCM_FORMAT_S16_LE)

	total_length = 0
	while True:
		try:
			filename = "%s.wav" % (strftime("%Y-%b-%d_%H_%M_%S",gmtime()))
			print "Saving %s" % (filename)
			f = wave.open(filename, 'wb')
			f.setnchannels(1)
			f.setsampwidth(2)
			f.setframerate(48000)
			while total_length < recorder.getNumFrames(5,48000):
				(frames_rec,data) = recorder.readPeriod()
		       	        total_length += (frames_rec)
        	        	f.writeframes(data)
			f.close()
			total_length = 	0
		finally:
			f.close()
