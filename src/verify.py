import collections
import json
import subprocess

import merkletools
import shlex
import os
from src.FrameHash import FrameHash
from src.recite import recite


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


def _get_hashes(offsets, hashes):
    hashes = collections.deque(hashes)
    offset_hashes = []
    for i in offsets:
        temp = []
        for j in range(i):
            temp.append(hashes.popleft())
        offset_hashes.append(temp)
    return offset_hashes


def check_txs(bc_api, metadata):
    matches = 0

    for i, merkle_root in enumerate(metadata["merkle_roots"]):
        if bc_api.hash_in_tx_ID(metadata["tx_ids"][i], merkle_root["merkle_root"]):
            matches += 1

    return "{} out of {} tx's include the correct merkle root".format(matches, len(metadata["merkle_roots"]))


def merkle_root_from_tx_ids(metadata):
    tx_ids = metadata["tx_ids"]
    mt = merkletools.MerkleTools()  # default is sha256
    mt.add_leaf(tx_ids)
    mt.make_tree()

    mt.get_merkle_root()
    return " ".join(recite(mt.get_merkle_root()))


def get_merkle_roots_from_video(video_file):
    _framehash(video_file)
    fh = FrameHash(path="out/out1.md5")
    with open('out/metadata.json') as json_file:
        metadata = json.load(json_file)
    offsets = _extract_frame_counts(metadata)
    offsetted_hashes = _get_hashes(offsets, fh.get_hashes()[0])  # only one element in list, get the first one
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
