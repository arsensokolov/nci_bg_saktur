import pika
import json
import os
import random
from datetime import date


class VoucherTaskPublisher(object):
    def __init__(self):
        self.ampq_url = os.environ.get('AMQP_URL', 'amqp://localhost?connection_attempts=5&retry_delay=5')
        self.queue_name = os.environ.get('QUEUE_NAME_REQUEST', 'request_queue')

        self.parameters = pika.URLParameters(self.ampq_url)
        self.connection = pika.BlockingConnection(self.parameters)
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue_name)

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

    def send(self):
        self.channel.basic_publish(
            exchange='',
            routing_key=self.queue_name,
            body=json.dumps(self.body),
        )
        self.connection.close()


if __name__ == '__main__':
    voucher_task = VoucherTaskPublisher()
    print(' [x] Sending task...')
    voucher_task.send()
    print(' [x] Done!')
