import math


def cosine_similarity(a, b):
    nokta_carpimi = sum(x * y for x, y in zip(a, b))
    a_boyu = math.sqrt(sum(x * x for x in a))
    b_boyu = math.sqrt(sum(y * y for y in b))
    return nokta_carpimi / (a_boyu * b_boyu)
