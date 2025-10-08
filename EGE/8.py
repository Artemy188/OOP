cnt = 0
ans = 0
word = ""
for a in "АБИНОРТУ":
    for b in "АБИНОРТУ":
        for c in "АБИНОРТУ":
            for d in "АБИНОРТУ":
                for e in "АБИНОРТУ":
                    cnt += 1
                    tool = set()
                    tool.add(a)
                    tool.add(b)
                    tool.add(c)
                    tool.add(d)
                    tool.add(e)
                    if not (a  in "АИОУ") and len(tool) == 5 and cnt % 2 == 1:
                        ans = cnt
                        word = a + b + c + d + e
print(ans)
print(word)
