import os
import subprocess

def convert_audio(dirname):
    for file in os.listdir(dirname):
        if not file.startswith('_'):
            continue
        
        filename = os.path.splitext(file)[0][1:] # Remove leading underscore
        
        if os.path.exists(os.path.join(dirname, f'{filename}.wav')): # Check if the file already exists
            continue
        
        command = [
            'ffmpeg',
            '-i', os.path.join(dirname, file),
            '-ac', '1',
            '-sample_fmt', 's16',
            os.path.join(dirname, f'{filename}.wav')
        ]
        
        print(f'Converting {file} to {filename}.wav')
        subprocess.run(command, check=True)