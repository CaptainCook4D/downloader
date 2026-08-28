# downloader

Use this downloader to fetch CaptainCook4D data from the Box cloud.

- `download_gopro_data.py` — GoPro video (360p and 4K)
- `download_hololens_data.py` — Hololens 2D video (360p)
- `download_hololens_3d_data.py` — Hololens 3D and sensor streams

All three read their links from `metadata/download_links.json`.

```bash
pip install -r requirements.txt
```

## 2D data

Only GoPro 360p:

```bash
python download_gopro_data.py --data2d
```

Both GoPro 360p and 4K:

```bash
python download_gopro_data.py --data2d --resolution4K
```

Hololens 360p video:

```bash
python download_hololens_data.py --data2d
```

## 3D and sensor data

Everything that describes the scene in 3D — depth, active brightness, depth pose,
spatial (head and hand) pose, and the three IMU streams:

```bash
python download_hololens_3d_data.py --data3d
```

Every Hololens stream, including the PV video, PV frames and the microphone capture:

```bash
python download_hololens_3d_data.py --all --sync --raw
```

Pick individual streams or groups:

```bash
python download_hololens_3d_data.py --streams depth,imu
```

Restrict to specific recordings:

```bash
python download_hololens_3d_data.py --data3d --recordings 1_10,2_38
```

See what would be fetched without downloading anything:

```bash
python download_hololens_3d_data.py --all --dry_run
```

### Sync and raw

Every Hololens stream exists in two variants:

- `--sync` (default) — resampled and time aligned with the GoPro video
- `--raw` — the untouched device output, at the device's own timestamps

Pass both to get each variant side by side.

### Streams

| Stream | Contents | Sync | Raw |
| --- | --- | --- | --- |
| `pv_video` | 360p photo-video stream, mp4 | yes | no |
| `pv_frames` | Photo-video frames, zip | yes | yes |
| `pv_pose` | Photo-video camera pose, pkl | yes | yes |
| `depth` | AHAT depth maps, zip | yes | yes |
| `ab` | AHAT active brightness, zip | yes | yes |
| `depth_pose` | Depth camera pose, pkl | yes | yes |
| `spatial` | Head and hand pose, pkl | yes | yes |
| `imu_accelerometer` | Accelerometer, pkl | yes | yes |
| `imu_gyroscope` | Gyroscope, pkl | yes | yes |
| `imu_magnetometer` | Magnetometer, pkl | yes | yes |
| `mc` | Microphone capture, pkl | no | yes |

Groups that expand to several streams: `depth` (depth + ab + depth_pose),
`pose` (pv_pose + depth_pose + spatial), `imu` (all three IMU streams),
`pv` (pv_video + pv_frames + pv_pose).

### Coverage

Not every recording has every stream. Of the 384 recordings, roughly 60 were captured
with the GoPro alone and have no Hololens data, and about 40 more lost the spatial and
IMU streams to device instability. The scripts report how many recording/stream
combinations were unavailable and simply skip them.

## Output layout

```
<output_dir>/captain_cook_4d/
    gopro/
        resolution_360p/<recording_id>_360p.mp4
        resolution_4k/<recording_id>_4K.mp4
    hololens/
        sync/
            pv/<recording_id>_360p.mp4
            depth/<recording_id>_depth.zip
            ab/<recording_id>_ab.zip
            depth_pose/<recording_id>_depth_ahat_pose.pkl
            spatial/<recording_id>_spatial.pkl
            imu_accelerometer/<recording_id>_imu_accelerometer.pkl
            ...
        raw/
            ... same streams, plus mc/<recording_id>_mc.pkl
```

Downloads are resumable: a file whose size already matches the server is skipped, and
partial downloads are written to a `.part` file so an interrupted run never leaves a
truncated file behind.

The 3D archives are large. Downloading `--data3d` for all recordings is on the order of
several terabytes, so restrict with `--recordings` or `--streams` unless you intend to
pull the whole dataset.
