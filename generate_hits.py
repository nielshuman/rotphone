import librosa
import soundfile as sf
import os

# Load the original audio (G note)
input_file = 'marimba_hit_G.wav'
y, sr = librosa.load(input_file)

# Notes in G Major scale: 5 below and 5 above G
notes = {
    'B_low': -11,
    'C': -10,
    'D': -8,
    'E': -7,
    'F#': -5,
    'G': 0,
    'A': 2,
    'B': 4,
    'C_high': 5,
    'D_high': 7,
    'E_high': 9
}

# Output directory
os.makedirs("g_major_full_range", exist_ok=True)

# Generate and save shifted audio files
for note, semitone_shift in notes.items():
    y_shifted = librosa.effects.pitch_shift(y, sr=sr, n_steps=semitone_shift, res_type='soxr_vhq')
    output_path = f"g_major_full_range/marimba_hit_{note}.wav"
    sf.write(output_path, y_shifted, sr)
    print(f"Saved {output_path}")
