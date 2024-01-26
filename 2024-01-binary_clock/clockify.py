from . import one_liner, proper
from .binarify import test_cases


tested_functions = [('proper', proper.clockify), ('one liner', one_liner.clockify)]

test_cases = [((test_case[1],), test_case[0][0]) for test_case in test_cases]
