import hashlib
import binascii

# Base58 Alphabet (No 0, O, I, l)
ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

def base58_decode(s):
    """
    Decodes a Base58 string into bytes.
    """
    num = 0
    for char in s:
        num = num * 58 + ALPHABET.index(char)
    
    # Convert to bytes (approximation)
    h = hex(num)[2:]
    if len(h) % 2 != 0:
        h = "0" + h
    return binascii.unhexlify(h)

def verify_address(address):
    print(f"Verifying Canonical Address: {address}")
    print("--------------------------------------------------")
    
    try:
        # 1. Base58 Decode
        raw_bytes = base58_decode(address)
        
        # 2. Check Length (25 bytes for P2PKH/P2SH)
        # 1 byte Version + 20 bytes Hash + 4 bytes Checksum
        if len(raw_bytes) != 25:
            # Note: Sometimes leading zeros might be stripped in raw decoding if not careful,
            # but for this specific vanity address, we expect full length.
            # If it's shorter, we pad.
            if len(raw_bytes) < 25:
                 raw_bytes = b'\x00' * (25 - len(raw_bytes)) + raw_bytes
            else:
                 print(f"❌ Invalid Length: {len(raw_bytes)} bytes (Expected 25)")
                 return
            
        # 3. Verify Checksum
        payload = raw_bytes[:-4]
        checksum = raw_bytes[-4:]
        
        # Double SHA256
        h1 = hashlib.sha256(payload).digest()
        h2 = hashlib.sha256(h1).digest()
        calculated_checksum = h2[:4]
        
        if checksum == calculated_checksum:
            print("✅ Checksum Valid")
            print("   (This is a mathematically legitimate Dogecoin address)")
        else:
            print(f"❌ Checksum Invalid")
            print(f"   Expected: {binascii.hexlify(calculated_checksum)}")
            print(f"   Actual:   {binascii.hexlify(checksum)}")
            return
            
        # 4. Analyze Vanity
        if address.startswith("DKabosuForeverRestinPeace"):
             print("✅ Matches Canoncial Vanity Prefix")
        else:
             print("⚠️ Warning: Prefix mismatch")

        if "111" in address:
             print("✅ Contains Void Marker '111'")
             print("   (Represents approximate zero value in search space)")
             
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    # The chosen canonical address
    CANONICAL_ADDRESS = "DKabosuForeverRestinPeace1118PGJ77"
    verify_address(CANONICAL_ADDRESS)
