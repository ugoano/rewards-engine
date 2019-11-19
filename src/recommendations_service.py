import logging

from queue.queue_service import QueueService


LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)

class RecommendationEngine:

    def __init__(self, queueService):
        self._queueService= queueService

    def on_message(self, body):
        LOGGER.info(f'RECOMMENDATIONS ENGINE {body}')


def main():
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
    queueService = QueueService(
        'amqp://guest:guest@localhost:5672/',
        'rewards-recommendation', 'rewards-recommendation'
    )
    queueService.set_message_handler(RecommendationEngine(queueService))

    try:
        queueService.run()
    except KeyboardInterrupt:
        queueService.stop()


if __name__ == '__main__':
    main()
