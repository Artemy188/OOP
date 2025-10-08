f = open("17.txt", 'r')
A = []
for line in f.readlines():
    A.append(int(line))
el = 1000000
for i in A:
    if len(str(i)) == 3:
        if i % 10 == 9:
            el = min(el, i)
ans = 0
res = 0
for i in range(len(A) - 1):
    a = A[i]
    b = A[i + 1]
    if len(str(a)) == 2 or len(str(b)) == 2:
        if (a + b) % el == 0:
            ans += 1
            res = max(res, a + b)
print(ans, res)