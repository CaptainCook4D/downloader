import os
from asyncio import as_completed
from concurrent.futures import ThreadPoolExecutor
import time
from pathlib import Path

import requests
from tqdm.auto import tqdm


class Constants:
	CAPTAIN_COOK_4D = "captain_cook_4d"
	
	GOPRO = "gopro"
	HOLOLENS = "hololens"
	GOPRO_RESOLUTION_4K = "gopro_4k"
	GOPRO_RESOLUTION_360P = "gopro_360p"
	
	DATA_2D = "data_2d"
	RESOLUTION_360P = "resolution_360p"
	RESOLUTION_4K = "resolution_4k"
	
	RAW = "raw"
	SYNC = "sync"
	
	SPATIAL = "spatial"
	
	PV = "pv"
	MC = "mc"
	
	AB_ZIP = "ab.zip"
	DEPTH_ZIP = "depth.zip"
	FRAMES_ZIP = "frames.zip"
	
	DEPTH_AHAT = "depth_ahat"
	DEPTH = "depth"
	AB = "ab"
	
	DEPTH_POSE = "depth_pose"
	PV_POSE = "pv_pose"
	SPATIAL_POSE = "spatial_pose"
	
	IMU = "imu"
	DEPTH_POSE_PKL = "depth_pose_pkl"
	PV_POSE_PKL = "pv_pose_pkl"
	SPATIAL_POSE_PKL = "spatial_pkl"
	
	IMU_MAGNETOMETER = "imu_magnetometer"
	IMU_GYROSCOPE = "imu_gyroscope"
	IMU_ACCELEROMETER = "imu_accelerometer"
	
	IMU_ACCELEROMETER_PKL = "imu_accelerometer_pkl"
	IMU_GYROSCOPE_PKL = "imu_gyroscope_pkl"
	IMU_MAGNETOMETER_PKL = "imu_magnetometer_pkl"
	
	IS_HOLOLENS_ENABLED = "is_hololens_enabled"
	IS_SPATIAL_ENABLED = "is_spatial_enabled"
	
	DATA_JSON = "data_json"
	
	HOLOLENS_DEVICE_INFO = "hololens_device_info"
	
	RECORDING_ID = "recording_id"
	METADATA = "metadata"
	DOWNLOAD_LINKS = "download_links"
	FILE_SIZES = "file_sizes"
	RECORDING = "recording"
	
	HOLOLENS_RAW_PV_FRAMES_ZIP = "hololens_raw_pv_frames_zip"
	HOLOLENS_RAW_DEPTH_AHAT_AB_ZIP = "hololens_raw_depth_ahat_ab_zip"
	HOLOLENS_RAW_DEPTH_AHAT_DEPTH_ZIP = "hololens_raw_depth_ahat_depth_zip"
	HOLOLENS_RAW_MC_PKL = "hololens_raw_mc_pkl"
	
	HOLOLENS_SYNC_PV_FRAMES_ZIP = "hololens_sync_pv_frames_zip"
	HOLOLENS_SYNC_DEPTH_AHAT_AB_ZIP = "hololens_sync_depth_ahat_ab_zip"
	HOLOLENS_SYNC_DEPTH_AHAT_DEPTH_ZIP = "hololens_sync_depth_ahat_depth_zip"
	HOLOLENS_SYNC_PV_VIDEO = "hololens_sync_pv_video"
	
	HOLOLENS_RAW_SPATIAL_PKL = "hololens_raw_spatial_pkl"
	HOLOLENS_RAW_IMU_MAGNETOMETER_PKL = "hololens_raw_imu_magnetometer_pkl"
	HOLOLENS_RAW_IMU_GYROSCOPE_PKL = "hololens_raw_imu_gyroscope_pkl"
	HOLOLENS_RAW_IMU_ACCELEROMETER_PKL = "hololens_raw_imu_accelerometer_pkl"
	
	HOLOLENS_SYNC_SPATIAL_PKL = "hololens_sync_spatial_pkl"
	HOLOLENS_SYNC_IMU_MAGNETOMETER_PKL = "hololens_sync_imu_magnetometer_pkl"
	HOLOLENS_SYNC_IMU_GYROSCOPE_PKL = "hololens_sync_imu_gyroscope_pkl"
	HOLOLENS_SYNC_IMU_ACCELEROMETER_PKL = "hololens_sync_imu_accelerometer_pkl"
	
	HOLOLENS_RAW_PV_POSE_PKL = "hololens_raw_pv_pose_pkl"
	HOLOLENS_SYNC_PV_POSE_PKL = "hololens_sync_pv_pose_pkl"
	
	HOLOLENS_RAW_DEPTH_POSE_PKL = "hololens_raw_depth_pose_pkl"
	HOLOLENS_SYNC_DEPTH_POSE_PKL = "hololens_sync_depth_pose_pkl"
	
	DURATION = "duration"


