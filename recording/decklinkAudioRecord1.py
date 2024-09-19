import gi, queue, threading, time, wave, os
import numpy as np

#   Decklink audio endless recorder by sendust
#   for SBS loudness monitor...
#   2024/8/2
#
#
#


gi.require_version("Gst", "1.0")

from gi.repository import Gst, GObject

#  https://gist.github.com/orig74/de52f3a85924eadee3d3a84d9e164f47

decklinkIdx = "1"
savingPath="/mnt/raid/video/SBS_HD" #os.getcwd()

def get_buffer(name):
    global pipeline
    sink = pipeline.get_by_name(name)
    pad = sink.pads[0]
    caps=pad.get_current_caps()
    struct=caps.get_structure(0)
    #print(struct)
    rate = struct.get_int('rate')[1]
    format =  struct.get_string('format')
    channels = struct.get_int('channels')[1]
    layout = struct.get_string('layout')
    #print(rate, format, channels, layout)
    
    sample = sink.emit('pull-sample') 
    buf = sample.get_buffer()
    mem = buf.get_all_memory()
    ret, mi = mem.map(Gst.MapFlags.READ)
    #print(mem)
    wavenp = np.frombuffer(mi.data, 'int32')  # Decklink audio, S32LE
    wavenp16 = (wavenp >> 16).astype('int16')
    #print(wavenp16[:8])     # Shows First 8 channel audio data
    print("%6d | %6d | %6d | %6d | %6d | %6d | %6d | %6d " % (wavenp16[0], wavenp16[1], wavenp16[2], wavenp16[3], wavenp16[4], wavenp16[5], wavenp16[6], wavenp16[7]), end="\r")
    #print(np.sqrt(np.mean(wave**2)))
    mi.memory.unmap(mi)
    return wavenp16
    


def on_new_buffer(sink):
    global q
    #print(f'{sink}  arrived..')
    q.put(get_buffer("audiosink"))
    return Gst.FlowReturn.OK


def queue_write():
    global q, q_flush, wa
    q_flush = False
    #print('save queue...')
    result = q.get()
    while q.qsize():
        result = np.concatenate((result, q.get()))
    #print(f'result size = {len(result)}')
    wa.write_wave(result)
    q_flush = True


class wave_append_writer:

    def __init__(self, meta = (2, 8, 48000)):       # 2 byte, 8 channel, 48kHz
        self.str_tick = "00"
        self.str_tick_prev = self.str_tick
        self.filename = ''
        self.meta = meta
        self.pt_wave = ''
    
    def update_tick(self, tick):
        self.str_tick_prev = self.str_tick
        self.str_tick = tick
        
        if not self.pt_wave:
            self.prepare_pt_wave()
            print("Create new wave file..  ", self.filename)
            
        if ((self.str_tick_prev == "59") and (self.str_tick == "00")):
            if self.pt_wave:
                self.pt_wave.close() 
                print(f'close wave file.. {self.filename}')
            self.prepare_pt_wave()
            print(f'file name changed.. {self.filename}')
            
            
    def prepare_pt_wave(self):
        name_file =  os.path.join(savingPath, time.strftime("%Y-%m-%d_%H.%M.%S") + ".wav")
        
        self.filename = name_file
        print(name_file)
        self.pt_wave = wave.open(self.filename, 'wb')
        self.pt_wave.setsampwidth(self.meta[0])
        self.pt_wave.setnchannels(self.meta[1])
        self.pt_wave.setframerate(self.meta[2])

    def write_wave(self, buffer):       # Must call after update_tick
        self.pt_wave.writeframes(buffer.tobytes())
        #print("write frames....")
        
        
    def close_wave(self):
        self.pt_wave.close() 

q = queue.Queue()
q_flush = True


wa = wave_append_writer((2, 8, 48000))
wa.update_tick(time.strftime("%M"))

pipe = "decklinkvideosrc device-number=" + decklinkIdx + " ! fakesink decklinkaudiosrc device-number="+ decklinkIdx +" channels=8 ! appsink name=audiosink"
Gst.init()
pipeline = Gst.parse_launch(pipe)

sink=pipeline.get_by_name('audiosink')
#sink.set_property("max-buffers",100)
sink.set_property("emit-signals", True)

sink.connect("new-sample", on_new_buffer) 

pipeline.set_state(Gst.State.READY)
pipeline.set_state(Gst.State.PLAYING)


bus = pipeline.get_bus()
message = bus.timed_pop_filtered(5*Gst.MSECOND,Gst.MessageType.ANY)


try:
    while True:
        #print('qsize = ', q.qsize(), end="\r", flush=True)
        if (message.type != Gst.MessageType.STATE_CHANGED):
            print(message.type, message.src)
        wa.update_tick(time.strftime("%M"))
        if q.qsize():
            queue_write()
        time.sleep(0.01)

except KeyboardInterrupt:
    print("keyboard interrupt..")