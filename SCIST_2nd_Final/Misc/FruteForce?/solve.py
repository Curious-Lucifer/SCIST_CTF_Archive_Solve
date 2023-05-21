from gmpy2 import iroot

x_test = []
y_test = []

for i in range(600):
    if (256325 - i ** 2) <= 0:
        break
    if iroot(256325 - i ** 2, 2)[1]:
        x_test.append(i)
        y_test.append(int(iroot(256325 - i**2, 2)[0]))

for x, y in zip(x_test, y_test):
    if ((y * 13910 + 441) % x) != 0:
        continue
    z = (y * 13910 + 441) // x
    if ((3 ** x) != (y ** 3 - z)):
        continue

    print('SCIST{' + str(y ** x % z) + '}')