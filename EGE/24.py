f = open("24.txt", 'r')
s = f.readline()
ans = len(s)
for i in range(len(s)):
    if s[i] == 'B':
        curr = 1
        state = 1
        for j in range(i + 1, len(s)):
            curr += 1
            if not s[j] in "AB1":
                if state == 1:
                    state = 2
                if state == 3:
                    break
                if state == 4:
                    break
                if state == 5:
                    state = 6
            else:
                if s[j] == "1":
                    if state == 3:
                        state = 4
                    else:
                        break
                elif s[j] == "B":
                    if state == 6:
                        ans = min(ans, curr)
                    break
                else:
                    if state == 2:
                        state = 3
                    elif state == 4:
                        state = 5
                    else:
                        break
print(ans)