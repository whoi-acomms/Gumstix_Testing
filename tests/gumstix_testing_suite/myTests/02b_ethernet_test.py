#dependencies="00a"
__author__ = 'chet'
import gumtools as gt
import serial

ser = serial.Serial(port='COM7', baudrate=115200, timeout=1)
if not gt.login(ser):
    gt.fail([ser])
ser.write('ping google.com\r')
ping = gt.expect(ser, ['64 bytes from'], 10)
if ping == -1:
    gt.fail([ser])
ser.write('\x03')
gt.expect(ser, ['[#]'], 10)
ser.write('wget http://www.ourdocuments.gov/document_data/pdf/doc_013.pdf\r')
dl = gt.expect(ser, ['saved'], 15)
if dl == -1:
    gt.fail([ser])
ser.close()
print 'PASSED'