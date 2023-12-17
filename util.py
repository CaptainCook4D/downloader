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
	
	response = fetch_response(url)
	total = response.headers.get('content-length')
	
	if os.path.exists(target_path):
		file_size = os.path.getsize(target_path)
		if file_size == int(total):
			print(f"File {target_path} already exists, skipping download \n")
			return url
		else:
			print(
				f"File {target_path} already exists, but size {file_size} is different from total {total}, downloading again \n")
			os.remove(target_path)
			parent_dir = os.path.dirname(target_path)
			if not os.path.exists(parent_dir):
				parent_dir.mkdir(parents=True, exist_ok=True)
	
	response.raise_for_status()
	with open(target_path, "wb") as download_file:
		for data in response.iter_content(chunk_size=1024):
			download_file.write(data)
	return url


def download_data(download_url_links, download_file_paths):
	# ---- DON'T INCREASE MAX_WORKERS, ELSE DOWNLOAD WILL BE INTERRUPTED ----
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
