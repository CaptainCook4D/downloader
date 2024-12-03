# downloader

Please use this downloader to fetch 2D data from the box cloud.

To download GoPro data, run download_gopro_data.py with the appropriate arguments set.

To download Hololens data, run download_hololens_data.py with the appropriate arguments set.


## Download Settings:

To download 2D data (only GoPro 360P data).

``
python download_gopro_data.py --data2d
``

To download 2D data (both GoPro 360P and GoPro 4K data).

``
python download_gopro_data.py --data2d --resolution4K
``

To download 2D data (only Hololens data).

``
python download_hololens_data.py --data2d
``


To download 3D data (only Hololens data).

**NOTE** We are currently processing Hololens 3D data. Please email rohith.peddi@utdallas.edu for priority access.
