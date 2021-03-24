#rm -rf out/*.*
#
#ffmpeg -hwaccel auto \
#-f alsa \
#  -ac 1 \
#  -ar 44000 \
#  -thread_queue_size 2048 \
#  -i hw:2,1,0 \
#-f video4linux2 \
#  -thread_queue_size 2048 \
#    -r 30 \
#  -i /dev/video0 \
#  -map 1 -map 0 \
#  -vcodec libx264 \
#  -s 1280x720 \
#  -preset fast \
#  -tune zerolatency \
#  -r 30 \
#  -acodec aac \
#  -t 00:00:20 \
#-f tee "[f=framehash]out/out.md5|[f=mp4]out/out.mp4"




    ffmpeg -hide_banner -hwaccel auto \
    -r 30 \
    -i out/out.mp4 \
    -c copy \
    -r 30 \
    -f framehash out/out1.md5








#ffmpeg -hwaccel auto -fflags +genpts \
#-f alsa -ac 1 -ar 44000 -thread_queue_size 2048 -i hw:2,1,0 \
#-f video4linux2 -thread_queue_size 2048 -i /dev/video0 \
#-vf "drawtext=fontfile=Freeerif.ttf:fontcolor=red:x=100:y=x/dar:enable=lt(mod(t\,2)\,1):box=1:text='Modified'" \
#-map 1 -map 0 \
#-vcodec libx264 -preset ultrafast -tune zerolatency -s 1280x720 -r 30 -acodec aac \
#-f tee "[f=framehash]out/out.md5|[f=mp4]out/out.mp4"
#
#echo "Next"
#ffmpeg -hide_banner -fflags +genpts \
#-i out/out.mp4 \
#-c copy \
#-f framehash out/from_stream_after.md5
#
#ffmpeg -loglevel error -fflags +genpts \
#-i out/out.mp4 \
#-metadata comment="abc" \
#-c copy \
#out/out_with_metadata.mp4
#
#ffmpeg -hide_banner -fflags +genpts \
#-i out/out_with_metadata.mp4 \
#-c copy \
#-f framehash out/from_metadata.md5