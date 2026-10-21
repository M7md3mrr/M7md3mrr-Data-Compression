import heapq

MAGIC = b"MHF1"   # marks our compressed files
ESC = 256         # special symbol that stands for ALL rare symbols


def build_codes(counts):
    # build Huffman codes from {symbol: count}
    heap = []
    order = 0                                   # unique number -> same tie-breaking every time
    for sym in sorted(counts):
        heap.append((counts[sym], order, sym))
        order += 1
    heapq.heapify(heap)
    while len(heap) > 1:
        c1, _, n1 = heapq.heappop(heap)
        c2, _, n2 = heapq.heappop(heap)
        heapq.heappush(heap, (c1 + c2, order, (n1, n2)))
        order += 1
    codes = {}
    stack = [(heap[0][2], "")] if heap else []
    while stack:
        node, code = stack.pop()
        if isinstance(node, tuple):
            stack.append((node[0], code + "0"))
            stack.append((node[1], code + "1"))
        else:
            codes[node] = code or "0"           # only one symbol -> code "0"
    return codes


def compress(data, limit):
    # data = bytes. Returns (frequent counts, rare total, bit string)
    counts = {}
    for b in data:
        counts[b] = counts.get(b, 0) + 1
    frequent = {s: c for s, c in counts.items() if c / len(data) >= limit}
    rare_total = sum(c for s, c in counts.items() if s not in frequent)

    tree_counts = dict(frequent)
    if rare_total > 0:
        tree_counts[ESC] = rare_total           # all rare symbols share ONE leaf
    codes = build_codes(tree_counts)

    parts = []
    for b in data:
        if b in codes:
            parts.append(codes[b])
        else:                                   # rare: ESC code + raw 8 bits
            parts.append(codes[ESC] + format(b, "08b"))
    return frequent, rare_total, "".join(parts)


def decompress(counts, rare_total, bits, length):
    # rebuild the same codes, then decode bit by bit
    out = bytearray()
    if length == 0:
        return out
    if rare_total > 0:
        counts[ESC] = rare_total
    table = {code: sym for sym, code in build_codes(counts).items()}
    i = 0
    while len(out) < length:
        code = ""
        while code not in table:
            if i >= len(bits):
                raise ValueError("The compressed data ended too early.")
            code += bits[i]
            i += 1
        sym = table[code]
        if sym == ESC:                          # next 8 bits = the rare symbol
            if i + 8 > len(bits):
                raise ValueError("The compressed data ended too early.")
            sym = int(bits[i:i + 8], 2)
            i += 8
        out.append(sym)
    return out


def do_compress():
    name = input("Input file: ").strip()
    out = input("Compressed file: ").strip()
    if name == out:
        raise ValueError("Input and output files must be different.")
    try:
        limit = float(input("Minimum symbol probability limit (0 to 1): "))
    except ValueError:
        raise ValueError("The limit must be a number.")
    if not 0 <= limit <= 1:
        raise ValueError("The limit must be between 0 and 1.")

    data = open(name, "rb").read()              # binary mode keeps every byte exactly
    frequent, rare_total, bits = compress(data, limit)

    bits_len = len(bits)
    bits += "0" * (-len(bits) % 8)              # pad to whole bytes
    packed = bytes(int(bits[i:i + 8], 2) for i in range(0, len(bits), 8))

    header = MAGIC + len(data).to_bytes(4, "big") + len(frequent).to_bytes(2, "big")
    for s in sorted(frequent):
        header += bytes([s]) + frequent[s].to_bytes(4, "big")
    header += rare_total.to_bytes(4, "big")

    f = open(out, "wb")
    f.write(header + packed)
    f.close()

    print("Original Size =", len(data), "*", 8, "=", len(data) * 8, "bits")
    print("Data bits =", bits_len, "bits (", len(packed), "bytes after packing )")
    print("Header =", len(header), "bytes =", len(header) * 8, "bits")
    print("Compressed Size =", (len(header) + len(packed)) * 8, "bits")
    print("Rare symbols merged into ESC:", len(set(data)) - len(frequent))


def do_decompress():
    name = input("Compressed file: ").strip()
    out = input("Output file: ").strip()
    if name == out:
        raise ValueError("Input and output files must be different.")
    blob = open(name, "rb").read()

    if len(blob) < 14 or blob[:4] != MAGIC:
        raise ValueError("This is not a valid compressed file.")
    length = int.from_bytes(blob[4:8], "big")
    n = int.from_bytes(blob[8:10], "big")
    header_size = 10 + 5 * n + 4
    if n > 256 or len(blob) < header_size:
        raise ValueError("The compressed file header is damaged.")
    counts = {}
    for i in range(n):
        pos = 10 + 5 * i
        counts[blob[pos]] = int.from_bytes(blob[pos + 1:pos + 5], "big")
    rare_total = int.from_bytes(blob[header_size - 4:header_size], "big")
    if sum(counts.values()) + rare_total != length:
        raise ValueError("The compressed file header is damaged.")

    bits = "".join(format(b, "08b") for b in blob[header_size:])   # unpack bytes -> bits
    data = decompress(counts, rare_total, bits, length)

    f = open(out, "wb")
    f.write(data)
    f.close()
    print("Done")


while True:
    print("\n1. Compress")
    print("2. Decompress")
    print("3. Exit")
    choice = input("Choose: ").strip()
    if choice == "3":
        break
    elif choice in ("1", "2"):
        try:
            if choice == "1":
                do_compress()
            else:
                do_decompress()
        except FileNotFoundError:
            print("Error: file not found.")
        except (ValueError, OSError) as e:
            print("Error:", e)
    else:
        print("Wrong choice")
