# GPX File Merger

A Python utility to merge multiple GPX (GPS Exchange Format) files into a single file, with all track points sorted chronologically by timestamp. Perfect for combining GPS tracks from multiple devices or recording sessions into one continuous timeline.

## Features

- ✅ **Chronological Sorting**: Automatically sorts all track points by timestamp across multiple files
- ✅ **Multi-file Support**: Merge 2, 3, or hundreds of GPX files at once
- ✅ **Flexible Input**: Use individual file paths or wildcard patterns (e.g., `*.gpx`)
- ✅ **Preserves Data**: Maintains all point attributes (latitude, longitude, elevation, timestamps, etc.)
- ✅ **Standard Format**: Outputs valid GPX 1.1 format compatible with all GPX readers
- ✅ **No Dependencies**: Uses only Python standard library - no external packages required
- ✅ **Error Handling**: Validates files and provides helpful error messages

## Installation

### Requirements
- Python 3.6 or higher

### Setup

1. Clone the repository:
```bash
git clone https://github.com/Prinsessen/GPX_File_Merger.git
cd GPX_File_Merger
```

2. No dependencies to install! The script uses only Python's standard library.

## Usage

### Command Line

#### Merge specific files:
```bash
python merge_gpx.py track1.gpx track2.gpx -o merged.gpx
```

#### Merge all GPX files in current directory:
```bash
python merge_gpx.py *.gpx -o combined_track.gpx
```

#### Use default output filename (merged.gpx):
```bash
python merge_gpx.py file1.gpx file2.gpx file3.gpx
```

#### View help:
```bash
python merge_gpx.py --help
```

### Command Line Arguments

- `input_files` - One or more GPX files to merge (required). Supports:
  - Individual files: `track1.gpx track2.gpx`
  - Wildcard patterns: `*.gpx` or `**/subfolder/*.gpx`

- `-o, --output` - Output filename (optional, default: `merged.gpx`)

### Programmatic Usage

Import the `GPXMerger` class to use it in your own Python code:

```python
from merge_gpx import GPXMerger

# Create merger instance
merger = GPXMerger()

# Add GPX files
merger.parse_gpx_file('track1.gpx')
merger.parse_gpx_file('track2.gpx')
merger.parse_gpx_file('track3.gpx')

# Sort chronologically
merger.sort_by_timestamp()

# Save merged file
merger.merge_to_file('merged_output.gpx')
```

See `example_usage.py` for a complete example.

## How It Works

1. **Parsing**: Reads and parses all input GPX files
2. **Extraction**: Extracts all track points (`<trkpt>`) and waypoints (`<wpt>`) with timestamps
3. **Sorting**: Sorts all points chronologically by their timestamp (ISO 8601 format)
4. **Merging**: Creates a single GPX file with all points in time order
5. **Output**: Generates a valid GPX 1.1 file with proper structure and metadata

## Example

### Input Files:
- `morning_run.gpx` - 10:00 AM to 10:30 AM
- `evening_run.gpx` - 5:00 PM to 5:45 PM

### Command:
```bash
python merge_gpx.py morning_run.gpx evening_run.gpx -o combined_run.gpx
```

### Output:
A single `combined_run.gpx` file with:
- All morning track points (10:00-10:30 AM)
- All evening track points (5:00-5:45 PM)
- Points properly ordered chronologically even though they came from different files

## Supported GPX Elements

The merger handles:
- **Track Points** (`<trkpt>`) - Points within tracks
- **Waypoints** (`<wpt>`) - Standalone waypoints
- **Attributes**: Preserves latitude, longitude, elevation, timestamps, and any other point attributes

## Output

The merged GPX file includes:
- Merged metadata from the first input file
- Current UTC timestamp in the metadata
- Single track segment containing all sorted points
- Valid GPX 1.1 XML structure

## Troubleshooting

### No track points found
- Ensure your GPX files contain points with `<time>` elements
- Check that timestamps are in valid ISO 8601 format (e.g., `2025-01-03T10:30:45Z`)

### Files not found with wildcard
- Ensure you're running the command from the directory containing the GPX files
- Try using explicit file paths instead

### Invalid timestamp warning
- This is non-fatal - points without valid timestamps are skipped
- Check your GPX file format

## File Structure

```
GPX_File_Merger/
├── README.md              # This file
├── merge_gpx.py           # Main script
├── example_usage.py       # Usage example
└── requirements.txt       # Dependencies (none)
```

## License

MIT License - Feel free to use and modify as needed.

## Contributing

Contributions are welcome! Feel free to:
- Report issues
- Suggest improvements
- Submit pull requests

## Author

Created by Prinsessen