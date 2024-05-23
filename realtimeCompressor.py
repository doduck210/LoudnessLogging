import pyaudio
import numpy as np

# Compressor parameters
threshold = -20.0   # Threshold (dB)
ratio = 4.0         # Ratio
attack = 0.01       # Attack time (seconds)
release = 0.1       # Release time (seconds)
sample_rate = 44100

# Function to convert dB to linear value
def db_to_linear(db):
    return 10 ** (db / 20)

# Function to convert linear value to dB
def linear_to_db(linear):
    return 20 * np.log10(linear)

# Function to apply compressor
def apply_compressor(input_signal, threshold, ratio, attack, release, sample_rate):
    output_signal = np.copy(input_signal)
    threshold_linear = db_to_linear(threshold)
    attack_coeff = np.exp(-1.0 / (sample_rate * attack))
    release_coeff = np.exp(-1.0 / (sample_rate * release))
    envelope = 0.0

    for i in range(len(input_signal)):
        input_level = np.abs(input_signal[i])
        if input_level > envelope:
            envelope = attack_coeff * (envelope - input_level) + input_level
        else:
            envelope = release_coeff * (envelope - input_level) + input_level

        if envelope > threshold_linear:
            gain = threshold_linear + (envelope - threshold_linear) / ratio
        else:
            gain = envelope
        
        output_signal[i] = input_signal[i] * gain / (envelope + 1e-6)

    return output_signal

# Audio callback function
def callback(in_data, frame_count, time_info, status):
    # Convert input audio data to numpy array
    input_signal = np.frombuffer(in_data, dtype=np.float32)

    # Apply compressor
    output_signal = apply_compressor(input_signal, threshold, ratio, attack, release, sample_rate)

    # Convert output audio data to bytes
    out_data = output_signal.astype(np.float32).tobytes()

    return (out_data, pyaudio.paContinue)

# PyAudio setup
p = pyaudio.PyAudio()
channels = 1
format = pyaudio.paFloat32
frames_per_buffer = 1024

# Open stream
stream = p.open(format=format,
                channels=channels,
                rate=sample_rate,
                input=True,
                output=True,
                frames_per_buffer=frames_per_buffer,
                stream_callback=callback)

# Start stream
stream.start_stream()

print("Streaming audio with compression applied. Press Ctrl+C to stop.")

# Wait until stream is stopped
try:
    while stream.is_active():
        pass
except KeyboardInterrupt:
    pass

# Stop and close stream, terminate PyAudio
stream.stop_stream()
stream.close()
p.terminate()
print("Stream stopped.")