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
			# ---- A handful of recordings have no GoPro 360p, fall back to the Hololens view ----
			gopro_360_url = recording_download_link_dict.get(Constants.GOPRO_RESOLUTION_360P)
			if gopro_360_url is not None:
				gopro_360p_path = data_directory / Constants.GOPRO / Constants.RESOLUTION_360P / f"{recording_id}_360p.mp4"
				download_url_links.append(gopro_360_url)
				download_file_paths.append(gopro_360p_path)
			else:
				hololens_pv_url = recording_download_link_dict.get(Constants.HOLOLENS_SYNC_PV_VIDEO)
				if hololens_pv_url is not None:
					hololens_pv_path = data_directory / Constants.GOPRO / Constants.RESOLUTION_360P / f"{recording_id}_360p.mp4"
					download_url_links.append(hololens_pv_url)
					download_file_paths.append(hololens_pv_path)
					print(f"No GoPro 360P for {recording_id}, using the Hololens view instead")
				else:
					print(f"No 360P video available for {recording_id}")

			if download_args.resolution4K:
				gopro_4k_url = recording_download_link_dict.get(Constants.GOPRO_RESOLUTION_4K)
				if gopro_4k_url is not None:
					gopro_4k_path = data_directory / Constants.GOPRO / Constants.RESOLUTION_4K / f"{recording_id}_4K.mp4"
					download_url_links.append(gopro_4k_url)
					download_file_paths.append(gopro_4k_path)
				else:
					print(f"No GoPro 4K available for {recording_id}")
	
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
