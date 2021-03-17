import json
import subprocess
from concurrent.futures import ThreadPoolExecutor
import datetime
from random import choice

import merkletools
import requests

from src.recite import recite


class API:
    def __init__(self):
        self.tx_ids = list()
        self.node_count = 3
        self.docker_ip_offset = 0
        self.mine_n_seconds = 10  # 10 second block time
        self.last_mine = datetime.datetime.now()
        create_nodes = True
        if create_nodes:
            self.create_nodes(self.node_count, self.docker_ip_offset)
        self.node_ips = ["http://172.17.0.{}:5000".format(2 + i + self.docker_ip_offset) for i in
                         range(self.node_count)]
        self.node_data = {"nodes": self.node_ips}  # all node IPs for nodes to connect to each other

    @staticmethod
    def resolve_node(node_url):
        return requests.get("{}/nodes/resolve".format(node_url))

    @staticmethod
    def create_nodes(node_count, docker_ip_offset):
        print("Creating {} blockchain node containers".format(node_count))
        for i in range(0, node_count):
            print("{:.2%} done".format(i / node_count), end="\r")
            subprocess.call("docker run --rm -p {}:5000 -d blockchain".format(80 + i + docker_ip_offset), shell=True,
                            stdout=subprocess.DEVNULL)
        print("done making nodes")

    @staticmethod
    def mine(node_ip):
        return requests.get("{}/mine".format(node_ip))

    @staticmethod
    def _transact(sender, recipient, amount, added_data, node_url):
        tx = {
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
            "added_data": added_data
        }
        return requests.post("{}/transactions/new".format(node_url), json=tx)

    def register_node(self, node_url):
        return requests.post("{}/nodes/register".format(node_url), json=self.node_data)

    def register_all_nodes(self):
        with ThreadPoolExecutor(max_workers=2) as pool:
            list(pool.map(self.register_node, self.node_ips))

    def resolve_all_nodes(self):
        with ThreadPoolExecutor(max_workers=2) as pool:
            list(pool.map(self.resolve_node, self.node_ips))

    def random_mine(self):
        if self.last_mine + datetime.timedelta(0, self.mine_n_seconds) <= datetime.datetime.now():
            self.last_mine = datetime.datetime.now()
            self.mine(choice(self.node_ips))
            print("block mined")

    def transact(self, sender, recipient, amount, added_data):
        print("Broadcasting transaction with merkle root {}".format(added_data))
        self.register_all_nodes()
        response = self._transact(sender, recipient, amount, json.dumps(added_data), self.node_ips[0]).json()
        self.tx_ids.append(response['tx_id'])
        self.mine(self.node_ips[0])
        self.resolve_all_nodes()

    def get_recite_words(self):
        mt = merkletools.MerkleTools()  # default is sha256
        mt.add_leaf(self.tx_ids)
        mt.make_tree()
        mt.get_merkle_root()
        return " ".join(recite(mt.get_merkle_root()))
