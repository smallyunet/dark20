#!/usr/bin/env python3
"""
DARK-DOGE Vanity Burn Address Generator
========================================
Creates beautiful, provably unspendable Dogecoin addresses.

The algorithm:
1. Start with a vanity prefix (e.g., "DKabosu")
2. Pad the middle with "1"s (representing void/zero in Base58)
3. Brute-force the last few characters to find valid checksum
4. Result: A valid address that looks beautiful but has no private key

Usage:
    python vanity_burn.py                          # Use default prefix
    python vanity_burn.py --prefix DKabosuRIP      # Custom prefix
    python vanity_burn.py --list                   # Show all variants
"""

import hashlib
import sys
import time
import itertools
from typing import Optional, List, Tuple
from dataclasses import dataclass

# Base58 Alphabet (No 0, O, I, l)
ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
ALPHABET_DICT = {c: i for i, c in enumerate(ALPHABET)}

# Dogecoin P2PKH version byte
DOGE_VERSION = 0x1e


@dataclass
class BurnAddress:
    address: str
    prefix: str
    ones_count: int
    beauty_score: int


def base58_decode(s: str) -> bytes:
    """Decode Base58 to bytes."""
    num = 0
    for c in s:
        if c not in ALPHABET_DICT:
            raise ValueError(f"Invalid Base58 character: {c}")
        num = num * 58 + ALPHABET_DICT[c]
    
    # Count leading '1's (which represent 0x00 bytes)
    pad_size = 0
    for c in s:
        if c == '1':
            pad_size += 1
        else:
            break
    
    # Convert to bytes
    result = []
    while num > 0:
        result.append(num & 0xff)
        num >>= 8
    
    return bytes(pad_size) + bytes(reversed(result))


def base58_encode(data: bytes) -> str:
    """Encode bytes to Base58."""
    num = int.from_bytes(data, 'big')
    
    result = []
    while num > 0:
        num, rem = divmod(num, 58)
        result.append(ALPHABET[rem])
    
    # Handle leading zero bytes
    for byte in data:
        if byte == 0:
            result.append('1')
        else:
            break
    
    return ''.join(reversed(result))


def double_sha256(data: bytes) -> bytes:
    """Double SHA256 hash."""
    return hashlib.sha256(hashlib.sha256(data).digest()).digest()


def create_burn_address(prefix: str, filler: str = "1") -> Optional[BurnAddress]:
    """
    Create a valid Dogecoin burn address with the given prefix.
    
    Strategy:
    - Dogecoin addresses are 34 characters
    - We use prefix + filler + variable suffix
    - Brute force the suffix until checksum is valid
    """
    target_len = 34
    
    # Validate prefix
    if not prefix.startswith('D'):
        print(f"Error: Address must start with 'D', got '{prefix[0]}'")
        return None
    
    for c in prefix:
        if c not in ALPHABET_DICT:
            print(f"Error: Invalid Base58 character '{c}'")
            print(f"  Note: Base58 doesn't include: 0, O, I, l")
            return None
    
    # Calculate filler needed
    suffix_len = 4  # We'll brute force last 4 chars
    filler_len = target_len - len(prefix) - suffix_len
    
    if filler_len < 0:
        print(f"Error: Prefix too long ({len(prefix)} chars). Max is {target_len - suffix_len - 1} chars.")
        return None
    
    # Build base with filler (using '1's for void aesthetic)
    base = prefix + (filler * filler_len)[:filler_len]
    
    print(f"🔍 Searching for valid address...")
    print(f"   Prefix: {prefix}")
    print(f"   Base:   {base}XXXX")
    
    start = time.time()
    attempts = 0
    
    # Brute force suffix (4 chars = 58^4 = ~11.3M combinations)
    for combo in itertools.product(ALPHABET, repeat=suffix_len):
        suffix = ''.join(combo)
        candidate = base + suffix
        attempts += 1
        
        try:
            # Decode
            decoded = base58_decode(candidate)
            
            # Pad to 25 bytes if needed
            if len(decoded) < 25:
                decoded = b'\x00' * (25 - len(decoded)) + decoded
            
            if len(decoded) != 25:
                continue
            
            # Check checksum
            payload = decoded[:-4]
            given_checksum = decoded[-4:]
            expected_checksum = double_sha256(payload)[:4]
            
            if given_checksum == expected_checksum:
                elapsed = time.time() - start
                ones = candidate.count('1')
                score = calculate_beauty(candidate)
                
                print(f"\n✅ Found valid address!")
                print(f"   Attempts: {attempts:,}")
                print(f"   Time:     {elapsed:.2f}s")
                print(f"   Rate:     {attempts/elapsed:,.0f}/sec")
                
                return BurnAddress(
                    address=candidate,
                    prefix=prefix,
                    ones_count=ones,
                    beauty_score=score
                )
                
        except Exception:
            continue
        
        # Progress every 500k
        if attempts % 500000 == 0:
            elapsed = time.time() - start
            print(f"   Progress: {attempts:,} ({attempts/elapsed:,.0f}/sec)")
    
    print(f"❌ No valid address found (tried all {attempts:,} combinations)")
    return None


