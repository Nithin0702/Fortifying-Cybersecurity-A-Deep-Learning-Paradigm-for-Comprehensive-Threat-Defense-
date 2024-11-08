from kafka import KafkaConsumer
from json import loads
consumer = KafkaConsumer(
    'ids',
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='latest',
    enable_auto_commit=True,
    value_deserializer=lambda x: loads(x.decode('ISO-8859-1')))

for message in consumer:
    print(message.value)
