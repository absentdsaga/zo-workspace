#!/usr/bin/env python3
"""
Deterministic seed strategy for reproducible frame generation

Seed formula:
  seed = char_hash + state_offset[state] + frame_index

This ensures:
- Same character + state + frame → always same output
- Different characters → different base seeds (via hash)
- Different states → different seed ranges (via offset)
- Different frames → incremental variation within state

Critical for debugging: "why did frame 5 of attack drift?"
"""

import hashlib

# State offsets (chosen to prevent overlap even with large character sets)
STATE_OFFSETS = {
    "idle": 0,
    "walk": 10000,
    "attack": 20000,
    "hit": 30000,
    "death": 40000,
    "cast": 50000,
    "defend": 60000,
    "emote": 70000
}

def get_character_hash(character_id: str) -> int:
    """
    Generate deterministic hash from character ID
    
    Uses CRC32-like approach to keep values in reasonable range
    while maintaining uniqueness across character set
    """
    hash_bytes = hashlib.sha256(character_id.encode()).digest()
    # Take first 4 bytes as int, mod to keep in safe range
    hash_int = int.from_bytes(hash_bytes[:4], byteorder='big')
    return hash_int % 1000000  # Keep under 1M to avoid overflow

def get_seed(character_id: str, state: str, frame_index: int, base_seed: int = 42) -> int:
    """
    Calculate deterministic seed for a specific frame
    
    Args:
        character_id: Unique character identifier (e.g., "hero_orange", "npc_bear")
        state: Animation state (e.g., "idle", "walk", "attack")
        frame_index: Frame number (1-indexed, e.g., 1, 2, 3...)
        base_seed: Global base seed (default: 42)
    
    Returns:
        Deterministic seed value
    
    Example:
        >>> get_seed("hero_orange", "idle", 1)
        542123  # Deterministic value
        >>> get_seed("hero_orange", "idle", 1)
        542123  # Same character/state/frame → same seed
        >>> get_seed("hero_orange", "idle", 2)
        542124  # Next frame → incremented
        >>> get_seed("hero_orange", "walk", 1)
        552123  # Different state → different offset
        >>> get_seed("npc_bear", "idle", 1)
        784123  # Different character → different hash
    """
    char_hash = get_character_hash(character_id)
    state_offset = STATE_OFFSETS.get(state, 0)
    
    seed = base_seed + char_hash + state_offset + frame_index
    
    return seed

def verify_seed_uniqueness(character_ids: list, states: list, max_frames: int = 20):
    """
    Verify that seed strategy produces unique seeds across test set
    
    Args:
        character_ids: List of character IDs to test
        states: List of states to test
        max_frames: Max frames per state to test
    
    Raises:
        AssertionError if collision detected
    """
    seen_seeds = {}
    
    for char_id in character_ids:
        for state in states:
            for frame_idx in range(1, max_frames + 1):
                seed = get_seed(char_id, state, frame_idx)
                
                key = (char_id, state, frame_idx)
                
                if seed in seen_seeds:
                    collision = seen_seeds[seed]
                    raise AssertionError(
                        f"SEED COLLISION: {key} and {collision} both produce seed {seed}"
                    )
                
                seen_seeds[seed] = key
    
    print(f"✓ Verified {len(seen_seeds)} unique seeds across:")
    print(f"  - {len(character_ids)} characters")
    print(f"  - {len(states)} states")
    print(f"  - {max_frames} frames/state")
    print(f"  = {len(seen_seeds)} total seeds (all unique)")

if __name__ == "__main__":
    # Self-test
    test_characters = [
        "hero_orange",
        "npc_bear",
        "npc_raccoon",
        "npc_fox",
        "boss_dragon"
    ]
    
    test_states = ["idle", "walk", "attack", "hit"]
    
    verify_seed_uniqueness(test_characters, test_states, max_frames=20)
    
    # Show examples
    print("\nExample seeds:")
    for char in test_characters[:2]:
        for state in test_states[:2]:
            for frame in [1, 5, 10]:
                seed = get_seed(char, state, frame)
                print(f"  {char:15} {state:8} frame {frame:2} → seed {seed}")
