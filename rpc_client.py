#!/usr/bin/env python
import pika
import uuid
import json
import os
import random
from datetime import date, timedelta
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic


class VoucherRpcClient(object):
    def __init__(self):
        self.ampq_url = os.environ.get('AMQP_URL', 'amqp://localhost?connection_attempts=5&retry_delay=5')
        self.queue_name = os.environ.get('QUEUE_NAME', 'rpc_queue')
        self.prefetch_count = int(os.environ.get('PREFETCH_COUNT', 1))

        self.parameters = pika.URLParameters(self.ampq_url)
        self.connection = pika.BlockingConnection(self.parameters)
        self.channel = self.connection.channel()

        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True
        )

    def on_response(self, ch: BlockingChannel, method: Basic.Deliver, props: pika.BasicProperties, body: str) -> None:
        if self.corr_id == props.correlation_id:
            self.response = body

    @property
    def body(self):
        today = date.today()
        date_from = date(today.year, today.month, 1)
        date_to = date_from + timedelta(days=30)
        return {
            'id': random.randint(1, 9999999),
            'operational_plan': {
                'id': random.randint(1, 9999999),
                'sanatorium_id': random.randint(1, 999),
                'name': 'string',
                'date_from': date_from.strftime('%Y-%m-%d'),
                'date_to': date_to.strftime('%Y-%m-%d'),
                'department': {
                    'num_of_beds': 0,
                    'department_id': random.randint(1, 99),
                }
            },
            'plan_type': {
                'id': 0,
                'code': 0,
                'name': 'string',
            },
            'number_stay_days': {
                'id': 0,
                'count': 0,
                'name': 'string',
                'is_system': False,
            },
            'number_days_between_arrivals': 0,
            'non_arrival_days': {
                'code': 0,
                'name': 'string',
            },
            'sanitary_days': 0,
            'number_arrival_days': 0,
            'comment': 'string',
            'status': {
                'id': 0,
                'code': 0,
                'name': 'string',
            }
        }

    def call(self):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(
            exchange='',
            routing_key=self.queue_name,
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
            ),
            body=json.dumps(self.body),
        )
        while self.response is None:
            self.connection.process_data_events()
        return json.loads(self.response)


voucher_rpc = VoucherRpcClient()

print(' [x] Requesting...')
response = voucher_rpc.call()
print(' [.] Got %r' % response)
