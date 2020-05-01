# wave2ttd
Experiments in Two Tone decoding

This program couples with MULTIRX of any other program that can record
two tones pages to a wave file.

Theory of operation:

Build an array of the tone sequence to be detected in 200ms chunks. For example
a tone sequence of 400Hz x 1sec + 200Hz x 2 sec looks like:
[200,200,200,200,200,400,400,400,400,400,400,400,400,400,400]

Read the wav file in 200ms chunks (wav framerate * 0.2 bytes)

Pack the byte data into an array of shorts (16 bit) (so for now it only works on 16bit wavs)

Perform an FFT on the chunk, find the largest 'bin', calculate the frequency, and append that to a buffer. The buffer acts a a "sliding window" of the incoming wav. As we add values to the end, we delete values from the start and maintain a constant size buffer, in the current case the buffer is 40 values long or about 8 seconds.

Compare the saved tone sequence to the same number of values at the end of the buffer.
 
If we match, decalare success and print the detect tone. Otherwise loop and grab another wav sample and try again.

Continue until all of the frames in the wav file have ben consumed. If no tone sets were detected print "UNKNOWN"