# ---------------------------------------------------------------------------------------
# ------------------------ HOLOLENS STREAM TABLE ----------------------------------------
#
# Every Hololens stream Box holds for a recording, in both the `sync` and the `raw`
# variant.  `sync` streams are time aligned with the GoPro video; `raw` streams are the
# untouched device output.  A `None` key means the stream does not exist in that variant.
#
#   stream name -> (sync link key, raw link key, output sub directory, file name template)
# ---------------------------------------------------------------------------------------

HOLOLENS_STREAMS = {
	"pv_video": (
		Constants.HOLOLENS_SYNC_PV_VIDEO,
		None,
		"pv",
		"{recording_id}_360p.mp4",
	),
	"pv_frames": (
		Constants.HOLOLENS_SYNC_PV_FRAMES_ZIP,
		Constants.HOLOLENS_RAW_PV_FRAMES_ZIP,
		"pv_frames",
		"{recording_id}_frames.zip",
	),
	"pv_pose": (
		Constants.HOLOLENS_SYNC_PV_POSE_PKL,
		Constants.HOLOLENS_RAW_PV_POSE_PKL,
		"pv_pose",
		"{recording_id}_pv_pose.pkl",
	),
	"depth": (
		Constants.HOLOLENS_SYNC_DEPTH_AHAT_DEPTH_ZIP,
		Constants.HOLOLENS_RAW_DEPTH_AHAT_DEPTH_ZIP,
		"depth",
		"{recording_id}_depth.zip",
	),
	"ab": (
		Constants.HOLOLENS_SYNC_DEPTH_AHAT_AB_ZIP,
		Constants.HOLOLENS_RAW_DEPTH_AHAT_AB_ZIP,
		"ab",
		"{recording_id}_ab.zip",
	),
	"depth_pose": (
		Constants.HOLOLENS_SYNC_DEPTH_POSE_PKL,
		Constants.HOLOLENS_RAW_DEPTH_POSE_PKL,
		"depth_pose",
		"{recording_id}_depth_ahat_pose.pkl",
	),
	"spatial": (
		Constants.HOLOLENS_SYNC_SPATIAL_PKL,
		Constants.HOLOLENS_RAW_SPATIAL_PKL,
		"spatial",
		"{recording_id}_spatial.pkl",
	),
	"imu_accelerometer": (
		Constants.HOLOLENS_SYNC_IMU_ACCELEROMETER_PKL,
		Constants.HOLOLENS_RAW_IMU_ACCELEROMETER_PKL,
		"imu_accelerometer",
		"{recording_id}_imu_accelerometer.pkl",
	),
	"imu_gyroscope": (
		Constants.HOLOLENS_SYNC_IMU_GYROSCOPE_PKL,
		Constants.HOLOLENS_RAW_IMU_GYROSCOPE_PKL,
		"imu_gyroscope",
		"{recording_id}_imu_gyroscope.pkl",
	),
	"imu_magnetometer": (
		Constants.HOLOLENS_SYNC_IMU_MAGNETOMETER_PKL,
		Constants.HOLOLENS_RAW_IMU_MAGNETOMETER_PKL,
		"imu_magnetometer",
		"{recording_id}_imu_magnetometer.pkl",
	),
	"mc": (
		None,
		Constants.HOLOLENS_RAW_MC_PKL,
		"mc",
		"{recording_id}_mc.pkl",
	),
}

