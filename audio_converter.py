#!/usr/bin/env python3

import os
import argparse
import subprocess
from pathlib import Path

def convert_audio(source_file: Path, target_file: Path, sample_rate: int, bit_depth: int):
    """Convert audio file using ffmpeg with specified parameters"""
    target_file.parent.mkdir(parents=True, exist_ok=True)
    
    cmd = [
        'ffmpeg', '-y',  # -y to overwrite output files
        '-i', str(source_file),
        '-acodec', 'pcm_s16le',  # Force 16-bit output
        '-ar', str(sample_rate),  # Sample rate
        '-sample_fmt', f's{bit_depth}',  # Bit depth
        str(target_file)
    ]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"Error converting {source_file}: {e.stderr}")
        return False
    return True

def process_directory(source_dir: Path, target_dir: Path, sample_rate: int, bit_depth: int):
    """Recursively process all wav and aiff files in source directory"""
    audio_extensions = {'.wav', '.aiff', '.aif'}
    
    for source_file in source_dir.rglob('*'):
        if source_file.suffix.lower() in audio_extensions:
            # Create corresponding target path
            relative_path = source_file.relative_to(source_dir)
            target_file = target_dir / relative_path
            
            # Ensure target directory exists
            target_file.parent.mkdir(parents=True, exist_ok=True)
            
            print(f"Converting: {source_file}")
            if convert_audio(source_file, target_file, sample_rate, bit_depth):
                print(f"Successfully converted to: {target_file}")
            else:
                print(f"Failed to convert: {source_file}")

def main():
    parser = argparse.ArgumentParser(description='Convert audio files to specified format')
    parser.add_argument('source_dir', help='Source directory containing audio files')
    parser.add_argument('target_dir', help='Target directory for converted files')
    parser.add_argument('--sample-rate', type=int, default=44100,
                        help='Sample rate in Hz (default: 44100)')
    parser.add_argument('--bit-depth', type=int, default=16,
                        help='Bit depth (default: 16)')
    
    args = parser.parse_args()
    
    source_path = Path(args.source_dir).resolve()
    target_path = Path(args.target_dir).resolve()
    
    if not source_path.exists():
        print(f"Error: Source directory '{source_path}' does not exist")
        return
    
    print(f"Processing files from: {source_path}")
    print(f"Saving converted files to: {target_path}")
    print(f"Sample rate: {args.sample_rate} Hz")
    print(f"Bit depth: {args.bit_depth} bit")
    
    process_directory(source_path, target_path, args.sample_rate, args.bit_depth)

if __name__ == "__main__":
    main()
