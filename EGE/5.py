def tr(a):
    ans = ""
    while a > 0:
        ans += str(a % 3)
        a //= 3
    return int(ans[::-1])
def antitr(a):
    a = str(a)
    a = a[::-1]
    ans = 0
    pow = 0
    for i in a:
        ans += int(i) * (3 ** pow)
        pow += 1
    return ans
for i in range(1, 100):
    b = tr(i)
    b = str(b)
    if i % 5 == 0:
        b = b + b[len(b) - 2:]
    else:
        b += str(tr((i % 5) * 7))
    if antitr(int(b)) <= 273:
        print(i)
