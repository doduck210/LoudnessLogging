import pyloudnorm as pyln
import soundfile as sf

def getLoudness(file):
    data, rate = sf.read(file) #data.shape : (길이, 채널수) 
    meter = pyln.Meter(rate)
    loudness = meter.integrated_loudness(data)
    return loudness