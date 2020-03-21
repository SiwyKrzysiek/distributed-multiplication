# Process responsible for processing tasks
# Each tasks contains multiple jobs. Each job is a row of input matrix that needs to be
# multiplied by vector

from multiprocessing.managers import BaseManager
from multiprocessing import Pool
import queue
from sys import exit
from typing import Tuple, List
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-a', '--address', type=str,
                    help='Select server address. Defaults to localhost', default='127.0.0.1')
parser.add_argument('-p', '--serverPort', type=int,
                    help='Set server port', default=2332)
parser.add_argument('-k', '--key', type=str,
                    help='Set server key', default='key')
args = parser.parse_args()

# Server connection data
SERVER_ADRES = args.address
SERVER_PORT = args.serverPort
SERVER_KEY = args.key.encode()


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
    print("Nie udało się połączyć z serwerem")
    exit(-1)

tasks_queue = manager.get_tasks_queue()
results_queue = manager.get_results_queue()
vector = manager.get_vector().copy()
vector = [v[0] for v in vector]  # Flatten vector


def process_job(job: Tuple[int, List[float]]) -> Tuple[int, float]:
    """Process single job from task"""
    global vector

    result = sum(p[0] * p[1] for p in zip(job[1], vector))
    return (job[0], result)


# Create subprocess for each CPU core/thread
with Pool() as pool:
    while not tasks_queue.empty():
        try:
            task = tasks_queue.get()
        except queue.Empty:
            exit(0)

        # print('Working on task')
        # print(task)
        # sleep(1)
        finished_jobs = pool.map(process_job, task)
        # print('Task done')

        # print(finished_jobs)
        # print()

        results_queue.put(finished_jobs)
        tasks_queue.task_done()