# Named bundles so users do not have to list every stream by hand.
STREAM_GROUPS = {
	"depth": ["depth", "ab", "depth_pose"],
	"pose": ["pv_pose", "depth_pose", "spatial"],
	"imu": ["imu_accelerometer", "imu_gyroscope", "imu_magnetometer"],
	"pv": ["pv_video", "pv_frames", "pv_pose"],
}

# --data3d is shorthand for everything that describes the scene in 3D.
DATA_3D_STREAMS = ["depth", "ab", "depth_pose", "spatial",
                   "imu_accelerometer", "imu_gyroscope", "imu_magnetometer"]

ALL_STREAMS = list(HOLOLENS_STREAMS.keys())


def resolve_streams(names):
	"""Expand group names into concrete stream names, preserving order and dropping repeats."""
	resolved = []
	for name in names:
		expanded = STREAM_GROUPS.get(name, [name])
		for stream in expanded:
			if stream not in HOLOLENS_STREAMS:
				raise ValueError(f"Unknown stream '{stream}'. Known streams: {', '.join(ALL_STREAMS)}")
			if stream not in resolved:
				resolved.append(stream)
	return resolved


def plan_hololens_downloads(download_links, streams, variants, data_directory, recording_ids=None):
	"""
	Work out exactly which files to fetch.

	Returns (urls, paths, skipped) where `skipped` explains, per recording, which
	requested streams have no link -- roughly 60 recordings have no Hololens data at
	all, and around 40 more are missing the spatial streams because of device drops.
	"""
	urls = []
	paths = []
	skipped = []

	for recording_id, recording_links in download_links.items():
		if recording_ids and recording_id not in recording_ids:
			continue
		if not isinstance(recording_links, dict):
			continue

		for variant in variants:
			variant_index = 0 if variant == Constants.SYNC else 1
			for stream in streams:
				link_key = HOLOLENS_STREAMS[stream][variant_index]
				sub_directory = HOLOLENS_STREAMS[stream][2]
				file_name = HOLOLENS_STREAMS[stream][3].format(recording_id=recording_id)

				if link_key is None:
					skipped.append((recording_id, variant, stream, "not available in this variant"))
					continue

				url = recording_links.get(link_key)
				if not url:
					skipped.append((recording_id, variant, stream, "no link for this recording"))
					continue

				urls.append(url)
				paths.append(data_directory / Constants.HOLOLENS / variant / sub_directory / file_name)

	return urls, paths, skipped


def prepare_download_directories(paths):
	"""Create every parent directory the planned downloads need."""
	for path in paths:
		Path(path).parent.mkdir(parents=True, exist_ok=True)


def download_url(download_tuple):
	url, target_path = download_tuple
	max_retries = 5
	retry_delay = 5

	def fetch_response(url):
		for attempt in range(max_retries):
			try:
				response = requests.get(url, stream=True)
				response.raise_for_status()
				return response
			except requests.exceptions.RequestException as e:
				print(f"Attempt {attempt + 1}/{max_retries} failed. Error: {str(e)}")
				if attempt < max_retries - 1:
					print(f"Retrying in {retry_delay} seconds...")
					time.sleep(retry_delay)
		return None

	response = fetch_response(url)
	if response is None:
		print(f"Giving up on {url} after {max_retries} attempts \n")
		return None

	total = response.headers.get('content-length')
	total = int(total) if total is not None else None

	# ---- The 3D archives are large, so never re-download a file we already hold in full ----
	if os.path.exists(target_path):
		file_size = os.path.getsize(target_path)
		if total is not None and file_size == total:
			print(f"File {target_path} already exists, skipping download \n")
			response.close()
			return url
		print(f"File {target_path} already exists, but size {file_size} does not match {total}, "
		      f"downloading again \n")
		os.remove(target_path)

	os.makedirs(os.path.dirname(os.path.abspath(target_path)), exist_ok=True)

	partial_path = f"{target_path}.part"
	with open(partial_path, "wb") as download_file:
		for data in response.iter_content(chunk_size=1024 * 1024):
			download_file.write(data)

	# ---- Only publish the final name once the body is fully written ----
	os.replace(partial_path, target_path)
	return url


