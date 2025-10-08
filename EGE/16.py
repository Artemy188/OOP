g = [0 for i in range(30004)]
f = [0 for j in range(30005)]
g[30003] = 3
g[30002] = 3
g[30001] = 3
g[30000] = 3
for i in range(29999, 0, -1):
    g[i] = g[i + 3] + 7
    f[i] = g[i + 1]
print(f[1500])