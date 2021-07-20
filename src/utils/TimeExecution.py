from functools import wraps
from time import time


def time_exec(func: callable):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time()
        execution_result = func(*args, **kwargs)
        execution_time = time() - start_time
        print(f"Execution time for {func.__name__}:", execution_time)
        return execution_result

    return wrapper