def download_data(download_url_links, download_file_paths):
	# ---- DON'T INCREASE MAX_WORKERS, ELSE DOWNLOAD WILL BE INTERRUPTED ----
	prepare_download_directories(download_file_paths)
	with ThreadPoolExecutor(max_workers=3) as executor:
		results = list(
			tqdm(
				executor.map(
					download_url,
					zip(download_url_links, download_file_paths)
				),
				total=len(download_url_links)
			)
		)

	failed = [url for url, result in zip(download_url_links, results) if result is None]
	if failed:
		print(f"\n{len(failed)} of {len(download_url_links)} files could not be downloaded:")
		for url in failed[:20]:
			print(f"  {url}")
		if len(failed) > 20:
			print(f"  ... and {len(failed) - 20} more")
	else:
		print(f"\nAll {len(download_url_links)} files downloaded successfully")
	return results


def prepare_gopro_2d_output_directory(args, output_dir: Path):
	output_dir.mkdir(parents=True, exist_ok=True)
	
	data_directory = output_dir / Constants.CAPTAIN_COOK_4D
	data_directory.mkdir(parents=True, exist_ok=True)
	
	gopro_data_directory = data_directory / Constants.GOPRO
	gopro_data_directory.mkdir(parents=True, exist_ok=True)
	
	if args.resolution4K:
		resolution_4K_directory = gopro_data_directory / Constants.RESOLUTION_4K
		resolution_4K_directory.mkdir(parents=True, exist_ok=True)
	
	resolution_360p_directory = gopro_data_directory / Constants.RESOLUTION_360P
	resolution_360p_directory.mkdir(parents=True, exist_ok=True)
	
	return data_directory


def prepare_hololens_2d_output_directory(args, output_dir: Path):
	output_dir.mkdir(parents=True, exist_ok=True)
	
	data_directory = output_dir / Constants.CAPTAIN_COOK_4D
	data_directory.mkdir(parents=True, exist_ok=True)
	
	hololens_data_directory = data_directory / Constants.HOLOLENS
	hololens_data_directory.mkdir(parents=True, exist_ok=True)
	
	hololens_sync_data_directory = hololens_data_directory / Constants.SYNC
	hololens_sync_data_directory.mkdir(parents=True, exist_ok=True)
	
	hololens_sync_pv_data_directory = hololens_sync_data_directory / Constants.PV
	hololens_sync_pv_data_directory.mkdir(parents=True, exist_ok=True)
	
	return data_directory


