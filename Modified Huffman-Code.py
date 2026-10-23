import heapq, struct
from collections import Counter

ESC = 256  # one shared leaf that stands for ALL rare symbols


def build_codes(counts):
    """Huffman codes from {symbol: count}. Same input -> same codes."""
    heap = [(c, i, s) for i, (s, c) in enumerate(sorted(counts.items()))]
    heapq.heapify(heap)
    n = len(heap)
    while len(heap) > 1:
        c1, _, a = heapq.heappop(heap)
        c2, _, b = heapq.heappop(heap)
        heapq.heappush(heap, (c1 + c2, n, (a, b)))
        n += 1
    codes = {}

    def walk(node, code):
        if isinstance(node, tuple):
            walk(node[0], code + "0")
            walk(node[1], code + "1")
        else:
            codes[node] = code or "0"      # single symbol -> "0"

    if heap:
        walk(heap[0][2], "")
    return codes


def compress(data, limit):
    freq = {s: c for s, c in Counter(data).items() if c >= limit * len(data)}
    rare = len(data) - sum(freq.values())
    codes = build_codes({**freq, **({ESC: rare} if rare else {})})
    # rare byte = ESC code + its raw 8 bits
    bits = "".join(codes.get(b) or codes[ESC] + f"{b:08b}" for b in data)
    packed = bytes(int(bits[i:i + 8].ljust(8, "0"), 2) for i in range(0, len(bits), 8))
    header = struct.pack(">IH", len(data), len(freq))
    header += b"".join(struct.pack(">BI", s, c) for s, c in sorted(freq.items()))
    header += struct.pack(">I", rare)
    return header + packed


def decompress(blob):
    length, n = struct.unpack_from(">IH", blob)
    pos = 6 + 5 * n + 4
    counts = {s: c for s, c in struct.iter_unpack(">BI", blob[6:pos - 4])}
    rare, = struct.unpack_from(">I", blob, pos - 4)
    if sum(counts.values()) + rare != length:
        raise ValueError("Not a valid compressed file.")
    if rare:
        counts[ESC] = rare
    table = {code: s for s, code in build_codes(counts).items()}
    bits = "".join(f"{b:08b}" for b in blob[pos:])
    out, code, i = bytearray(), "", 0
    try:
        while len(out) < length:
            code += bits[i]
            i += 1
            if code in table:
                sym, code = table[code], ""
                if sym == ESC:
                    sym = int(bits[i:i + 8], 2)
                    i += 8
                out.append(sym)
    except (IndexError, ValueError):
        raise ValueError("The compressed data ended too early.")
    return bytes(out)


def main():
    while True:
        choice = input("\n1. Compress\n2. Decompress\n3. Exit\nChoose: ").strip()
        if choice == "3":
            return
        if choice not in ("1", "2"):
            print("Wrong choice")
            continue
        try:
            src = input("Input file: ").strip()
            dst = input("Output file: ").strip()
            if src == dst:
                raise ValueError("Input and output files must be different.")
            data = open(src, "rb").read()
            if choice == "1":
                limit = float(input("Minimum symbol probability (0 to 1): "))
                if not 0 <= limit <= 1:
                    raise ValueError("The limit must be between 0 and 1.")
                result = compress(data, limit)
                print(f"Original: {len(data) * 8} bits | Compressed: {len(result) * 8} bits "
                      f"({len(result) / max(len(data), 1):.0%} of original)")
            else:
                result = decompress(data)
                print("Done")
            open(dst, "wb").write(result)
        except (ValueError, OSError, struct.error) as e:
            print("Error:", e)


if __name__ == "__main__":
    main()
