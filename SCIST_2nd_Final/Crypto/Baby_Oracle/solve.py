from pwn import *

r = remote('lab.scist.org', 7000)

ori_iv_cipher = bytes.fromhex(r.recvline().strip().split(b' = ')[1].decode())

def oracle(iv_cipher):
    r.sendlineafter(b'= ', iv_cipher.hex().encode())
    return b'Correct' in r.recvline()

iv = ori_iv_cipher[:16]
block_num = len(ori_iv_cipher) // 16 - 1

flag = b''

for k in range(block_num):
    plain = b''
    iv_cipher = ori_iv_cipher[16 * k: 16 * (k + 2)]
    for j in range(16):
        print(k, j)
        for i in range(256):
            new_iv_cipher = iv + b'a' * 15 + iv_cipher[-17 - j: -1 - j] + bytes([i])
            if oracle(new_iv_cipher) and (i != iv_cipher[-1 - j]):
                plain = bytes([i ^ 1 ^ iv_cipher[-1-j]]) + plain
                break
    flag += plain
    print(flag)

print(flag)

r.interactive()