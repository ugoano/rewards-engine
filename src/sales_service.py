import json
import logging
import random
from queue.queue_service import QueueService

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)

USER_IDS = [12345, 76543, 234567, 987654, 23456, 87654]


def generate_sale():
    return {
        'type': 'sale',
        'item_id': random.randint(1, 20),
        'cost': (random.randint(100, 2000)/100),
        'currency': 'GBP',
        'user_id': random.choice(USER_IDS)
    }


class SalesService(QueueService):

    def on_bindok(self, unused_frame):
        """This method is invoked by pika when it receives the Queue.BindOk
        response from RabbitMQ. Since we know we're now setup and bound, it's
        time to start publishing."""
        self.send_message()

    def schedule_next_message(self):
        self._connection.add_timeout(1, self.send_message)

    def send_message(self):
        message = generate_sale()
        LOGGER.info('Generated sale %s', message)
        self._channel.basic_publish(
            self.EXCHANGE,
            self.QUEUE,
            json.dumps(message, ensure_ascii=False),
            self.DEFAULT_MESSAGE_PROPERTY
        )
        self.schedule_next_message()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
    service = SalesService('amqp://guest:guest@localhost:5672/', 'sales', 'sales')
    try:
        service.run()
    except KeyboardInterrupt:
        service.stop()
