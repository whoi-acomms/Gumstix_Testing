# $Id$

import serial
import time

eser0 = serial.Serial('/dev/eser0', 115200, timeout=1)
ttyO0 = serial.Serial('/dev/ttyO0', 115200, timeout=1)
eser1 = serial.Serial('/dev/eser1', 115200, timeout=1)
ttyO1 = serial.Serial('/dev/ttyO1', 115200, timeout=1)

write_buf = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ\n'
N = 3
iteration = 0
logfile = open('./gumstix_serial_port_burnin.log', 'a')

while True:

	for n in range(1,N):
		iteration = iteration + 1

		eser0.write(write_buf)
		read_buf = ttyO0.readline()
		if read_buf != write_buf:
			tup = time.asctime() + 'error writing from eser0 to ttyO0, iteration ', iteration, '\n'
			print str(tup)
			logfile.write(str(tup))
			logfile.write('\n')
			logfile.flush()

		ttyO0.write(write_buf)
		read_buf = eser0.readline()
		if read_buf != write_buf:
			tup = time.asctime() + 'error writing from ttyO0 to eser0, iteration ', iteration, '\n'
			print str(tup)
			logfile.write(str(tup))
			logfile.write('\n')
			logfile.flush()

		eser1.write(write_buf)
		read_buf = ttyO1.readline()
		if read_buf != write_buf:
			tup = time.asctime() + 'error writing from eser1 to ttyO1, iteration ', iteration, '\n'
			print str(tup)
			logfile.write(str(tup))
			logfile.write('\n')
			logfile.flush()

		ttyO1.write(write_buf)
		read_buf = eser1.readline()
		if read_buf != write_buf:
			tup = time.asctime() + 'error writing from ttyO1 to eser1, iteration ', iteration, '\n'
			print str(tup)
			logfile.write(str(tup))
			logfile.write('\n')
			logfile.flush()

	tup = time.asctime() + ': success! wrote alphabet eser0<->ttyO0 and eser1<->ttyO1 (',N,'times, iteration',iteration,').\n'
	print str(tup)
	logfile.write(str(tup))
	logfile.write('\n')
	logfile.flush()
	time.sleep(10)

	
	
	
logfile.flush()
logfile.close()
exit

