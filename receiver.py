import pika
import os
import sys
import json


def main():
    parameters = pika.URLParameters(os.environ.get('AMQP_URL', 'amqp://localhost?connection_attempts=5&retry_delay=5'))
    connection = pika.BlockingConnection(parameters=parameters)
    channel = connection.channel()

    queue = os.environ.get('QUEUE_NAME_RESPONSE', 'response_queue')
    channel.queue_declare(queue)

    def callback(ch, method, prop, body):
        print(' [x] Received: %r' % json.loads(body))

    channel.basic_consume(queue=queue, on_message_callback=callback, auto_ack=True)

    print(' [*] Waiting for messages. To exit prexx CTRL+C')
    channel.start_consuming()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
