
def u16_to_bytesLE(u16):
    return bytearray([(u16 & 0xFF), ((u16 >> 8) & 0xFF)])

def u32_to_bytesLE(u32):
    return bytearray([(u32 & 0xFF), ((u32 >> 8) & 0xFF), ((u32 >> 16) & 0xFF), ((u32 >> 24) & 0xFF)])

def u64_to_bytesLE(u64):
    return bytearray([(u64 & 0xFF), ((u64 >> 8) & 0xFF), ((u64 >> 16) & 0xFF), ((u64 >> 24) & 0xFF),
                      ((u64 >> 32) & 0xFF), ((u64 >> 40) & 0xFF), ((u64 >> 48) & 0xFF), ((u64 >> 56) & 0xFF)])

def packetCheckSum(pkt_all):    
    pkt_sum = (0x100 - (sum(pkt_all) & 0xFF)) & 0xFF
    return pkt_sum

def hexStrToByteArray(text1: str) -> bytearray:
    len1 = len(text1)
    #data = bytearray.fromhex(text1)
    #---hex string to hex bytes
    dataBytes = bytearray()
    i = 0
    while(i < len1):
        if(i % 2 == 0):
            dataBytes.append((int(text1[i], 16) << 4))
        else:
            dataBytes[-1] += int(text1[i], 16)                
        i += 1

    return dataBytes