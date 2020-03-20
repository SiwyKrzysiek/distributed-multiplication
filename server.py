# Proces responsible for creating shared queues

from multiprocessing import Queue
from multiprocessing.managers import BaseManager

SERVER_PORT = 2332
SERVER_KEY = b'key'


class CalculationManager(BaseManager):
    """Shared manager class"""


tasks_queue = Queue()
results_queue = Queue()
CalculationManager.register(
    'get_tasks_queue', callable=lambda: tasks_queue)
CalculationManager.register(
    'get_results_queue', callable=lambda: results_queue)

manager = CalculationManager(address=('', SERVER_PORT), authkey=SERVER_KEY)
server = manager.get_server()
server.serve_forever()