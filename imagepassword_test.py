from itertools import combinations, product
from programs import ImagePassword

def make_combinations(likes, dislikes):
    result = []
    for p in product(combinations(dislikes, 3), likes):
        result.append(set(p[0] + (p[1],)))
    return result

combos = [make_combinations(d[0], d[1]) for d in ImagePassword._USER_INFO]

dups = []
for c1 in combos:
    for c2 in [c for c in combos if c is not c1]:
        dups.extend([c for c in c1 if c in c2])

if dups:
    print('Found duplicates: {}'.format(dups))
else:
    print('No duplicates')