def prepare_hololens_3d_output_directory(args, output_dir: Path):
	output_dir.mkdir(parents=True, exist_ok=True)
	
	data_directory = output_dir / Constants.CAPTAIN_COOK_4D
	data_directory.mkdir(parents=True, exist_ok=True)
	
	hololens_data_directory = data_directory / Constants.HOLOLENS
	hololens_data_directory.mkdir(parents=True, exist_ok=True)
	
	hololens_sync_data_directory = hololens_data_directory / Constants.SYNC
	hololens_sync_data_directory.mkdir(parents=True, exist_ok=True)
	
	hololens_sync_pv_data_directory = hololens_sync_data_directory / Constants.PV
	hololens_sync_pv_data_directory.mkdir(parents=True, exist_ok=True)
	
	hololens_sync_pv_pose_data_directory = hololens_sync_data_directory / Constants.PV_POSE
	hololens_sync_pv_pose_data_directory.mkdir(parents=True, exist_ok=True)
	
	hololens_sync_depth_pose_data_directory = hololens_sync_data_directory / Constants.DEPTH_POSE
	hololens_sync_depth_pose_data_directory.mkdir(parents=True, exist_ok=True)
	
	hololens_sync_spatial_data_directory = hololens_sync_data_directory / Constants.SPATIAL_POSE
	hololens_sync_spatial_data_directory.mkdir(parents=True, exist_ok=True)
	
	hololens_sync_imu_magnetometer_data_directory = hololens_sync_data_directory / Constants.IMU_MAGNETOMETER
	hololens_sync_imu_magnetometer_data_directory.mkdir(parents=True, exist_ok=True)
	
	hololens_sync_imu_gyroscope_data_directory = hololens_sync_data_directory / Constants.IMU_GYROSCOPE
	hololens_sync_imu_gyroscope_data_directory.mkdir(parents=True, exist_ok=True)
	
	hololens_sync_imu_accelerometer_data_directory = hololens_sync_data_directory / Constants.IMU_ACCELEROMETER
	hololens_sync_imu_accelerometer_data_directory.mkdir(parents=True, exist_ok=True)
	
	hololens_sync_depth_ahat_ab_data_directory = hololens_sync_data_directory / Constants.AB
	hololens_sync_depth_ahat_ab_data_directory.mkdir(parents=True, exist_ok=True)
	
	hololens_sync_depth_ahat_depth_data_directory = hololens_sync_data_directory / Constants.DEPTH
	hololens_sync_depth_ahat_depth_data_directory.mkdir(parents=True, exist_ok=True)
	
	hololens_metadata_directory = hololens_sync_data_directory / Constants.METADATA
	hololens_metadata_directory.mkdir(parents=True, exist_ok=True)
	
	return data_directory


def prepare_output_directory(args, output_dir: Path):
	output_dir.mkdir(parents=True, exist_ok=True)
	
	data_directory = output_dir / Constants.CAPTAIN_COOK_4D
	data_directory.mkdir(parents=True, exist_ok=True)
	
	if args.data2d:
		gopro_360p_directory = data_directory / Constants.GOPRO_RESOLUTION_360P
		gopro_360p_directory.mkdir(parents=True, exist_ok=True)
		
		hololens_sync_pv_video_directory = data_directory / Constants.HOLOLENS_SYNC_PV_VIDEO
		hololens_sync_pv_video_directory.mkdir(parents=True, exist_ok=True)
		
		if not args.resolution360p:
			gopro_4K_directory = data_directory / Constants.GOPRO_RESOLUTION_4K
			gopro_4K_directory.mkdir(parents=True, exist_ok=True)
	
	if args.data3d:
		depth_ahat_depth_directory = data_directory / Constants.DEPTH_AHAT / Constants.DEPTH
		depth_ahat_depth_directory.mkdir(parents=True, exist_ok=True)
		
		depth_ahat_ab_directory = data_directory / Constants.DEPTH_AHAT / Constants.AB
		depth_ahat_ab_directory.mkdir(parents=True, exist_ok=True)
	
	if args.spatial:
		spatial_directory = data_directory / Constants.SPATIAL
		spatial_directory.mkdir(parents=True, exist_ok=True)
		
		pv_pose_directory = data_directory / Constants.PV_POSE_PKL
		pv_pose_directory.mkdir(parents=True, exist_ok=True)
		
		depth_pose_directory = data_directory / Constants.DEPTH_POSE_PKL
		depth_pose_directory.mkdir(parents=True, exist_ok=True)
		
		imu_magnetometer_directory = data_directory / Constants.IMU / Constants.IMU_MAGNETOMETER
		imu_magnetometer_directory.mkdir(parents=True, exist_ok=True)
		
		imu_gyroscope_directory = data_directory / Constants.IMU / Constants.IMU_GYROSCOPE
		imu_gyroscope_directory.mkdir(parents=True, exist_ok=True)
		
		imu_accelerometer_directory = data_directory / Constants.IMU / Constants.IMU_ACCELEROMETER
		imu_accelerometer_directory.mkdir(parents=True, exist_ok=True)
		
		hololens_device_info_directory = data_directory / Constants.HOLOLENS_DEVICE_INFO
		hololens_device_info_directory.mkdir(parents=True, exist_ok=True)
	
	if args.raw:
		raw_directory = data_directory / Constants.RAW
		raw_directory.mkdir(parents=True, exist_ok=True)
	
	return data_directory
