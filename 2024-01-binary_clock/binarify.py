from . import proper


tested_function = proper.binarify

test_cases = [
    (('18:57:31',), ' 1  0  0\n 0 11 00\n00 01 10\n10 11 11'),
    (('10:37:49',), ' 0  0  1\n 0 01 10\n00 11 00\n10 11 01'),
    (('07:24:16',), ' 0  0  0\n 1 01 01\n01 10 01\n01 00 10'),
]
