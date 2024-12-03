import argparse
import json
from pathlib import Path

from util import prepare_gopro_2d_output_directory, Constants, download_data


def process_download_gopro_data(download_args):
	# ---- Parse Download Links Json ----
	with open("metadata/download_links.json", "r") as f:
		download_links = json.load(f)
	
	output_dir = Path(download_args.output_dir)
	data_directory = prepare_gopro_2d_output_directory(download_args, output_dir)
	
	download_url_links = []
	download_file_paths = []
	for index, (recording_id, recording_download_link_dict) in enumerate(download_links.items()):
		if download_args.data2d:
			if (Constants.GOPRO_RESOLUTION_360P in recording_download_link_dict and
					recording_download_link_dict[Constants.GOPRO_RESOLUTION_360P] is not None):
				gopro_360_url = recording_download_link_dict[Constants.GOPRO_RESOLUTION_360P]
				gopro_360p_path = data_directory / Constants.GOPRO / Constants.RESOLUTION_360P / f"{recording_id}_360p.mp4"
				download_url_links.append(gopro_360_url)
				download_file_paths.append(gopro_360p_path)
			else:
				if recording_download_link_dict[Constants.HOLOLENS_SYNC_PV_VIDEO] is not None:
					hololens_pv_url = recording_download_link_dict[Constants.HOLOLENS_SYNC_PV_VIDEO]
					hololens_pv_path = data_directory / Constants.GOPRO / Constants.RESOLUTION_360P / f"{recording_id}_360p.mp4"
					download_url_links.append(hololens_pv_url)
					download_file_paths.append(hololens_pv_path)
					print(f"Hololens 360P data downloaded for {recording_id}")
			
			if download_args.resolution4K:
				if recording_download_link_dict[Constants.GOPRO_RESOLUTION_4K] is not None:
					gopro_4k_url = recording_download_link_dict[Constants.GOPRO_RESOLUTION_4K]
					gopro_4k_path = data_directory / Constants.GOPRO / Constants.RESOLUTION_4K / f"{recording_id}_4K.mp4"
					download_url_links.append(gopro_4k_url)
					download_file_paths.append(gopro_4k_path)
	
	print("-------------------------------------------------")
	print(f"Downloading {len(download_url_links)} files")
	download_data(download_url_links, download_file_paths)


if __name__ == "__main__":
	print("Starting the download process")
	
	# Create the parser
	parser = argparse.ArgumentParser(description='Download the data from BOX Cloud')
	
	parser.add_argument('--data2d', action='store_true',
	                    help='Use this to download 2D data from Box Cloud which includes GOPRO [360p] data')
	parser.add_argument('--resolution4K', action='store_true',
	                    help='Use this to default download 4K data from Box Cloud which includes GOPRO [4K] data')
	
	parser.add_argument('--output_dir', type=str, default="data", help='Output directory to store the downloaded data')
	
	# Parse the arguments
	args = parser.parse_args()
	
	process_download_gopro_data(args)
