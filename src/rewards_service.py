import logging

from rewards.rewards_engine import RewardsEngine
from queue.queue_service import QueueService

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)


def main():
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
    queueService = QueueService('amqp://guest:guest@localhost:5672/', 'rewards', 'rewards')

    queueService.set_message_handler(RewardsEngine(queueService))

    try:
        queueService.run()
    except KeyboardInterrupt:
        queueService.stop()


if __name__ == '__main__':
    main()
