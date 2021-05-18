answer = [2, 3, 5, 7, 9]
for i in answer:
    for j in answer:
        for k in answer:
            for l in answer:
                for m in answer:
                    if i + j * k**2 + l**3 - m == 399:
                        print(i, j, k, l, m)
                        # exit()

# 9 2 5 7 3