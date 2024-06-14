import librosa
import numpy as np

# Load the audio file
file_path = './a.wav'
y, sr = librosa.load(file_path, sr=None)

# Calculate the number of samples per second
samples_per_second = sr

# Calculate the number of frames per second
hop_length = int(samples_per_second / (len(y) / sr))

# Calculate the duration of the audio in seconds
duration_in_seconds = int(librosa.get_duration(y=y, sr=sr))

loudness_per_second = []

for i in range(duration_in_seconds):
    # Extract 1-second chunk of the audio
    start_sample = i * samples_per_second
    end_sample = start_sample + samples_per_second
    y_chunk = y[start_sample:end_sample]
    
    # Perform Short-Time Fourier Transform (STFT) on the chunk
    S = np.abs(librosa.stft(y_chunk, hop_length=hop_length))
    
    # Calculate the power spectrum of the chunk
    power = np.square(S)
    
    # Calculate the average power for the chunk
    avg_power = np.mean(power)
    
    # Convert to decibels
    loudness_db = 10 * np.log10(avg_power)
    
    loudness_per_second.append(loudness_db)

# Print the results
for i, db in enumerate(loudness_per_second):
    print(f"Second {i+1}: {db} dB")