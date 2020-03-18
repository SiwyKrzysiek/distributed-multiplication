# Proces responsible for creating tasks and adding them to queues
# and processing received results

from sys import exit
from multiprocessing.managers import BaseManager

SERVER_ADRES = '127.0.0.1'
SERVER_PORT = 2332
SERVER_KEY = b'key'


class CalculationManager(BaseManager):
    """Shared manager class"""


CalculationManager.register('get_tasks_queue')
CalculationManager.register('get_results_queue')

manager = CalculationManager(
    address=(SERVER_ADRES, SERVER_PORT), authkey=SERVER_KEY)

try:
    manager.connect()
except ConnectionRefusedError:
    print("Nie udało się połączyć z serwerem")
    exit(-1)

tasks_queue = manager.get_tasks_queue()

# TODO: Load data, create tasks and enqueue them
