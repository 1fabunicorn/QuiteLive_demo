def _read_wordlist(file_path):
    with open(file_path) as f:
        content = f.readlines()
    content = [x.strip() for x in content]
    return content


wordlist = _read_wordlist("src/assets/english.txt")


# len(merkle_root) = 64
# len(wordlist) = 2048
# FFFF is the highest value a chunk can be, but we only have 2048 words
# words[0] = chunks[0] % len(wordlist)
def recite(merkle_root):
    chunk_size = 4
    # split merkle root into 16 chunks
    chunks = [merkle_root[i:i + chunk_size] for i in range(0, len(merkle_root), chunk_size)]
    words = []
    for chunk in chunks:
        chunk_to_hex = int("0x{}".format(chunk), 16)
        words.append(wordlist[chunk_to_hex % len(wordlist)])
    return words
