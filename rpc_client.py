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
        date_from = date(today.year, 1, 1)
        date_to = date(today.year, 4, 9)
        plan_type_code = random.randint(1, 2)
        plan_type_names = ['Ежедневный', 'Заездный']
        return {
            'id': random.randint(1, 9999999),
            'operational_plan': {
                'id': random.randint(1, 9999999),
                'sanatorium_id': random.randint(1, 999),
                'name': 'string',
                'date_from': date_from.strftime('%Y-%m-%d'),
                'date_to': date_to.strftime('%Y-%m-%d'),
                'department': {
                    'num_of_beds': 300,
                    'department_id': random.randint(1, 99),
                }
            },
            'plan_type': {
                'id': plan_type_code,
                'code': plan_type_code,
                'name': plan_type_names[plan_type_code - 1],
            },
            'number_stay_days': {
                'id': random.randint(1, 99999),
                'count': 14,
                'name': '14 дней',
                'is_system': True,
            },
            'number_days_between_arrivals': 1,
            'non_arrival_days': [
                {
                    'id': random.randint(1, 9999),
                    'code': 1,
                    'name': 'пн',
                },
                {
                    'id': random.randint(1, 9999) + 1,
                    'code': 2,
                    'name': 'вт',
                },
            ],
            'sanitary_days': 2,
            'number_arrival_days': 5,
            'comment': None,
            'status': {
                'id': 2,
                'code': 2,
                'name': 'На согласовании в санатории',
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
count = 1
while not response['success']:
    count += 1
    if count > 10:
        break
    print(' [.] Error: %s' % response['data']['error_msg'])
    print(' [x] Trying request %i...' % count)
    response = voucher_rpc.call()
if response['success']:
    print(' [.] Got %i arrivals' % len(response['data']))
    print(' [.] Got %r' % response)
else:
    print(' [.] No correct response data')
