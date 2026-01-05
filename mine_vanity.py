#!/usr/bin/env python3
"""
DARK-DOGE Vanity Address Miner
==============================
Mines beautiful Dogecoin burn addresses with customizable patterns.

Usage:
    python mine_vanity.py --prefix "DKabosu" --suffix "1111"
    python mine_vanity.py --prefix "DDogeRIP" --min-ones 8
    python mine_vanity.py --beauty-mode  # Auto-find the most beautiful addresses
"""

import hashlib
import os
import sys
import time
import argparse
import multiprocessing
from dataclasses import dataclass
from typing import Optional, List, Tuple

# Base58 Alphabet (No 0, O, I, l)
ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
ALPHABET_SET = set(ALPHABET)

# Dogecoin Version Byte
DOGE_VERSION = 0x1e  # P2PKH addresses start with 'D'


@dataclass
class MiningResult:
    address: str
    beauty_score: int
    ones_count: int
    pattern_matched: str
    attempts: int
    time_seconds: float


def base58_encode(data: bytes) -> str:
    """Encode bytes to Base58 string."""
    num = int.from_bytes(data, 'big')
    
    result = []
    while num > 0:
        num, rem = divmod(num, 58)
        result.append(ALPHABET[rem])
    
    # Handle leading zeros
    for byte in data:
        if byte == 0:
            result.append('1')
        else:
            break
    
    return ''.join(reversed(result))


def create_address_from_hash(pubkey_hash: bytes) -> str:
    """Create a Dogecoin address from a 20-byte public key hash."""
    # Version + Hash
    versioned = bytes([DOGE_VERSION]) + pubkey_hash
    
    # Double SHA256 for checksum
    checksum = hashlib.sha256(hashlib.sha256(versioned).digest()).digest()[:4]
    
    # Full address bytes
    address_bytes = versioned + checksum
    
    return base58_encode(address_bytes)


def generate_random_hash() -> bytes:
    """Generate a random 20-byte hash (simulating RIPEMD160(SHA256(pubkey)))."""
    return os.urandom(20)


def calculate_beauty_score(address: str) -> int:
    """
    Calculate a beauty score for an address.
    Higher is more beautiful.
    
    Scoring:
    - Consecutive '1's: +10 per '1' (represents void/zero)
    - Repeating patterns: +5 per repeat
    - Clean endings (111, 777, etc.): +20
    - Lowercase letters (harder to read): -1 per char
    """
    score = 0
    
    # Count consecutive 1s (the more the better for "void" aesthetic)
    max_ones = 0
    current_ones = 0
    for c in address:
        if c == '1':
            current_ones += 1
            max_ones = max(max_ones, current_ones)
        else:
            current_ones = 0
    score += max_ones * 10
    
    # Total 1s count
    total_ones = address.count('1')
    score += total_ones * 3
    
    # Repeating character patterns at end (like 777, 888)
    if len(address) >= 3:
        last_three = address[-3:]
        if last_three[0] == last_three[1] == last_three[2]:
            score += 25
        elif last_three[1] == last_three[2]:
            score += 10
    
    # Check for "nice" endings
    nice_endings = ['111', '777', '888', '999', 'RIP', 'END', 'Wow']
    for ending in nice_endings:
        if address.endswith(ending):
            score += 20
    
    # Penalize too many lowercase (harder to read)
    lowercase_count = sum(1 for c in address if c.islower())
    score -= lowercase_count
    
    # Bonus for palindrome-like patterns in suffix
    suffix = address[-6:]
    if suffix == suffix[::-1]:
        score += 30
    
    return score


def check_pattern_match(address: str, prefix: Optional[str], suffix: Optional[str], 
                        contains: Optional[str], min_ones: int) -> Tuple[bool, str]:
    """Check if address matches the desired pattern."""
    matched = []
    
    if prefix and not address.startswith(prefix):
        return False, ""
    if prefix:
        matched.append(f"prefix:{prefix}")
    
    if suffix and not address.endswith(suffix):
        return False, ""
    if suffix:
        matched.append(f"suffix:{suffix}")
    
    if contains and contains not in address:
        return False, ""
    if contains:
        matched.append(f"contains:{contains}")
    
    ones_count = address.count('1')
    if ones_count < min_ones:
        return False, ""
    if min_ones > 0:
        matched.append(f"ones:{ones_count}")
    
    return True, ", ".join(matched) if matched else "beauty"


