import json


version = 0.1
hash_alg = "md5"


def _format_metadata(merkle_roots, tx_ids):
    return {
        "version": version,
        "hash_algorithm": hash_alg,
        "merkle_roots": merkle_roots,
        "tx_ids": tx_ids
    }


def add_metadata(merkle_roots, tx_ids):
    metadata = _format_metadata(merkle_roots, tx_ids)
    with open('out/metadata.json', 'w+') as outfile:
        json.dump(metadata, outfile)

