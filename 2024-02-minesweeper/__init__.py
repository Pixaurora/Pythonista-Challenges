from . import proper


tested_function = proper.find

test_cases = [
    ([(5, 8, 48.872), (12, 21, 35.107), (24, 20, 22.203)], (21, 13)),
    ([(18, 42, 35.558), (39, 16, 106.004), (7, 24, 32.202)], (8, 35)),
    ([(42, 19, 98.004), (3, 17, 122.484), (28, 29, 61.294)], (29, 50)),
]