def mine_worker(args: Tuple) -> Optional[MiningResult]:
    """Worker function for multiprocessing."""
    prefix, suffix, contains, min_ones, min_beauty, max_attempts, worker_id = args
    
    start_time = time.time()
    best_result = None
    best_score = -1
    
    for attempt in range(max_attempts):
        # Generate random hash
        pubkey_hash = generate_random_hash()
        address = create_address_from_hash(pubkey_hash)
        
        # Check pattern match
        matches, pattern = check_pattern_match(address, prefix, suffix, contains, min_ones)
        
        if matches:
            score = calculate_beauty_score(address)
            
            if score >= min_beauty and score > best_score:
                best_score = score
                best_result = MiningResult(
                    address=address,
                    beauty_score=score,
                    ones_count=address.count('1'),
                    pattern_matched=pattern,
                    attempts=attempt + 1,
                    time_seconds=time.time() - start_time
                )
                
                # Print progress
                print(f"[Worker {worker_id}] Found: {address} (score: {score}, 1s: {best_result.ones_count})")
        
        # Progress update every 100k attempts
        if attempt > 0 and attempt % 100000 == 0:
            elapsed = time.time() - start_time
            rate = attempt / elapsed
            print(f"[Worker {worker_id}] Progress: {attempt:,} attempts, {rate:,.0f} addr/sec")
    
    return best_result


def estimate_difficulty(prefix: str) -> Tuple[float, str]:
    """Estimate mining difficulty for a given prefix."""
    # After 'D', each character has 1/58 probability
    prefix_len = len(prefix) - 1  # -1 because D is fixed
    
    if prefix_len <= 0:
        return 1, "instant"
    
    expected_attempts = 58 ** prefix_len
    
    # Estimate time at ~500k addr/sec
    rate = 500000
    seconds = expected_attempts / rate
    
    if seconds < 1:
        time_str = "instant"
    elif seconds < 60:
        time_str = f"{seconds:.1f} seconds"
    elif seconds < 3600:
        time_str = f"{seconds/60:.1f} minutes"
    elif seconds < 86400:
        time_str = f"{seconds/3600:.1f} hours"
    elif seconds < 86400 * 365:
        time_str = f"{seconds/86400:.1f} days"
    elif seconds < 86400 * 365 * 1000:
        time_str = f"{seconds/86400/365:.1f} years"
    else:
        time_str = "heat death of universe"
    
    return expected_attempts, time_str


def validate_prefix(prefix: str) -> bool:
    """Validate that prefix only contains valid Base58 characters."""
    if not prefix.startswith('D'):
        print("⚠️  Warning: Dogecoin addresses must start with 'D'")
        return False
    
    for c in prefix:
        if c not in ALPHABET_SET:
            print(f"❌ Invalid character '{c}' - Base58 doesn't include 0, O, I, l")
            return False
    
    return True


def beauty_mode_suggestions():
    """Print suggestions for beautiful addresses."""
    suggestions = [
        ("DKabosu", "Medium - ~30 min", "Classic tribute"),
        ("DKabosuRIP", "Hard - ~2 hours", "Memorial style"),
        ("DDoge", "Easy - ~1 sec", "Simple and clean"),
        ("DDogeVoid", "Medium - ~10 min", "Black hole theme"),
        ("DWow", "Easy - instant", "Such wow, very burn"),
        ("DMuchWow", "Medium - ~5 min", "Doge meme style"),
        ("DRIPKabosu", "Hard - ~2 hours", "RIP tribute"),
    ]
    
    print("\n" + "=" * 60)
    print("SUGGESTED PREFIXES FOR BEAUTIFUL ADDRESSES")
    print("=" * 60)
    print(f"{'Prefix':<20} {'Difficulty':<20} {'Theme'}")
    print("-" * 60)
    for prefix, difficulty, theme in suggestions:
        print(f"{prefix:<20} {difficulty:<20} {theme}")
    print("=" * 60)
    print("\nTip: Run with --prefix <choice> --min-ones 5 for best results")
    print("     More 1s = more 'void' aesthetic\n")


