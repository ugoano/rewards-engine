import logging
import pika

LOGGER = logging.getLogger(__name__)


class QueueService(object):
    EXCHANGE = None
    QUEUE = None
    EXCHANGE_TYPE = 'direct'
    DEFAULT_MESSAGE_PROPERTY = pika.BasicProperties(app_id='verve', content_type='text/json', delivery_mode=1)

    def __init__(self, amqp_url, exchange, queue):
        self._connection = None
        self._channel = None
        self._closing = False
        self._consumer_tag = None
        self._url = amqp_url
        self.EXCHANGE = exchange
        self.QUEUE = queue

    def connect(self):
        LOGGER.debug('Connecting to %s', self._url)
        return pika.SelectConnection(pika.URLParameters(self._url),
                                     self.on_connection_open,
                                     stop_ioloop_on_close=False)

    def on_connection_open(self, unused_connection):
        LOGGER.debug('Connection opened')
        self.add_on_connection_close_callback()
        self.open_channel()

    def add_on_connection_close_callback(self):
        LOGGER.debug('Adding connection close callback')
        self._connection.add_on_close_callback(self.on_connection_closed)

    def on_connection_closed(self, connection, reply_code, reply_text):
        self._channel = None
        if self._closing:
            self._connection.ioloop.stop()
        else:
            LOGGER.warning('Connection closed, reopening in 5 seconds: (%s) %s',
                           reply_code, reply_text)
            self._connection.add_timeout(5, self.reconnect)

    def reconnect(self):
        self._connection.ioloop.stop()

        if not self._closing:
            # Create a new connection
            self._connection = self.connect()

            # There is now a new connection, needs a new ioloop to run
            self._connection.ioloop.start()

    def open_channel(self):
        LOGGER.debug('Creating a new channel')
        self._connection.channel(on_open_callback=self.on_channel_open)

    def on_channel_open(self, channel):
        LOGGER.debug('Channel opened')
        self._channel = channel
        self.add_on_channel_close_callback()
        self.setup_exchange(self.EXCHANGE)

    def add_on_channel_close_callback(self):
        LOGGER.debug('Adding channel close callback')
        self._channel.add_on_close_callback(self.on_channel_closed)

    def on_channel_closed(self, channel, reply_code, reply_text):
        LOGGER.warning('Channel %i was closed: (%s) %s',
                       channel, reply_code, reply_text)
        self._connection.close()

    def setup_exchange(self, exchange_name):
        LOGGER.debug('Declaring exchange %s', exchange_name)
        self._channel.exchange_declare(self.on_exchange_declareok,
                                       exchange_name,
                                       self.EXCHANGE_TYPE,
                                       False,
                                       True)

    def on_exchange_declareok(self, unused_frame):
        LOGGER.debug('Exchange declared')
        self.setup_queue(self.QUEUE)

    def setup_queue(self, queue_name):
        LOGGER.debug('Declaring queue %s', queue_name)
        self._channel.queue_declare(self.on_queue_declareok, queue_name, False, True)

    def on_queue_declareok(self, method_frame):
        LOGGER.debug('Binding %s to %s with %s',
                    self.EXCHANGE, self.QUEUE, self.QUEUE)
        self._channel.queue_bind(self.on_bindok, self.QUEUE,
                                 self.EXCHANGE, self.QUEUE)

    def on_bindok(self, unused_frame):
        LOGGER.debug('Queue bound')
        self.start_consuming()

    def start_consuming(self):
        LOGGER.debug('Issuing consumer related RPC commands')
        self.add_on_cancel_callback()
        self._consumer_tag = self._channel.basic_consume(self.on_message,
                                                         'sales', )

    def add_on_cancel_callback(self):
        LOGGER.debug('Adding consumer cancellation callback')
        self._channel.add_on_cancel_callback(self.on_consumer_cancelled)

    def on_consumer_cancelled(self, method_frame):
        LOGGER.debug('Consumer was cancelled remotely, shutting down: %r',
                    method_frame)
        if self._channel:
            self._channel.close()

    def acknowledge_message(self, delivery_tag):
        LOGGER.debug('Acknowledging message %s', delivery_tag)
        self._channel.basic_ack(delivery_tag)

    def stop_consuming(self):
        if self._channel:
            LOGGER.debug('Sending a Basic.Cancel RPC command to RabbitMQ')
            self._channel.basic_cancel(self.on_cancelok, self._consumer_tag)

    def on_cancelok(self, unused_frame):
        LOGGER.debug('RabbitMQ acknowledged the cancellation of the consumer')
        self.close_channel()

    def close_channel(self):
        LOGGER.debug('Closing the channel')
        self._channel.close()

    def run(self):
        self._connection = self.connect()
        self._connection.ioloop.start()

    def stop(self):
        LOGGER.debug('Stopping')
        self._closing = True
        self.stop_consuming()
        self._connection.ioloop.start()
        LOGGER.debug('Stopped')

    def close_connection(self):
        """This method closes the connection to RabbitMQ."""
        LOGGER.debug('Closing connection')
        self._connection.close()

    def set_message_handler(self, callback):
        self._callback = callback

    def on_message(self, channel, basic_deliver, properties, body):
        LOGGER.debug('Received message # %s from %s: %s',
                    basic_deliver.delivery_tag, properties.app_id, body)

        if self._callback:
            self._callback.on_message(body)

        self.acknowledge_message(basic_deliver.delivery_tag)

    # Simple Send method to send a response back to the Event Log.
    def send_message(self, body):
        exchange = self.EXCHANGE
        routing_key = self.QUEUE
        properties = self.DEFAULT_MESSAGE_PROPERTY
        mandatory = True

        if self._channel.basic_publish(exchange, routing_key, body, properties, mandatory):
            return True
        else:
            return False
