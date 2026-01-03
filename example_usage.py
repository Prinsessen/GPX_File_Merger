#!/usr/bin/env python3
"""
Example usage of the GPX File Merger script.
This demonstrates how to use the GPXMerger class programmatically.
"""

from merge_gpx import GPXMerger


def example_merge():
    """Example: Merge GPX files from a list."""
    # Create merger instance
    merger = GPXMerger()

    # Add GPX files to merge (in any order)
    gpx_files = [
        "track1.gpx",
        "track2.gpx",
        "track3.gpx",
    ]

    # Parse all files
    for gpx_file in gpx_files:
        try:
            merger.parse_gpx_file(gpx_file)
            print(f"Loaded: {gpx_file}")
        except FileNotFoundError:
            print(f"File not found: {gpx_file}")
        except Exception as e:
            print(f"Error loading {gpx_file}: {e}")

    # Sort chronologically
    merger.sort_by_timestamp()

    # Save merged file
    merger.merge_to_file("merged_output.gpx")


if __name__ == "__main__":
    example_merge()
