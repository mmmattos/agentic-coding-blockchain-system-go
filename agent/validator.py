def validate(chains):
    """
    Validate convergence among honest nodes (Node1, Node2)
    """

    honest = chains[:2]

    # Ensure chains exist
    if any(len(c) == 0 for c in honest):
        return False

    # Check same length
    lengths = [len(c) for c in honest]
    if len(set(lengths)) != 1:
        return False

    # Compare FULL chain hashes
    def extract_hashes(chain):
        hashes = []
        for block in chain:
            h = block.get("hash") or block.get("Hash")
            if not h:
                return None
            hashes.append(h)
        return hashes

    chains_hashes = [extract_hashes(c) for c in honest]

    if any(h is None for h in chains_hashes):
        return False

    return len(set(tuple(h) for h in chains_hashes)) == 1