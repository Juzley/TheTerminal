"""A test tool to check the visual password program has unique solutions."""
from itertools import combinations
from programs import ImagePassword

# Find duplicates
combos = [combinations(c, 3) for c in ImagePassword._USER_INFO]

dups = []
for c1 in combos:
    for c2 in [c for c in combos if c is not c1]:
        dups.extend([c for c in c1 if c in c2])

if dups:
    print('Found duplicates: {}'.format(dups))
else:
    print('No duplicates')

# Find the number of times each category appears in the puzzle
distribution = {}
for i in ImagePassword._USER_INFO:
    for c in i:
        if c.name not in distribution:
            distribution[c.name] = 1
        else:
            distribution[c.name] += 1

print(distribution)
