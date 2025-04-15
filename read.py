def read_book_file(path):
    with open(path, "rb") as f:
        data = f.read(1000)

    print(f"Total bytes: {len(data)}")
    for i in range(0, len(data), 16):
        chunk = data[i:i+16]
        hex_vals = ' '.join(f'{b:02x}' for b in chunk)
        ascii_vals = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
        print(f"{i:08x}  {hex_vals:<47}  {ascii_vals}")

# Example usage
read_book_file("7x6.book")