def main():
    parser = argparse.ArgumentParser(
        description="Mine beautiful Dogecoin vanity burn addresses",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python mine_vanity.py --prefix DKabosu --min-ones 5
  python mine_vanity.py --prefix DDoge --suffix 111
  python mine_vanity.py --beauty-mode
  python mine_vanity.py --prefix DWow --attempts 10000000
        """
    )
    
    parser.add_argument('--prefix', type=str, default='D',
                        help='Address prefix (must start with D)')
    parser.add_argument('--suffix', type=str, default=None,
                        help='Desired address suffix')
    parser.add_argument('--contains', type=str, default=None,
                        help='String that must appear in address')
    parser.add_argument('--min-ones', type=int, default=0,
                        help='Minimum number of 1s in address')
    parser.add_argument('--min-beauty', type=int, default=0,
                        help='Minimum beauty score')
    parser.add_argument('--attempts', type=int, default=1000000,
                        help='Maximum attempts per worker (default: 1M)')
    parser.add_argument('--workers', type=int, default=None,
                        help='Number of parallel workers (default: CPU count)')
    parser.add_argument('--beauty-mode', action='store_true',
                        help='Show suggestions for beautiful addresses')
    parser.add_argument('--estimate', action='store_true',
                        help='Only estimate difficulty, don\'t mine')
    
    args = parser.parse_args()
    
    if args.beauty_mode:
        beauty_mode_suggestions()
        return
    
    # Validate prefix
    if not validate_prefix(args.prefix):
        sys.exit(1)
    
    # Estimate difficulty
    expected, time_est = estimate_difficulty(args.prefix)
    print(f"\n{'=' * 60}")
    print(f"DARK-DOGE VANITY ADDRESS MINER")
    print(f"{'=' * 60}")
    print(f"Prefix:           {args.prefix}")
    print(f"Suffix:           {args.suffix or 'any'}")
    print(f"Min 1s:           {args.min_ones}")
    print(f"Min Beauty Score: {args.min_beauty}")
    print(f"Expected attempts: ~{expected:,.0f}")
    print(f"Estimated time:   {time_est}")
    print(f"{'=' * 60}\n")
    
    if args.estimate:
        return
    
    # Set up workers
    num_workers = args.workers or multiprocessing.cpu_count()
    attempts_per_worker = args.attempts // num_workers
    
    print(f"Starting {num_workers} workers with {attempts_per_worker:,} attempts each...")
    print(f"Total attempts: {num_workers * attempts_per_worker:,}\n")
    
    # Prepare worker arguments
    worker_args = [
        (args.prefix, args.suffix, args.contains, args.min_ones, 
         args.min_beauty, attempts_per_worker, i)
        for i in range(num_workers)
    ]
    
    start_time = time.time()
    
    # Run workers
    with multiprocessing.Pool(num_workers) as pool:
        results = pool.map(mine_worker, worker_args)
    
    elapsed = time.time() - start_time
    
    # Collect best results
    valid_results = [r for r in results if r is not None]
    
    if valid_results:
        # Sort by beauty score
        valid_results.sort(key=lambda x: x.beauty_score, reverse=True)
        
        print(f"\n{'=' * 60}")
        print("TOP RESULTS")
        print(f"{'=' * 60}")
        
        for i, result in enumerate(valid_results[:10], 1):
            print(f"\n#{i} {result.address}")
            print(f"    Beauty Score: {result.beauty_score}")
            print(f"    1s Count:     {result.ones_count}")
            print(f"    Pattern:      {result.pattern_matched}")
        
        print(f"\n{'=' * 60}")
        print(f"BEST ADDRESS: {valid_results[0].address}")
        print(f"{'=' * 60}")
    else:
        print("\n❌ No addresses found matching criteria.")
        print("Try reducing constraints or increasing attempts.")
    
    total_attempts = sum(r.attempts for r in results if r)
    print(f"\nCompleted in {elapsed:.1f}s ({total_attempts/elapsed:,.0f} addr/sec)")


if __name__ == "__main__":
    main()
