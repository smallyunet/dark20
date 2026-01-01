import hashlib
import binascii

def base58_encode(b):
    alphabet = b'123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    # Convert big-endian bytes to integer
    n = int.from_bytes(b, 'big')
    
    chars = []
    while n > 0:
        n, r = divmod(n, 58)
        chars.append(alphabet[r:r+1])
    
    # Handle leading zeros
    pad = 0
    for byte in b:
        if byte == 0:
            pad += 1
        else:
            break
    
    return (b'1' * pad) + b''.join(reversed(chars))

def calculate_burn_address():
    # Input seed
    seed = 'Kabosu: 2005-2024'
    print(f"Seed: {seed}")
    
    # 1. SHA256 of the seed
    sha256_hash = hashlib.sha256(seed.encode('utf-8')).digest()
    
    # 2. RIPEMD160 of the SHA256 hash
    # Note: hashlib.new('ripemd160') might assume OpenSSL availability. 
    # Usually available on standard Python installs on Mac/Linux.
    try:
        if 'ripemd160' in hashlib.algorithms_available:
            ripemd160 = hashlib.new('ripemd160')
        else:
            # Fallback for systems without ripemd160 in hashlib (rare but possible)
            # This is a critical failure for this script if missing, but let's assume it's there for now.
             raise Exception("RIPEMD160 not available in hashlib")
             
        ripemd160.update(sha256_hash)
        h160 = ripemd160.digest()
    except Exception as e:
        print(f"Error: {e}")
        return

    print(f"H160: {binascii.hexlify(h160).decode('utf-8')}")

    # 3. Add Dogecoin Version Byte (0x1E = 30)
    version_byte = b'\x1e'
    payload = version_byte + h160
    
    # 4. Calculate Checksum (Double SHA256)
    checksum = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]
    
    # 5. Append Checksum
    final_binary = payload + checksum
    
    # 6. Base58 Encode
    address_bytes = base58_encode(final_binary)
    address = address_bytes.decode('utf-8')
    
    print("-" * 30)
    print(f"Dark-20 Burn Address: {address}")
    print("-" * 30)
    
    return address

if __name__ == "__main__":
    calculate_burn_address()