def calculate_beauty(address: str) -> int:
    """Calculate aesthetic score."""
    score = 0
    
    # Count 1s
    ones = address.count('1')
    score += ones * 5
    
    # Consecutive 1s
    max_consec = 0
    current = 0
    for c in address:
        if c == '1':
            current += 1
            max_consec = max(max_consec, current)
        else:
            current = 0
    score += max_consec * 10
    
    # Repeating suffix
    if len(address) >= 3 and address[-1] == address[-2] == address[-3]:
        score += 25
    
    # Penalize lowercase
    score -= sum(1 for c in address if c.islower())
    
    return score


def generate_multiple(prefixes: List[str]) -> List[BurnAddress]:
    """Generate addresses for multiple prefixes."""
    results = []
    
    for prefix in prefixes:
        print(f"\n{'='*60}")
        result = create_burn_address(prefix)
        if result:
            results.append(result)
    
    return results


def show_list():
    """Generate and display multiple beautiful addresses."""
    prefixes = [
        # Classic memorial
        "DKabosu",
        "DKabosuRIP",
        
        # Doge meme
        "DDoge",
        "DWow",
        "DMuchWow",
        "DSuchBurn",
        
        # Black hole theme
        "DVoid",
        "DBlackHole",
        "DBurn",
        "DDark",
        
        # RIP theme
        "DRIP",
        "DRestInPeace",
        
        # Year
        "D2o24",  # Note: 'o' not '0'
    ]
    
    print("=" * 70)
    print("DARK-DOGE BURN ADDRESS GALLERY")
    print("=" * 70)
    
    results = generate_multiple(prefixes)
    
    # Sort by beauty
    results.sort(key=lambda x: x.beauty_score, reverse=True)
    
    print("\n" + "=" * 70)
    print("RESULTS RANKED BY BEAUTY")
    print("=" * 70)
    
    for i, r in enumerate(results, 1):
        print(f"\n#{i:2d} | Score: {r.beauty_score:3d} | 1s: {r.ones_count:2d}")
        print(f"     {r.address}")
    
    if results:
        print("\n" + "=" * 70)
        print(f"🏆 RECOMMENDED: {results[0].address}")
        print("=" * 70)


def verify_address(address: str) -> bool:
    """Verify that an address has valid checksum."""
    try:
        decoded = base58_decode(address)
        
        if len(decoded) < 25:
            decoded = b'\x00' * (25 - len(decoded)) + decoded
        
        if len(decoded) != 25:
            return False
        
        payload = decoded[:-4]
        given_checksum = decoded[-4:]
        expected_checksum = double_sha256(payload)[:4]
        
        return given_checksum == expected_checksum
    except:
        return False


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate beautiful Dogecoin burn addresses",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python vanity_burn.py                      # Default prefix
  python vanity_burn.py --prefix DKabosu     # Custom prefix
  python vanity_burn.py --prefix DRIP        # RIP theme
  python vanity_burn.py --list               # Generate gallery
  python vanity_burn.py --verify <address>   # Verify address
        """
    )
    
    parser.add_argument('--prefix', type=str, default="DKabosuRIP",
                        help='Vanity prefix (must start with D)')
    parser.add_argument('--list', action='store_true',
                        help='Generate multiple beautiful addresses')
    parser.add_argument('--verify', type=str,
                        help='Verify an existing address')
    
    args = parser.parse_args()
    
    if args.verify:
        valid = verify_address(args.verify)
        if valid:
            print(f"✅ Valid address: {args.verify}")
            print(f"   Beauty score: {calculate_beauty(args.verify)}")
            print(f"   1s count: {args.verify.count('1')}")
        else:
            print(f"❌ Invalid address: {args.verify}")
        return
    
    if args.list:
        show_list()
        return
    
    # Single address generation
    result = create_burn_address(args.prefix)
    
    if result:
        print("\n" + "=" * 60)
        print("GENERATED BURN ADDRESS")
        print("=" * 60)
        print(f"Address:      {result.address}")
        print(f"Prefix:       {result.prefix}")
        print(f"1s Count:     {result.ones_count}")
        print(f"Beauty Score: {result.beauty_score}")
        print("=" * 60)
        
        # Verify it's valid
        if verify_address(result.address):
            print("✅ Checksum verified - this is a valid Dogecoin address")
        else:
            print("❌ Warning: Checksum verification failed!")
        
        print("\n📋 Copy this address for your project:")
        print(f"   {result.address}")


if __name__ == "__main__":
    main()
