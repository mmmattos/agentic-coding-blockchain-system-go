def validate(chains):
    """
    Validate convergence among honest nodes.
    """

    honest = chains[:2]

    # Check same length
    lengths = [len(c) for c in honest]
    if len(set(lengths)) != 1:
        return False

    # Check last block exists
    for c in honest:
        if not c:
            return False

    # Extract last hashes (using 'Hash' from Go)
    last_hashes = []
    for c in honest:
        last_block = c[-1]
        h = last_block.get("Hash")
        if not h:
            return False
        last_hashes.append(h)

    return len(set(last_hashes)) == 1