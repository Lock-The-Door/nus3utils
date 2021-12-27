import sys
import wave
filePath = sys.argv[1]
audio = wave.open(filePath, 'rb')
samples = audio.getnframes()
print(samples)