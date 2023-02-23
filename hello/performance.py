# import hello.utils as utils


# utils.create_files()

# using time module
import time
import sys

def perf_checker(id: str = 'NA', process: str = 'NA'):
    # print(f"{process}:{id}")
    start_time = 0

    def start():
        global start_time
        start_time = time.time()

    def lap(step):
        global start_time
        print(f"{process}:{id}:{step} took {time.time() - start_time}")
        sys.stdout.flush()
        start_time = time.time()

    return (start, lap)