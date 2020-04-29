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
import csv

def main(file):
   ToneDict = defaultdict(list)
   buffer = [0] * 40

   with open('tones.csv') as csvfile:
      tonereader = csv.reader(csvfile, delimiter=',')
      for row in tonereader:
         ttemp = [float(row[1])] * int(round(float(row[2]) / 0.2)) + [float(row[3])] * int(round(float(row[4]) / 0.2))
         ToneDict[row[0]] = array(ttemp)

   f=wave.open(file,'rb')
   numFrames=f.getnframes()
   #print(f"frames: {numFrames}")
   #print(f"channels: {f.getnchannels()}")
   #print(f"width: {f.getsampwidth()}")
   rate=f.getframerate()
   #print(f"rate: {rate}")

   # fetch audio in 200ms chunks
   chunk=int(rate*0.2)
   #print(f"chunk size: {chunk}")

   found = 0
   w=f.readframes(chunk)
   while len(w) > 0:
       audio_data=list(unpack(str(int(len(w)/2))+'h',w))
       audio_threshold=50
       tone_offset=0
       if max(audio_data) > 10 ** (audio_threshold / 10 * np.log10(32768) / 10):
           window = np.hamming(len(audio_data))
           audio_data = audio_data * window
           FFT = abs(np.fft.rfft(audio_data))
           FFT[:46] = 0
           FFT[559:] = 0
           freq = rate / 2 * FFT.argmax() / len(FFT) * (1 + tone_offset)
           print(f"freq: {freq}")
           buffer.append(freq)
           buffer.pop(0)
           for tonedescription in ToneDict:
              tempbuffer = buffer[40 - len(ToneDict[tonedescription]):40]
              temp = abs(1 - array(tempbuffer) / ToneDict[tonedescription])
              temp1 = temp < 0.02
              temp2 = temp > 100000
              temp = operator.or_(temp1, temp2)
              if reduce(operator.and_, temp):
                 print(f"{tonedescription}")
                 found = 1
       w=f.readframes(chunk)
   if found == 0:
       print("UNKNOWN")
   f.close()

if __name__ == "__main__":
    main(sys.argv[1])

