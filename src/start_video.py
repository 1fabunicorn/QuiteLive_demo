import shlex
import os
import glob
from subprocess import Popen
from datetime import timedelta


def start(t_seconds):
    command = shlex.split("""
    ffmpeg -loglevel error -hwaccel auto -fflags +genpts
    -f alsa
      -ac 1
      -ar 44000
      -thread_queue_size 2048
      -i hw:2,1,0
    -f video4linux2
      -thread_queue_size 2048
      -i /dev/video0
      -map 1 -map 0
      -vcodec libx264
      -preset ultrafast 
      -tune zerolatency
      -s 1280x720
      -r 30
      -acodec aac
      -t {}
    -f tee "[f=framehash]out/out.md5|[f=mp4]out/out.mp4"
    """.format(str(timedelta(seconds=t_seconds))))
    Popen(command)
