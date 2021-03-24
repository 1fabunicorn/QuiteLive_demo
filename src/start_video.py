import shlex
import os
import glob
from subprocess import Popen
from datetime import timedelta


def start(t_seconds, modified=True):
    if modified:
        command = shlex.split("""
            ffmpeg -loglevel error -hwaccel auto 
            -f alsa
              -ac 1
              -ar 44000
              -thread_queue_size 2048
              -i hw:2,1,0
            -f video4linux2
              -thread_queue_size 2048
              -r 30
              -i /dev/video0
              -map 1 -map 0
              -vf "drawtext=fontfile=Freeerif.ttf:fontcolor=red:x=100:y=x/dar:enable=lt(mod(t\,2)\,1):box=1:text='Modified"
              -vsync drop
              -vcodec libx265
              -s 1280x720
              -preset medium
              -r 30
              -acodec aac
              -t {}
            -f tee "[f=framehash]out/out.md5|[f=mp4]out/out.mp4"
            """.format(str(timedelta(seconds=t_seconds))))
    else:
        command = shlex.split("""
        ffmpeg -loglevel error -hwaccel auto 
        -f alsa
          -ac 1
          -ar 44000
          -thread_queue_size 2048
          -i hw:2,1,0
        -f video4linux2
          -thread_queue_size 2048
          -r 30
          -i /dev/video0
          -map 1 -map 0
          -vsync drop
          -vcodec libx265
          -s 1280x720
          -preset medium
          -r 30
          -acodec aac
          -t {}
        -f tee "[f=framehash]out/out.md5|[f=mp4]out/out.mp4"
        """.format(str(timedelta(seconds=t_seconds))))
    Popen(command)

