# Process responsible for processing tasks
# Each tasks contains multiple jobs. Each job is a row of input matrix that needs to be
# multiplied by vector

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
vector = manager.get_vector().copy()

while not tasks_queue.empty():
    task = tasks_queue.get()

    # Simulate task processing
    print('Working on task')
    sleep(1)
    print('Task done')

    results_queue.put(7)
    tasks_queue.task_done()
