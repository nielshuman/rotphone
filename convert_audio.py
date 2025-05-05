import os
import subprocess

def convert_audio(input_dir, output_dir):
    for file in os.listdir(input_dir):
        filename = os.path.splitext(file)[0]
        if os.path.exists(os.path.join(output_dir, f'{filename}.wav')):
            continue
        
        command = [
            'ffmpeg',
            '-i', os.path.join(input_dir, file),
            '-ac', '1',
            '-sample_fmt', 's16',
            os.path.join(output_dir, f'{filename}.wav')
        ]
        
        print(f'Converting {file} to {filename}.wav')
        subprocess.run(command, check=True)