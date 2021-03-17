import collections
import json
import subprocess

import merkletools
import yaml
import shlex
import os
from mutagen.mp4 import MP4
from src.FrameHash import FrameHash


def _framehash(video_file):
    if os.path.exists("out/out1.md5"):
        os.remove("out/out1.md5")
    command = shlex.split("""
    ffmpeg -hide_banner -fflags +genpts \
    -i {} \
    -c copy \
    -f framehash out/out1.md5
    """.format(video_file))
    subprocess.Popen(command)


def _extract_frame_counts(metadata):
    offsets = []
    for root in metadata['merkle_roots']:
        offsets.append(root['frame_count'])
    return offsets


def get_hashes(offsets, hashes):
    hashes = collections.deque(hashes)
    offset_hashes = []
    for i in offsets:
        temp = []
        for j in range(i):
            temp.append(hashes.popleft())
        offset_hashes.append(temp)
    return offset_hashes


def verify(video_file):
    _framehash(video_file)
    fh = FrameHash(path="out/out1.md5")
    with open('out/metadata.json') as json_file:
        metadata = json.load(json_file)
    offsets = _extract_frame_counts(metadata)
    offsetted_hashes = get_hashes(offsets, fh.get_hashes()[0])
    # print(offsetted_hashes)
    mt = merkletools.MerkleTools()  # default is sha256
    merkle_roots = []
    for hashes in offsetted_hashes:
        mt.reset_tree()
        mt.add_leaf(hashes)
        mt.make_tree()
        new_merkle_root = {
            "frame_count": len(hashes),
            "merkle_root": mt.get_merkle_root(),
        }
        merkle_roots.append(new_merkle_root)
    return merkle_roots



# print(json.dumps(merkle_root, indent=4))


