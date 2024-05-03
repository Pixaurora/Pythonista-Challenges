import logging
import gc
import sys

from benchmark.errors import IncorrectOutput

from .config import DisplayMethod, Test, TestedFunction, setup


log = logging.getLogger(__name__)


def main(tested_functions: list[tuple[str, TestedFunction]], test_cases: list[Test], display_method: DisplayMethod, project_name: str):
    for title, tested_function in tested_functions:
        implementation_name: str = f"{title} " if title else ""
        implementation_name += "implementation"

        print(f'=== Testing {implementation_name} for {project_name} ===')

        for case_id, test in enumerate(test_cases, start=1):
            print(f'Test #{case_id} result: ', end='')

            try:
                gc.disable()
                print(f'Success! Took {test.benchmark(tested_function) * 1000} ms on average to complete!')
            except IncorrectOutput as output:
                output = output.format(display_method)
                print('Failure! Unexpected output.', 'Input:', *test.args, 'Expected:', output.expected, 'Actual:', output.actual, sep='\n')
            except Exception as e:
                print('Failure! Raised an exception.')
                log.error('Showing exception', exc_info=e)
            finally:
                gc.enable()
                gc.collect()


usage: str = 'Usage: `benchmark <module_name> <test_repetitions=1_000_000>`'

if len(sys.argv) < 2:
    print(usage)

module_name: str = sys.argv[1]

test_repetitions: int
if len(sys.argv) > 2:
    try:
        test_repetitions = int(sys.argv[2])
    except ValueError:
        print(f'Argument 2 must be readable as an integer!\n{usage}')
        exit()
else:
    test_repetitions = 1_000_000

project_name = module_name[module_name.rfind('-') + 1 :].replace('_', ' ')

main(*setup(module_name, test_repetitions), project_name)
