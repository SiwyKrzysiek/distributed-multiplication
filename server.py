# Proces responsible for creating shared queues

from multiprocessing import Queue, JoinableQueue
from multiprocessing.managers import BaseManager
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--port', type=int,
                    help='Set server port', default=2332)
parser.add_argument('-k', '--key', type=str,
                    help='Set server key', default='key')
args = parser.parse_args()

# Server settings
SERVER_PORT = args.port
SERVER_KEY = args.key.encode()

print(
    f'Starting server on port {SERVER_PORT} with key "{SERVER_KEY.decode()}"')


class CalculationManager(BaseManager):
    """Shared manager class"""


tasks_queue = JoinableQueue()
results_queue = Queue()
vector = []
CalculationManager.register(
    'get_tasks_queue', callable=lambda: tasks_queue)
CalculationManager.register(
    'get_results_queue', callable=lambda: results_queue)

# Shared memory to distribute vector in order not to duplicate data
CalculationManager.register(
    'get_vector', callable=lambda: vector)

manager = CalculationManager(address=('', SERVER_PORT), authkey=SERVER_KEY)
server = manager.get_server()
server.serve_forever()
