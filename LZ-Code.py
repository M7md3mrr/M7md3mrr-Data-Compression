
SEARCH_WINDOW = 25


def compress(data):
    tags = []
    i = 0
    while i < len(data):
        best_position = 0
        best_length = 0
        for start in range(max(0, i - SEARCH_WINDOW), i):
            length = 0
            while i + length < len(data) - 1 and data[start + length] == data[i + length]:
                length += 1
            if length > 0 and length >= best_length:   
                best_length = length
                best_position = i - start
        tags.append((best_position, best_length, data[i + best_length]))
        i = i + best_length + 1
    return tags     


def decompress(tags):
    data = ""
    for position, length, next_symbol in tags:
        for _ in range(length):
            data += data[-position]
        data += next_symbol
    return data


def do_compress():
    name = input("Input file: ")  
    out = input("Compressed file: ") 
    data = open(name, "r").read() 
    
    tags = compress(data) 

    f = open(out, "w") 
    for position, length, next_symbol in tags:
        if next_symbol == "\n":
            next_symbol = "\\n"
        f.write(f"{position} {length} {next_symbol}\n") 
    f.close() 


    position_bits = max(t[0] for t in tags).bit_length() 
    length_bits = max(t[1] for t in tags).bit_length()
    tag_size = position_bits + length_bits + 8
    print("Original Size =", len(data), "*", 8, "=", len(data) * 8, "bits")
    print("Tag size =", position_bits, "+", length_bits, "+ 8 =", tag_size, "bits")
    print("Compressed Size =", len(tags), "*", tag_size, "=", len(tags) * tag_size, "bits")


def do_decompress():
    name = input("Compressed file: ")
    out = input("Output file: ")
    tags = []   
    for line in open(name, "r"):
        position, length, next_symbol = line.rstrip("\n").split(" ", 2) 
        if next_symbol == "\\n":
            next_symbol = "\n"
    
        tags.append((int(position), int(length), next_symbol))
    open(out, "w").write(decompress(tags))
    print("Done")


while True:
    print("\n1. Compress")
    print("2. Decompress")
    print("3. Exit")
    choice = input("Choose: ")
    if choice == "1":
        do_compress()
    elif choice == "2":
        do_decompress()
    elif choice == "3":
        break
    else:
        print("Wrong choice")


