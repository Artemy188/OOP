# vPop
def f(s, m):
    if s >= 444: return m % 2 == 0
    if m == 0: return 0
    h = [f(s + 2, m - 1), f(s + 5, m - 1), f(s * 3, m - 1)]
    return any(h) if m % 2 else all(h)  # if in 19 "неудачно" => all->any


r = range(1, 401)
print(min(s for s in r if f(s, 2)))
print(*[s for s in r if f(s, 1) < f(s, 3)][:2])
print(max(s for s in r if f(s, 2) < f(s, 4)))