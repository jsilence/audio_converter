# Audio Converter

A command-line tool for batch converting audio files while maintaining directory structure. Automatically detects and converts identical stereo channels to mono.

## Features

- Converts WAV and AIFF files
- Maintains source directory structure in target directory
- Automatically detects and converts identical stereo channels to mono
- Configurable sample rate and bit depth
- Progress bar with real-time status
- Error handling and reporting

## Requirements

- Python 3.6+
- ffmpeg
- Required Python packages:
  - typer
  - rich

## Installation

1. Ensure ffmpeg is installed:
```bash
brew install ffmpeg  # macOS
```

2. Install Python dependencies:
```bash
pip install typer rich
```

## Usage

```bash
python audio_converter.py SOURCE_DIR TARGET_DIR [OPTIONS]
```

### Arguments

- `SOURCE_DIR`: Directory containing audio files to convert
- `TARGET_DIR`: Directory where converted files will be saved

### Options

- `--sample-rate`, `-sr`: Sample rate in Hz (default: 44100)
- `--bit-depth`, `-bd`: Bit depth (default: 16)

### Example

```bash
python audio_converter.py ~/Music/Originals ~/Music/Converted --sample-rate 48000 --bit-depth 24
```

## Features in Detail

### Directory Structure Preservation

The converter maintains the exact directory structure from the source directory in the target directory. For example:

```
Source/
  ├── Album1/
  │   ├── track1.wav
  │   └── track2.wav
  └── Album2/
      └── track3.wav
```

Will be converted to:

```
Target/
  ├── Album1/
  │   ├── track1.wav
  │   └── track2.wav
  └── Album2/
      └── track3.wav
```

### Automatic Mono Conversion

The script automatically detects when stereo channels are identical and converts such files to mono to save space while preserving audio quality.

### Progress Tracking

Real-time progress bar shows:
- Overall conversion progress
- Current file being processed
- Success/failure status for each file

## Error Handling

- Validates input and output directories
- Reports conversion failures
- Maintains progress even if individual files fail
- Creates target directories as needed

## License

MIT License
