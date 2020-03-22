# Proces responsible for creating tasks and adding them to queues
# and processing received results

from sys import exit
from multiprocessing.managers import BaseManager
from typing import List, Tuple, Iterable
import math
import argparse
import time

parser = argparse.ArgumentParser()
parser.add_argument('-a', '--address', type=str,
                    help='Select server address. Defaults to localhost', default='127.0.0.1')
parser.add_argument('-p', '--serverPort', type=int,
                    help='Set server port', default=2332)
parser.add_argument('-k', '--key', type=str,
                    help='Set server key', default='key')
parser.add_argument('-t', '--tasks', type=int,
                    help='Number of tasks that will be created', default=8)
parser.add_argument('-o', '--output', type=str,
                    help='Path to file in which to store results. If not provided vector is just displayed.')
parser.add_argument('matrix', type=str, help='Path to file with input matrix')
parser.add_argument('vector', type=str, help='Path to file with input vector')
args = parser.parse_args()

# Server connection data
SERVER_ADRES = args.address
SERVER_PORT = args.serverPort
SERVER_KEY = args.key.encode()

# File data
MATRIX_FILE_NAME = args.matrix
VECTOR_FILE_NAME = args.vector

TASK_COUNT = args.tasks


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
    print(
        f'Connecting to server {SERVER_ADRES}:{SERVER_PORT} with key "{SERVER_KEY.decode()}"')
    manager.connect()
except ConnectionRefusedError:
    print("Can't connect to the server")
    exit(-1)

tasks_queue = manager.get_tasks_queue()
results_queue = manager.get_results_queue()
vektor = manager.get_vector()

print(f'Loading matrix from file {MATRIX_FILE_NAME}')
start = time.time()
matrix = loadMatrix(MATRIX_FILE_NAME)
matrix_load_time = time.time() - start
print(f'Loading matrix took {matrix_load_time} s')

# Save vector to shared memory
print(f'Loading vector from file {VECTOR_FILE_NAME}')
vektor.clear()
start = time.time()
vektor.extend(loadMatrix(VECTOR_FILE_NAME))
vector_load_time = time.time() - start
print(f'Loading vector took {vector_load_time} s')

# ---------- Create tasks ---------- #
# Matrix will be divided into groups of rows to multiply
# Single task is a list of pairs of row number in original matrix and row data
# Worker can multiply matrix row and vectro from shared memory to create singe value of result


def create_tasks(matrix, taks_count) -> Iterable[tuple]:
    for row_range in split_to_ranges(len(matrix), taks_count):
        yield [(j, matrix[j]) for j in range(*row_range)]


print(f"Splitting calculation into {TASK_COUNT} tasks")
start = time.time()
for task in create_tasks(matrix, TASK_COUNT):
    tasks_queue.put(task)
task_creation_time = time.time() - start
print(f'Creating tasks took {task_creation_time} s')
start = time.time()

print('Waiting for workers to process tasks')
tasks_queue.join()
calculation_time = time.time() - start
print(f'Calculations took {calculation_time} s')

print('All tasks are done')

# Join results to output vector
start = time.time()
result = [0] * len(matrix)
while not results_queue.empty():
    task_result = results_queue.get()
    for job_result in task_result:
        i, value = job_result
        result[i] = value
result_assemble_time = time.time() - start
print(f'Assembling result vector took {result_assemble_time} s')

if not args.output:
    print('Output vector:')
    print(result)
else:
    with open(args.output, 'w') as file:
        file.write(str(len(result)) + '\n')
        file.write('1\n')
        for v in result:
            file.write(str(v) + '\n')
