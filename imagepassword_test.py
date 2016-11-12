from itertools import combinations, product

DISLIKE_1 = {'A', 'B', 'C', 'D'}
LIKE_1 = {'G', 'H'}

DISLIKE_2 = {'A', 'B', 'E', 'F'}
LIKE_2 = {'C', 'D'}

DISLIKE_3 = {'A', 'C', 'J', 'I'}
LIKE_3 = {'E', 'D'}


def make_combinations(dislikes, likes):
    result = []
    for p in product(combinations(dislikes, 3), likes):
        result.append(set(p[0] + (p[1],)))
    return result

data = [(DISLIKE_1, LIKE_1), (DISLIKE_2, LIKE_2), (DISLIKE_3, LIKE_3)]
combos = [make_combinations(d[0], d[1]) for d in data]

dups = []
for c1 in combos:
    for c2 in [c for c in combos if c is not c1]:
        dups.extend([c for c in c1 if c in c2])

if dups:
    print('Found duplicates: {}'.format(dups))
else:
    print('No duplicates')
