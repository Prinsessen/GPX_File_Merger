#!/usr/bin/env python3
"""
GPX File Merger - Merge multiple GPX files in chronological order.
This script combines track points from multiple GPX files, sorted by timestamp.
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime
from xml.etree import ElementTree as ET
from typing import List, Tuple


class GPXMerger:
    """Merge multiple GPX files chronologically."""

    GPX_NAMESPACE = "http://www.topografix.com/GPX/1/1"
    ET.register_namespace("", GPX_NAMESPACE)

    def __init__(self):
        """Initialize the GPX Merger."""
        self.track_points = []
        self.metadata = {}

    def parse_gpx_file(self, file_path: str) -> None:
        """
        Parse a GPX file and extract track points with timestamps.

        Args:
            file_path: Path to the GPX file

        Raises:
            FileNotFoundError: If the file doesn't exist
            ET.ParseError: If the file is not valid XML
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"GPX file not found: {file_path}")

        try:
            tree = ET.parse(file_path)
            root = tree.getroot()

            # Extract metadata from the first file
            if not self.metadata:
                self._extract_metadata(root)

            # Extract all track points (trkpt)
            self._extract_track_points(root, file_path)

        except ET.ParseError as e:
            raise ET.ParseError(f"Invalid GPX file '{file_path}': {e}")

    def _extract_metadata(self, root) -> None:
        """Extract metadata from GPX root element."""
        # Define namespace map for finding elements
        ns = {"gpx": self.GPX_NAMESPACE}

        metadata = root.find("gpx:metadata", ns)
        if metadata is not None:
            name = metadata.find("gpx:name", ns)
            if name is not None:
                self.metadata["name"] = name.text
            desc = metadata.find("gpx:desc", ns)
            if desc is not None:
                self.metadata["desc"] = desc.text

    def _extract_track_points(self, root, file_path: str) -> None:
        """Extract all track points from a GPX file."""
        ns = {"gpx": self.GPX_NAMESPACE}

        # Find all track points in tracks
        for trkpt in root.findall(".//gpx:trkpt", ns):
            time_elem = trkpt.find("gpx:time", ns)
            if time_elem is not None and time_elem.text:
                try:
                    # Parse ISO 8601 timestamp
                    timestamp = datetime.fromisoformat(
                        time_elem.text.replace("Z", "+00:00")
                    )
                    # Store both the element and its timestamp
                    self.track_points.append((timestamp, trkpt, file_path))
                except ValueError:
                    print(
                        f"Warning: Could not parse timestamp '{time_elem.text}' "
                        f"from {file_path}",
                        file=sys.stderr,
                    )

        # Also find waypoints (wpt)
        for wpt in root.findall(".//gpx:wpt", ns):
            time_elem = wpt.find("gpx:time", ns)
            if time_elem is not None and time_elem.text:
                try:
                    timestamp = datetime.fromisoformat(
                        time_elem.text.replace("Z", "+00:00")
                    )
                    self.track_points.append((timestamp, wpt, file_path))
                except ValueError:
                    print(
                        f"Warning: Could not parse timestamp '{time_elem.text}' "
                        f"from {file_path}",
                        file=sys.stderr,
                    )

    def sort_by_timestamp(self) -> None:
        """Sort all track points chronologically by timestamp."""
        self.track_points.sort(key=lambda x: x[0])

    def merge_to_file(self, output_path: str) -> None:
        """
        Write merged track points to a new GPX file.

        Args:
            output_path: Path where the merged GPX file will be saved
        """
        if not self.track_points:
            print("Error: No track points found to merge.", file=sys.stderr)
            return

        # Create a new GPX structure
        gpx = ET.Element("gpx")
        gpx.set("version", "1.1")
        gpx.set("creator", "GPX Merger Script")
        gpx.set("xmlns", self.GPX_NAMESPACE)

        # Add metadata
        metadata = ET.SubElement(gpx, "metadata")
        name = ET.SubElement(metadata, "name")
        name.text = self.metadata.get("name", "Merged GPX Track")
        desc = ET.SubElement(metadata, "desc")
        desc.text = self.metadata.get("desc", "Merged from multiple GPX files")
        time = ET.SubElement(metadata, "time")
        time.text = datetime.utcnow().isoformat() + "Z"

        # Create a single track with merged points
        trk = ET.SubElement(gpx, "trk")
        trk_name = ET.SubElement(trk, "name")
        trk_name.text = "Merged Track"

        trk_seg = ET.SubElement(trk, "trkseg")

        # Add all track points in chronological order
        for timestamp, point_elem, source_file in self.track_points:
            # Clone the element
            new_point = self._clone_element(point_elem)
            trk_seg.append(new_point)

        # Write to file
        tree = ET.ElementTree(gpx)
        tree.write(output_path, encoding="utf-8", xml_declaration=True)
        print(f"✓ Merged GPX file created: {output_path}")
        print(f"  Total track points merged: {len(self.track_points)}")

    @staticmethod
    def _clone_element(elem) -> ET.Element:
        """Create a deep copy of an XML element."""
        clone = ET.Element(elem.tag, elem.attrib)
        clone.text = elem.text
        clone.tail = elem.tail
        for child in elem:
            clone.append(GPXMerger._clone_element(child))
        return clone


def main():
    """Main function to handle command-line arguments and execute the merge."""
    parser = argparse.ArgumentParser(
        description="Merge multiple GPX files in chronological order based on timestamps.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python merge_gpx.py track1.gpx track2.gpx -o merged.gpx
  python merge_gpx.py *.gpx -o combined_track.gpx
        """,
    )

    parser.add_argument(
        "input_files",
        nargs="+",
        help="GPX files to merge (can use wildcards like *.gpx)",
    )
    parser.add_argument(
        "-o", "--output", default="merged.gpx", help="Output GPX file (default: merged.gpx)"
    )

    args = parser.parse_args()

    # Expand file paths
    input_files = []
    for pattern in args.input_files:
        matches = list(Path(".").glob(pattern))
        if matches:
            input_files.extend([str(f) for f in matches if f.is_file()])
        else:
            # Try as direct path
            if Path(pattern).is_file():
                input_files.append(pattern)

    if not input_files:
        print("Error: No valid GPX files found.", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(input_files)} GPX file(s) to merge:")
    for f in input_files:
        print(f"  - {f}")

    merger = GPXMerger()

    # Parse all GPX files
    for gpx_file in input_files:
        try:
            print(f"Processing: {gpx_file}")
            merger.parse_gpx_file(gpx_file)
        except (FileNotFoundError, ET.ParseError) as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    # Sort track points chronologically
    merger.sort_by_timestamp()

    # Write merged file
    merger.merge_to_file(args.output)


if __name__ == "__main__":
    main()
