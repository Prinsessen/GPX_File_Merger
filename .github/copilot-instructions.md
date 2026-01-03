# AI Coding Agent Instructions for GPX File Merger

## Project Overview

**GPX File Merger** is a lightweight Python utility that merges multiple GPS exchange format (GPX) files into a single chronologically sorted file. It has **zero external dependencies** (uses only Python standard library).

Core functionality: Parse GPX XML → Extract track/waypoints → Sort by ISO 8601 timestamp → Output merged GPX 1.1

## Architecture

### Key Components

- **`GPXMerger` class** ([merge_gpx.py](merge_gpx.py#L15)): Central orchestrator
  - `parse_gpx_file()`: Reads and parses individual GPX files using `ElementTree`
  - `_extract_track_points()`: Extracts `<trkpt>` and `<wpt>` elements with timestamp validation
  - `sort_by_timestamp()`: Sorts accumulated points by parsed `datetime` objects
  - `merge_to_file()`: Constructs new GPX 1.1 XML tree and writes output

- **CLI entry point** ([merge_gpx.py](merge_gpx.py#L179)): `main()` function handles argparse with glob pattern expansion via `Path.glob()`

- **Example client** ([example_usage.py](example_usage.py)): Demonstrates programmatic API usage

### Data Flow

1. Parse → accumulate tuples of `(timestamp, elem, source_file)` in `self.track_points`
2. Sort → in-place sort by timestamp (first element of tuple)
3. Merge → clone elements into new GPX structure with single track/trkseg
4. Output → UTF-8 XML with ISO 8601 metadata timestamp

## Critical Patterns & Conventions

### XML Namespace Handling

GPX files use the namespace `http://www.topografix.com/GPX/1/1`. Always register and query with namespace prefix:
```python
ns = {"gpx": GPXMerger.GPX_NAMESPACE}
root.findall(".//gpx:trkpt", ns)  # Not findall(".//trkpt")
```

### Timestamp Parsing

ISO 8601 format with timezone handling:
```python
timestamp = datetime.fromisoformat(time_elem.text.replace("Z", "+00:00"))
```
Invalid timestamps are non-fatal—print warnings to stderr and skip the point.

### Element Cloning

Deep recursion required to preserve nested XML structure: `_clone_element()` recursively copies tag, attributes, text, tail, and children (no `copy` module—manual recursion).

### File Pattern Expansion

Use `Path.glob()` for wildcard patterns (`*.gpx`), then fall back to direct path for non-match files:
```python
matches = list(Path(".").glob(pattern))
if matches:
    input_files.extend([str(f) for f in matches if f.is_file()])
else:
    if Path(pattern).is_file():
        input_files.append(pattern)
```

## Testing & Validation

- **No test suite exists**—add tests when implementing features
- **Manual validation**: Create sample `.gpx` files with timestamp variations and verify merged output order
- **Edge cases to consider**: Mixed timezone timestamps, missing `<time>` elements, empty files, invalid XML

## Common Tasks

### Adding GPX Element Support
Find `_extract_track_points()` and `merge_to_file()`. Current scope: `<trkpt>` and `<wpt>` only. Any new element type needs timestamp extraction and cloning logic.

### Modifying Output Format
The output GPX structure is built in `merge_to_file()` (lines 136–161). Metadata comes from the first parsed file; adjust `self.metadata` extraction in `_extract_metadata()` as needed.

### Improving Error Handling
Errors are raised from `parse_gpx_file()` and caught in `main()`. Validation logic for file existence and XML parsing is in place; enhance with more granular error codes if needed.

## Quick Commands

```bash
# CLI usage
python merge_gpx.py track1.gpx track2.gpx -o output.gpx
python merge_gpx.py *.gpx  # Uses default output: merged.gpx

# Programmatic usage
from merge_gpx import GPXMerger
merger = GPXMerger()
merger.parse_gpx_file("file.gpx")
merger.sort_by_timestamp()
merger.merge_to_file("out.gpx")
```

## Validation & Error Scenarios

### GPX File Validation Patterns

When enhancing validation, reference these patterns:

**ISO 8601 Timestamp Format**:
```python
import re
iso_8601_pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$'
# Valid: 2025-01-03T10:30:45Z, 2025-01-03T10:30:45.123Z, 2025-01-03T10:30:45+00:00
```

**Latitude/Longitude Validation**:
```python
def validate_coordinates(lat, lon):
    try:
        lat_f, lon_f = float(lat), float(lon)
        return -90 <= lat_f <= 90 and -180 <= lon_f <= 180
    except (ValueError, TypeError):
        return False
```

### Common Error Scenarios

| Scenario | Handling | Example |
|----------|----------|---------|
| Missing `<time>` element | Non-fatal; skip point with stderr warning | `Warning: Could not parse timestamp...` |
| Invalid XML structure | Catch `ET.ParseError`, exit with status 1 | Mismatched tags, encoding issues |
| No matching files from glob | Check if `Path.glob()` returns empty list, try direct path | `*.gpx` pattern matches nothing |
| Empty `self.track_points` after parsing | Print error message and return early from `merge_to_file()` | All files parsed but no valid points |
| Mixed timezone formats | `fromisoformat()` with `replace("Z", "+00:00")` handles both | `2025-01-03T10:30:45Z` vs `+00:00` |

## Dependencies & Environment

- **Python 3.6+** (no external packages)
- **Standard library only**: `argparse`, `pathlib`, `datetime`, `xml.etree.ElementTree`
- No virtual environment needed; can run directly
