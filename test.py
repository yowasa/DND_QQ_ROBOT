t = list(range(10))
step = 3
b = [t[i:i + step] for i in range(0, len(t), step)]
print(b)
