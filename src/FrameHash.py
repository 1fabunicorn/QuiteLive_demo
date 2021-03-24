import os
from time import sleep
import pandas
import merkletools


class FrameHash:
    def __init__(self, path):
        self.path = self._set_path(path)
        self.hashes_dataframe = None
        self.hashes = list()
        self.merkle_roots = list()
        self.csv_start = self._get_csv_start()
        self.f_pointer = self.csv_start

    def _get_csv_start(self):
        sleep(2)
        with open(self.path, "r") as f:
            for line_number, line in enumerate(f.readlines(), start=1):
                if line[0:8] == "#stream#":  # find header
                    return line_number  # this is the first line with a frame
            raise Exception("Error: Malformed FrameHash file, can't find header")

    @staticmethod
    def _set_path(path):
        while True:
            if os.path.isfile(path) is True:
                break
            sleep(.1)
        return path

    def sync(self, new_f_pointer):
        hash_frame_new = pandas.read_csv(self.path, skiprows=self.f_pointer,
                                         names=["stream", "dts", "pts", "duration", "size", "hash", "placeholder1",
                                                "placeholder2", "placeholder3"])
        self.f_pointer = new_f_pointer
        return hash_frame_new

    def get_hashes(self):
        current_line_count = self.line_count()
        if self.f_pointer != current_line_count:
            hash_frame_new = self.sync(current_line_count)
            hash_column = hash_frame_new["hash"].tolist()
            hash_column = [ele.strip(' ') for ele in hash_column]  # removes whitespace from start
            self.hashes.append(hash_column)  # adds list to list
        return self.hashes

    def get_last_hashes(self):
        return self.get_hashes()[-1]

    def compute_root(self):
        mt = merkletools.MerkleTools()  # default is sha256
        last_hashes = self.get_last_hashes()
        mt.add_leaf(last_hashes)
        mt.make_tree()
        new_merkle_root = {
            "frame_count": self.f_pointer - self.csv_start,
            "merkle_root": mt.get_merkle_root(),
            # "hash": self.get_last_hashes(),

        }
        self.merkle_roots.append(new_merkle_root)
        return new_merkle_root

    def get_roots(self):  # compute merkle root on last set of frames
        return self.merkle_roots

    def line_count(self):
        with open(self.path) as f:
            for i, l in enumerate(f):
                pass
        return i + 1

