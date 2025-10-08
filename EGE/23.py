A = [0 for i in range(100)]
A[47] = 1
for i in range(46, 10, -1):
    if i != 22:
        A[i] = A[i + 2] + A[i + 5] + A[2 * i] + A[2 * i + 1]
print(A[11])