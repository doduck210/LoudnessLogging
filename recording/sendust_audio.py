import pyaudio, time, queue, threading
import wave, math, struct

SHORT_NORMALIZE = (1.0/32768.0)
FRAMES_PER_SECOND = 48000


q = queue.Queue()


def get_rms(block):
    # RMS amplitude is defined as the square root of the 
    # mean over time of the square of the amplitude.
    # so we need to convert this string of bytes into 
    # a string of 16-bit samples...
    # we will get one short out for each 
    # two chars in the string.
    count = len(block)/2
    format = "%dh"%(count)
    shorts = struct.unpack( format, block )

    # iterate over the block.
    sum_squares = 0.0
    for sample in shorts:
        # sample is a signed short in +/- 32768. 
        # normalize it to 1.0
        n = sample * SHORT_NORMALIZE
        sum_squares += n*n

    return math.sqrt( sum_squares / count )
    

def write_wave(stereo_frames):
    with wave.open(f'{time.strftime("audio_%H%M%S")}.wav', mode="wb") as wav_file:
        wav_file.setnchannels(2)
        wav_file.setsampwidth(2)
        wav_file.setframerate(FRAMES_PER_SECOND)
        wav_file.writeframes(stereo_frames)


    
def cb_audio_backup(in_data, frame_count, time_info, status_flags):
    global q
    #q.put(in_data)
    #print(f'{time_info}           ',  end="\r", flush=True)
    rms = get_rms(in_data)
    #print(in_data, frame_count)
    print(int(rms * 500) *  '|', flush=True)
    return (None, pyaudio.paContinue)
    

def thread_write():
    global q
    b = bytearray()
    while q.qsize() > 5:
        b.extend(q.get())
    print('Finish File write')
    write_wave(b)



    
def cb_audio(in_data, frame_count, time_info, status_flags):
    global q
    #print(time_info, end="\r")
    q.put(in_data)
    rms = get_rms(in_data)
    print(" " * 100, end="\r")
    print(int(rms * 500) *  '|', end="\r", flush=True)
    if (q.qsize() == 4000):
        threading.Thread(target=thread_write).start()
    return (None, pyaudio.paContinue)
    
    
    
probe = pyaudio.PyAudio()


for each in range(probe.get_device_count()):
    device = probe.get_device_info_by_index(each)
    print(device)
    
device_index = int(input("Select audio device number   "))

format = probe.get_format_from_width(2, False)  # 2 byte, unsigned = True
stream = probe.open(rate=FRAMES_PER_SECOND, channels=2,  format=format, input=True, output=False, input_device_index=device_index, stream_callback =cb_audio)




try:
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    pass