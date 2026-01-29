
import hashlib
import json

def hash_pair(hash1: str, hash2: str) -> str:
    """
    Calculates the SHA-256 hash of a concatenated pair of two hashes,
    ensuring a consistent order.
    """
    # Ensure consistent order for hashing to prevent trivial mismatches
    if hash1 > hash2:
        hash1, hash2 = hash2, hash1
    combined = hash1 + hash2
    return hashlib.sha256(combined.encode()).hexdigest()

def build_merkle_tree(hash_list: list[str]) -> tuple[str | None, dict]:
    """
    Constructs a Merkle Tree from a list of hashes.

    Args:
        hash_list: A list of SHA-256 hash strings.

    Returns:
        A tuple containing the Merkle Root hash (or None if input is empty)
        and a dictionary representing the full tree structure.
    """
    if not hash_list:
        return None, {}

    tree = {'leaves': hash_list}
    nodes = list(hash_list)
    level = 0

    while len(nodes) > 1:
        # If there's an odd number of nodes, duplicate the last one to create a pair
        if len(nodes) % 2 != 0:
            nodes.append(nodes[-1])
        
        next_level_nodes = []
        for i in range(0, len(nodes), 2):
            new_hash = hash_pair(nodes[i], nodes[i+1])
            next_level_nodes.append(new_hash)
        
        nodes = next_level_nodes
        tree[f'level_{level+1}'] = nodes
        level += 1
    
    merkle_root = nodes[0] if nodes else None
    tree['root'] = merkle_root
    
    return merkle_root, tree
