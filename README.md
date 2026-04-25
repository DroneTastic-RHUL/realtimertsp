# realtimertsp
Python package to receive RTSP streams with as little delay as possible

Always gets the latest frame from a stream allowing for sub 100ms latency.

Requires `ffmpeg` and `ffprobe` to be in path.
`ffprobe` is only used when no stream size has been specified.

## Usage
Installation:
```shell
pip install https://github.com/DroneTastic-RHUL/realtimertsp.git
```

CLI:
```shell
python -m realtimertsp rtsp://dronetastic.local:8554/cam1
```

Python:
```python
with RealtimeStream(url) as stream:
    frame = stream.read_latest_frame() # get a read only frame (use .copy() to write in cv2)
```
