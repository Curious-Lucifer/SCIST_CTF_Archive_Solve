
def un_bitshift_right_xor(value: int, shift: int):
    """
    - input : `value (int)`, `shift (int)`
    - output : `result (int)` , `value = (result >> shift) ^ result`
    """

    i = 0
    result = 0
    while ((i * shift) < 32):
        partmask = int('1' * shift + '0' * (32 - shift), base = 2) >> (shift * i)
        part = value & partmask
        value ^= (part >> shift)
        result |= part
        i += 1
    return result

def un_bitshift_left_xor_mask(value: int, shift: int, mask: int):
    """
    - input : `value (int)`, `shift (int)`, `mask (int)`
    - output : `result (int)` , `value = ((result << shift) & mask) ^ result`
    """

    i = 0
    result = 0
    while ((i * shift) < 32):
        partmask = int('0' * (32 - shift) + '1' * shift, base = 2) << (shift * i)
        part = value & partmask
        value ^= (part << shift) & mask
        result |= part
        i += 1
    return result

def rand_to_state(value: int):
    """
    - input : `value (int)`
    - output : `value (int)` , for MT19937
    """

    value = un_bitshift_right_xor(value, 18)
    value = un_bitshift_left_xor_mask(value, 15, 0xefc60000)
    value = un_bitshift_left_xor_mask(value, 7, 0x9d2c5680)
    value = un_bitshift_right_xor(value, 11)
    return value

def state_to_rand(value: int):
        """
        - input : `value (int)`
        - output : `value (int)` , for MT19937
        """

        value ^= (value >> 11)
        value ^= (value << 7) & 0x9d2c5680
        value ^= (value << 15) & 0xefc60000
        value ^= (value >> 18)
        return value

def calc(xor_state0, xor_state1, xor_state2, xor_state3):
    xor_state = xor_state0 + xor_state1 + xor_state2
    pre_shift_xor_state = []
    for i in range(1, 624):
        y = xor_state[i] & 0x7fffffff
        next = y >> 1
        next ^= xor_state[i + 198]
        if ((y & 1) == 1):
            next ^= 0x9908b0df
        pre_shift_xor_state.append(next)
    
    xor_state = xor_state1 + xor_state2 + xor_state3
    shift_xor_state = []
    for i in range(312):
        y = (xor_state[113 + i] & 0x80000000) + (pre_shift_xor_state[113 + i] & 0x7fffffff)
        next = y >> 1
        next ^= pre_shift_xor_state[311 + i]
        if ((y & 1) == 1):
            next ^= 0x9908b0df

        if (next & 0x40000000) != (xor_state[312 + 113 + i] & 0x40000000):
            shift_xor_state.append(pre_shift_xor_state[311 + i] ^ 0x40000000)
        else:
            shift_xor_state.append(pre_shift_xor_state[311 + i])
    
    return xor_state2.copy(), shift_xor_state

def gen_next_xor_state(xor_state, shift_xor_state):
    xor_state = xor_state.copy()
    shift_xor_state = shift_xor_state.copy()
    for i in range(312):
        y = (shift_xor_state[i] & 0x80000000) + (xor_state[i] & 0x7fffffff)
        next = y >> 1
        next ^= xor_state[198 + i]
        if ((y & 1) == 1):
            next ^= 0x9908b0df
        shift_xor_state.append(next)

        y = (xor_state[i] & 0x80000000) + (shift_xor_state[i + 1] & 0x7fffffff)
        next = y >> 1
        next ^= shift_xor_state[199 + i]
        if ((y & 1) == 1):
            next ^= 0x9908b0df
        xor_state.append(next)
    
    return xor_state[312:], shift_xor_state[312:]


from pwn import *
from tqdm import trange

r = remote('lab.scist.org', 7001)

def get_rand():
    r.sendline(b'0')
    return int(r.recvline().strip().split(b': ')[1].decode())

xor_state0 = []
for i in trange(312):
    xor_state0.append(rand_to_state(get_rand()))
xor_state1 = []
for i in trange(312):
    xor_state1.append(rand_to_state(get_rand()))
xor_state2 = []
for i in trange(312):
    xor_state2.append(rand_to_state(get_rand()))
xor_state3 = []
for i in trange(312):
    xor_state3.append(rand_to_state(get_rand()))

xor_state, xor_shift_state = calc(xor_state0, xor_state1, xor_state2, xor_state3)
xor_state, xor_shift_state = gen_next_xor_state(xor_state, xor_shift_state)
xor_state, xor_shift_state = gen_next_xor_state(xor_state, xor_shift_state)

for i in trange(49):
    r.sendline(str(state_to_rand(xor_state[i])).encode())
    assert b'correct' in r.recvline()

r.sendline(str(state_to_rand(xor_state[49])).encode())

r.interactive()
