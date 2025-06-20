# Audio Duration Compare

This script compares the durations of audiobook files between two folders (Proofing and Master) to identify discrepancies.

## Features

- Select first audio file in each folder via GUI file picker.
- Matches files sequentially based on chapter numbers in filenames.
- Uses `ffprobe` to measure audio durations.
- Outputs a CSV report showing durations and differences.
- Flags duration mismatches greater than 6 seconds.
- Terminal progress bar during processing.

## Requirements

- Python 3
- `ffprobe` installed and in PATH (part of FFmpeg)
- Python package `tqdm` for progress bar:  
