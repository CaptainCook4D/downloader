import argparse
import json
from collections import Counter
from pathlib import Path

from util import (
	ALL_STREAMS,
	Constants,
	DATA_3D_STREAMS,
	HOLOLENS_STREAMS,
	STREAM_GROUPS,
	download_data,
	plan_hololens_downloads,
	resolve_streams,
)


# Please note that not all videos are recorded with hololens.
# Roughly, 60 videos are recorded only with GoPro, and they do not have hololens components.
# Due to device instability, roughly additional 40 videos don't have spatial data that includes Pose, 3D Hand Data


def parse_recording_ids(args):
	if args.recordings:
		return {recording_id.strip() for recording_id in args.recordings.split(",") if recording_id.strip()}
	if args.recordings_file:
		with open(args.recordings_file, "r") as recordings_file:
			return {line.strip() for line in recordings_file if line.strip()}
	return None


def select_streams(args):
	if args.streams:
		return resolve_streams([name.strip() for name in args.streams.split(",") if name.strip()])
	if args.all:
		return list(ALL_STREAMS)
	if args.data3d:
		return list(DATA_3D_STREAMS)
	return None


def process_download_hololens_3d_data(download_args):
	streams = select_streams(download_args)
	if not streams:
		print("Nothing selected. Pass --data3d, --all, or --streams <names>.")
		print(f"Available streams: {', '.join(ALL_STREAMS)}")
		print(f"Available groups : {', '.join(STREAM_GROUPS)}")
		return

	variants = []
	if download_args.sync:
		variants.append(Constants.SYNC)
	if download_args.raw:
		variants.append(Constants.RAW)
	if not variants:
		variants = [Constants.SYNC]

	# ---- Parse Download Links Json ----
	with open(download_args.links, "r") as f:
		download_links = json.load(f)

	output_dir = Path(download_args.output_dir)
	data_directory = output_dir / Constants.CAPTAIN_COOK_4D

	recording_ids = parse_recording_ids(download_args)
	download_url_links, download_file_paths, skipped = plan_hololens_downloads(
		download_links, streams, variants, data_directory, recording_ids
	)

	print("-------------------------------------------------")
	print(f"Variants : {', '.join(variants)}")
	print(f"Streams  : {', '.join(streams)}")
	print(f"Files to download : {len(download_url_links)}")

	if skipped:
		reasons = Counter(f"{variant}/{stream}" for _, variant, stream, _ in skipped)
		print(f"Unavailable       : {len(skipped)} (recording/stream combinations with no data)")
		for label, count in sorted(reasons.items(), key=lambda kv: (-kv[1], kv[0])):
			print(f"    {count:5d}  {label}")

	if download_args.dry_run:
		print("-------------------------------------------------")
		print("Dry run, nothing downloaded. Sample of what would be fetched:")
		for url, path in list(zip(download_url_links, download_file_paths))[:10]:
			print(f"  {path}  <-  {url}")
		return

	if not download_url_links:
		print("No files matched the selection, nothing to download.")
		return

	print("-------------------------------------------------")
	download_data(download_url_links, download_file_paths)


if __name__ == "__main__":
	print("Starting the download process")

	parser = argparse.ArgumentParser(
		description="Download 3D Hololens data from BOX Cloud",
		formatter_class=argparse.RawDescriptionHelpFormatter,
		epilog=(
			"Streams: " + ", ".join(ALL_STREAMS) + "\n"
			"Groups : " + ", ".join(f"{name} ({'+'.join(members)})" for name, members in STREAM_GROUPS.items())
		)
	)

	parser.add_argument('--data3d', action='store_true',
	                    help='Download the 3D streams: depth, ab, depth pose, spatial and imu')
	parser.add_argument('--all', action='store_true',
	                    help='Download every Hololens stream, including the pv video and frames')
	parser.add_argument('--streams', type=str, default=None,
	                    help='Comma separated list of streams or groups to download, e.g. depth,imu')

	parser.add_argument('--sync', action='store_true',
	                    help='Download the sync variant, time aligned with the GoPro video (default)')
	parser.add_argument('--raw', action='store_true',
	                    help='Download the raw variant, straight off the device')

	parser.add_argument('--recordings', type=str, default=None,
	                    help='Comma separated recording ids to restrict the download to, e.g. 1_10,2_38')
	parser.add_argument('--recordings_file', type=str, default=None,
	                    help='File with one recording id per line to restrict the download to')

	parser.add_argument('--links', type=str, default="metadata/download_links.json",
	                    help='Download links json to read')
	parser.add_argument('--output_dir', type=str, default="data",
	                    help='Output directory to store the downloaded data')
	parser.add_argument('--dry_run', action='store_true',
	                    help='List what would be downloaded without fetching anything')

	args = parser.parse_args()

	process_download_hololens_3d_data(args)
