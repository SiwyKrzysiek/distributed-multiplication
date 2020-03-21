# Proces responsible for creating tasks and adding them to queues
# and processing received results

from sys import exit
from multiprocessing.managers import BaseManager
from typing import List, Tuple, Iterable
import math

# TODO: Load as parameters
# Server connection data
SERVER_ADRES = '127.0.0.1'
SERVER_PORT = 2332
SERVER_KEY = b'key'

# File data
MATRIX_FILE_NAME = 'smallA.dat'
VECTOR_FILE_NAME = 'smallX.dat'

TASK_COUNT = 5


def loadMatrix(file_name: str) -> List[List[float]]:
    """
    Import matrix from file.
    Matrix is stored in row oriented list.
    Such that each row is a nested list.
    """

    with open(file_name, 'r') as file:
        row_count = int(file.readline())
        column_count = int(file.readline())

        return [[float(file.readline()) for _ in range(column_count)]
                for _ in range(row_count)]


def split_to_ranges(vector_lenght: int, range_count: int) -> List[Tuple[int, int]]:
    """
    Divide single range into rangeCount parts. Each part takes form of [a, b)
    Example: splitIntoRanges(10, 3) => [0, 4), [4, 8), [8, 10)
    """
    part_size = math.ceil(vector_lenght / range_count)

    ranges = []
    index = 0
    for _ in range(range_count):
        if index < vector_lenght:
            r = index, min(index + part_size, vector_lenght)

            ranges.append(r)
            index = r[1]
        else:  # There are more ranges than vector length
            ranges.append((0, 0))

    return ranges


class CalculationManager(BaseManager):
    """Shared manager class"""


CalculationManager.register('get_tasks_queue')
CalculationManager.register('get_results_queue')

CalculationManager.register('get_vector')

manager = CalculationManager(
    address=(SERVER_ADRES, SERVER_PORT), authkey=SERVER_KEY)

try:
    manager.connect()
except ConnectionRefusedError:
    print("Nie udało się połączyć z serwerem")
    exit(-1)

tasks_queue = manager.get_tasks_queue()
results_queue = manager.get_results_queue()
vektor = manager.get_vector()

# TODO: Load data, create tasks and enqueue them
matrix = loadMatrix(MATRIX_FILE_NAME)

# Save vector to shared memory
vektor.clear()
vektor.extend(loadMatrix(VECTOR_FILE_NAME))

# ---------- Create tasks ---------- #
# Matrix will be divided into groups of rows to multiply
# Single task is a list of pairs of row number in original matrix and row data
# Worker can multiply matrix row and vectro from shared memory to create singe value of result


def create_tasks(matrix, taks_count) -> Iterable[tuple]:
    for row_range in split_to_ranges(len(matrix), taks_count):
        yield [(j, matrix[j]) for j in range(*row_range)]


print("Created tasks:")
for task in create_tasks(matrix, TASK_COUNT):
    print(task)
    tasks_queue.put(task)

print("Waiting for workers to process tasks")
tasks_queue.join()

print('All tasks are done')

# Join results to output vector
result = [0] * len(matrix)
while not results_queue.empty():
    task_result = results_queue.get()
    for job_result in task_result:
        i, value = job_result
        result[i] = value

print('Output vector:')
print(result)
