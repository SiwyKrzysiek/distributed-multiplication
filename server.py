# Proces responsible for creating shared queues

from multiprocessing import Queue, JoinableQueue
from multiprocessing.managers import BaseManager

# Server settings
SERVER_PORT = 2332
SERVER_KEY = b'key'


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
