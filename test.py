from kafka import KafkaProducer
import json
import nfstream
from os import getlogin, listdir

# device host name/ user name
device_name = getlogin()

# kafka server ip and port
bootstrap_server_ip = "localhost"
server_port = 9092

producer = KafkaProducer(bootstrap_servers=[bootstrap_server_ip + ":" + str(
	server_port)], key_serializer=str.encode, value_serializer=str.encode)
kafka_topic = "nids"

producer.send(kafka_topic, key=device_name, value="hello")