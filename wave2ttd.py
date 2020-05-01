#!/usr/bin/python3
import sys
import operator
import wave
from struct import *
import numpy as np
from numpy import zeros, short, fromstring, array, chararray
from numpy.fft import fft
from collections import defaultdict
from functools import reduce
import argparse
import csv

def main(args):
   ToneDict = defaultdict(list)
   buffer = [0] * 40

   with open('tones.csv') as csvfile:
      tonereader = csv.reader(csvfile, delimiter=',')
      for row in tonereader:
         ttemp = [float(row[1])] * int(round(float(row[2]) / 0.2)) + [float(row[3])] * int(round(float(row[4]) / 0.2))
         ToneDict[row[0]] = array(ttemp)

   if args.debug:
       debug = open('debug.csv', 'w', newline='')
       debugwriter=csv.writer(debug)

   f = wave.open(args.filename,'rb')
   numFrames = f.getnframes()
   rate = f.getframerate()
   chunk = int(rate*0.2) # fetch audio in 200ms chunks

   if args.debug:
       print("frames: {0} channels: {1}".format(numFrames, f.getnchannels()))
       print("width: {0} rate: {1} chuck size:{2}".format(f.getsampwidth(), rate, chunk))


   found = 0
   w=f.readframes(chunk)
   while len(w) >= chunk:
       audio_data=list(unpack(str(int(len(w)/2))+'h',w))
       audio_threshold=50
       tone_offset=0
       if max(audio_data) > 10 ** (audio_threshold / 10 * np.log10(32768) / 10):
           window = np.hamming(len(audio_data))
           audio_data = audio_data * window
           FFT = abs(np.fft.rfft(audio_data))
           lo_limit = int((300*len(FFT))/(rate/2))
           hi_limit = int((2800*len(FFT))/(rate/2))
           FFT[:lo_limit] = 0
           FFT[hi_limit:] = 0
           freq = rate / 2 * FFT.argmax() / len(FFT) * (1 + tone_offset)
           if args.debug:
               print("freq: {0:8.2f} len(FFT): {1} FFT.argmax: {2:>3d} lo_limit: {3} hi_limit: {4}"
                     .format(freq, len(FFT), FFT.argmax(), lo_limit, hi_limit))
               debugwriter.writerow(FFT[lo_limit:hi_limit])
           buffer.append(freq)
           buffer.pop(0)
           for tonedescription in ToneDict:
              tempbuffer = buffer[40 - len(ToneDict[tonedescription]):40]
              temp = abs(1 - array(tempbuffer) / ToneDict[tonedescription])
              temp1 = temp < 0.02
              temp2 = temp > 100000
              temp = operator.or_(temp1, temp2)
              if reduce(operator.and_, temp):
                 print(tonedescription)
                 found = 1
       w=f.readframes(chunk)

   if found == 0:
       print("UNKNOWN")
   f.close()
   if args.debug:
       debug.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Decode wav file with TwoTone signals.')
    parser.add_argument("filename", help="input wav file")
    parser.add_argument("-d", "--debug", help="debug mode", action="store_true")
    args = parser.parse_args()

    main(args)

