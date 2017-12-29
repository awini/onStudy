python _grab.py | ffmpeg -f rawvideo -pixel_format rgb24 -video_size 1280x720 -framerate 4 -i - -f flv rtmp://localhost/myapp/mystream
