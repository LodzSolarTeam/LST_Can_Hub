def shifting(bitlist):
    out = 0
    for bit in bitlist:
        out = (out << 1) | bit
    return out


