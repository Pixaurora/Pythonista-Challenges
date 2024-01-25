from . import proper
from .binarify import test_cases


tested_function = proper.clockify

test_cases = [((test_case[1],), test_case[0][0]) for test_case in test_cases]
