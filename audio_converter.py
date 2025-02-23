#!/usr/bin/env python3

import os
import subprocess
import json
from pathlib import Path
import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich import print as rprint

# Initialize rich console
console = Console()

def has_identical_channels(file_path: Path) -> bool:
    """Check if stereo audio file has identical channels"""
    cmd = [
        'ffprobe',
        '-i', str(file_path),
        '-select_streams', 'a:0',
        '-show_entries', 'stream=channels',
        '-v', 'quiet',
        '-of', 'json'
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        audio_info = json.loads(result.stdout)
        channels = int(audio_info['streams'][0]['channels'])
        
        if channels != 2:  # If not stereo, return False
            return False
            
        # Now check if channels are identical using ffmpeg
        check_cmd = [
            'ffmpeg',
            '-i', str(file_path),
            '-af', 'channelcompare',  # Compare channels
            '-f', 'null',
            '-'
        ]
        
        result = subprocess.run(check_cmd, capture_output=True, text=True, encoding='latin-1', errors='ignore')
        # If channels are different, ffmpeg will output warnings
        return 'difference' not in result.stderr.lower()
        
    except (subprocess.CalledProcessError, json.JSONDecodeError, KeyError):
        return False

def convert_audio(source_file: Path, target_file: Path, sample_rate: int, bit_depth: int):
    """Convert audio file using ffmpeg with specified parameters"""
    target_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Check if we should convert to mono
    should_mono = has_identical_channels(source_file)
    
    cmd = [
        'ffmpeg', '-y',  # -y to overwrite output files
        '-i', str(source_file),
        '-acodec', 'pcm_s16le',  # Force 16-bit output
        '-ar', str(sample_rate),  # Sample rate
        '-sample_fmt', f's{bit_depth}'  # Bit depth
    ]
    
    # Add mono conversion if needed
    if should_mono:
        cmd.extend(['-ac', '1'])
        print(f"Converting to mono as channels are identical")
    
    cmd.append(str(target_file))
    
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True, encoding='latin-1', errors='ignore')
    except subprocess.CalledProcessError as e:
        print(f"Error converting {source_file}: {e.stderr}")
        return False
    return True

def process_directory(source_dir: Path, target_dir: Path, sample_rate: int, bit_depth: int):
    """Recursively process all wav and aiff files in source directory"""
    audio_extensions = {'.wav', '.aiff', '.aif'}
    
    # Get list of files first
    audio_files = [f for f in source_dir.rglob('*') if f.suffix.lower() in audio_extensions]
    
    if not audio_files:
        console.print("[yellow]No audio files found in the source directory.[/yellow]")
        return

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    ) as progress:
        task = progress.add_task("[cyan]Converting audio files...", total=len(audio_files))
        
        for source_file in audio_files:
            progress.update(task, description=f"[cyan]Converting: {source_file.name}")
            
            # Create corresponding target path
            relative_path = source_file.relative_to(source_dir)
            target_file = target_dir / relative_path
            
            # Ensure target directory exists
            target_file.parent.mkdir(parents=True, exist_ok=True)
            
            if convert_audio(source_file, target_file, sample_rate, bit_depth):
                console.print(f"[green]✓[/green] Converted: {source_file.name}")
            else:
                console.print(f"[red]✗[/red] Failed to convert: {source_file.name}")
            
            progress.advance(task)

def main(
    source_dir: Path = typer.Argument(..., help="Source directory containing audio files", exists=True, dir_okay=True, file_okay=False),
    target_dir: Path = typer.Argument(..., help="Target directory for converted files"),
    sample_rate: int = typer.Option(44100, "--sample-rate", "-sr", help="Sample rate in Hz"),
    bit_depth: int = typer.Option(16, "--bit-depth", "-bd", help="Bit depth"),
):
    """
    Convert audio files to specified format while maintaining directory structure.
    Supports WAV and AIFF files. Automatically converts identical stereo channels to mono.
    """
    source_path = source_dir.resolve()
    target_path = target_dir.resolve()
    
    console.print("\n[bold cyan]Audio Converter[/bold cyan]")
    console.print(f"[white]Source directory:[/white] [yellow]{source_path}[/yellow]")
    console.print(f"[white]Target directory:[/white] [yellow]{target_path}[/yellow]")
    console.print(f"[white]Sample rate:[/white] [green]{sample_rate}[/green] Hz")
    console.print(f"[white]Bit depth:[/white] [green]{bit_depth}[/green] bit\n")
    
    process_directory(source_path, target_path, sample_rate, bit_depth)
    
    console.print("\n[bold green]Conversion complete![/bold green]")

if __name__ == "__main__":
    typer.run(main)
