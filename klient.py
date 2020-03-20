# Proces responsible for creating tasks and adding them to queues
# and processing received results

from sys import exit
from multiprocessing.managers import BaseManager
from typing import List

# TODO: Load as parameters
# Server connection data
SERVER_ADRES = '127.0.0.1'
SERVER_PORT = 2332
SERVER_KEY = b'key'

# File data
MATRIX_FILE_NAME = 'A.dat'
VECTOR_FILE_NAME = 'X.dat'


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


class CalculationManager(BaseManager):
    """Shared manager class"""


CalculationManager.register('get_tasks_queue')
CalculationManager.register('get_results_queue')

CalculationManager.register('get_wektor')

manager = CalculationManager(
    address=(SERVER_ADRES, SERVER_PORT), authkey=SERVER_KEY)

try:
    manager.connect()
except ConnectionRefusedError:
    print("Nie udało się połączyć z serwerem")
    exit(-1)

tasks_queue = manager.get_tasks_queue()
wektor = manager.get_wektor()

# TODO: Load data, create tasks and enqueue them
matrix = loadMatrix(MATRIX_FILE_NAME)
print(len(matrix))
print(len(matrix[0]))
# print(matrix)
