# Process responsible for processing tasks
# Each tasks contains multiple jobs. Each job is a row of input matrix that needs to be
# multiplied by vector

from multiprocessing.managers import BaseManager
from multiprocessing import Pool
from time import sleep
from typing import Tuple, List

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

vector = [v[0] for v in vector]  # Flatten vector

print('vector: ' + str(vector))


def process_job(job: Tuple[int, List[float]]) -> Tuple[int, float]:
    """Process single job from task"""
    global vector

    result = sum(p[0] * p[1] for p in zip(job[1], vector))
    return (job[0], result)


# Create subprocess for each CPU core/thread
pool = Pool()

while not tasks_queue.empty():
    task = tasks_queue.get()

    # Simulate task processing
    print('Working on task')
    print(task)
    # sleep(1)
    finished_jobs = pool.map(process_job, task)
    print('Task done')

    print(finished_jobs)
    print()

    results_queue.put(finished_jobs)
    tasks_queue.task_done()

pool.close()
