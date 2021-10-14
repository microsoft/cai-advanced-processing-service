from SpellingResolver import test_spelling_resolver

mm = [
    'anton marta 123',
    'siegfried dora 2 * 7',
    'toni berta 22',
    'd e 3 times 7 2 times 3'
]

ll = [
    'am123',
    'sd77',
    'tb22',
    'de77733'
]

def test():
    for r, resolved in zip(mm, ll):
        assert test_spelling_resolver(r) == resolved