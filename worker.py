# Process responsible for processing tasks

from multiprocessing.managers import BaseManager
from time import sleep

# TODO: Load as parameters
# Server connection data
SERVER_ADRES = '127.0.0.1'
SERVER_PORT = 2332
SERVER_KEY = b'key'


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

while not tasks_queue.empty():
    task = tasks_queue.get()

    # Simulate task processing
    print('Working on task')
    sleep(1)
    print('Task done')

    results_queue.put(7)
    tasks_queue.task_done()
