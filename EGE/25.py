sr = []
for a in "0123456789":
    for b in "0123456789":
        for c in "0123456789":
            s = a + b + c
            for i in range(4):
                for e in "0123456789":
                    res = "431" + s[i:] + "7" + e + "14"
                    res1 = int(res)
                    if res1 % 2026 == 0 and not (res1 in sr):
                        sr.append(res1)
                        print(res1, res1 // 2026)