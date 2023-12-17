import argparse
import json
from pathlib import Path

from util import prepare_hololens_2d_output_directory, Constants, download_data


# Please note that not all videos are recorded with hololens.
# Roughly, 60 videos are recorded only with GoPro, and they do not have hololens components.
# Due to device instability, roughly additional 40 videos don't have spatial data that includes Pose, 3D Hand Data

def process_download_hololens_data(download_args):
	# ---- Parse Download Links Json ----
	with open("metadata/download_links.json", "r") as f:
		download_links = json.load(f)
	
	output_dir = Path(download_args.output_dir)
	data_directory = prepare_hololens_2d_output_directory(download_args, output_dir)
	
	download_url_links = []
	download_file_paths = []
	for index, (recording_id, recording_download_link_dict) in enumerate(download_links.items()):
		if download_args.data2d:
			if Constants.HOLOLENS_SYNC_PV_VIDEO in recording_download_link_dict:
				if recording_download_link_dict[Constants.HOLOLENS_SYNC_PV_VIDEO] is not None:
					hololens_pv_url = recording_download_link_dict[Constants.HOLOLENS_SYNC_PV_VIDEO]
					hololens_pv_path = data_directory / Constants.HOLOLENS / Constants.SYNC / Constants.PV / f"{recording_id}_360p.mp4"
					download_url_links.append(hololens_pv_url)
					download_file_paths.append(hololens_pv_path)
					print(f"Hololens 360P data downloaded for {recording_id}")
			else:
				print(f"Hololens 360P data not available for {recording_id}")
	
	print("-------------------------------------------------")
	print(f"Downloading {len(download_url_links)} files")
	download_data(download_url_links, download_file_paths)


if __name__ == "__main__":
	print("Starting the download process")
	
	# Create the parser
	parser = argparse.ArgumentParser(description='Download the data from BOX Cloud')
	
	parser.add_argument('--data2d', action='store_true',
	                    help='Use this to download 2D data from Box Cloud which includes Hololens [360p] data')
	
	parser.add_argument('--output_dir', type=str, default="data", help='Output directory to store the downloaded data')
	
	# Parse the arguments
	args = parser.parse_args()
	
	process_download_hololens_data(args)
