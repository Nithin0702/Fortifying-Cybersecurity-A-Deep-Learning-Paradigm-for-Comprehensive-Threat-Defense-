from kafka import KafkaProducer
import json
import nfstream
from os import getlogin, listdir
# PvGQtA5z
# device host name/ user name
device_name = getlogin()

# kafka server ip and port
bootstrap_server_ip = "localhost"
server_port = 9092

producer = KafkaProducer(bootstrap_servers = [bootstrap_server_ip + ":" + str(server_port)],key_serializer=str.encode,value_serializer=str.encode)
kafka_topic = "nids"

network_interfaces = listdir("/sys/class/net/")
network_interfaces.remove("lo")

for i in range(len(network_interfaces)):
	print(f"{i+1} : {network_interfaces[i]}")

user_input = int(input(f"Select one network interface:"))
print(f"http://{bootstrap_server_ip}")

live_capture = nfstream.NFStreamer(
	source=network_interfaces[user_input-1], statistical_analysis=False, promiscuous_mode=True, idle_timeout=10)
print("sending data to kafka")

count = 1

for packet in live_capture:
	data = f"{str(time())},{packet.src_port},{packet.dst_port},{packet.protocol},{packet.bidirectional_packets},{packet.bidirectional_bytes},{packet.src2dst_duration_ms},{packet.src2dst_packets},{packet.src2dst_bytes},{packet.dst2src_duration_ms},{packet.dst2src_packets},{packet.dst2src_bytes},{packet.bidirectional_mean_ps},{packet.bidirectional_stddev_ps},{packet.bidirectional_max_ps},{packet.src2dst_min_ps},{packet.src2dst_mean_ps},{packet.src2dst_stddev_ps},{packet.src2dst_max_ps},{packet.dst2src_min_ps},{packet.dst2src_mean_ps},{packet.dst2src_stddev_ps},{packet.dst2src_max_ps},{packet.bidirectional_min_piat_ms},{packet.bidirectional_mean_piat_ms},{packet.bidirectional_stddev_piat_ms},{packet.bidirectional_max_piat_ms},{packet.src2dst_min_piat_ms},{packet.src2dst_mean_piat_ms},{packet.src2dst_stddev_piat_ms},{packet.src2dst_max_piat_ms},{packet.dst2src_min_piat_ms},{packet.dst2src_mean_piat_ms},{packet.dst2src_stddev_piat_ms},{packet.dst2src_max_piat_ms},{packet.bidirectional_syn_packets},{packet.bidirectional_cwr_packets},{packet.bidirectional_ece_packets},{packet.bidirectional_urg_packets},{packet.bidirectional_ack_packets},{packet.bidirectional_psh_packets},{packet.bidirectional_rst_packets},{packet.bidirectional_fin_packets},{packet.src2dst_syn_packets},{packet.src2dst_cwr_packets},{packet.src2dst_ece_packets},{packet.src2dst_urg_packets},{packet.src2dst_ack_packets},{packet.src2dst_psh_packets},{packet.src2dst_rst_packets},{packet.src2dst_fin_packets},{packet.dst2src_syn_packets},{packet.dst2src_cwr_packets},{packet.dst2src_ece_packets},{packet.dst2src_urg_packets},{packet.dst2src_ack_packets},{packet.dst2src_psh_packets},{packet.dst2src_rst_packets},{packet.dst2src_fin_packets}"

	producer.send(kafka_topic, key=device_name, value=data)
	print(f"No of packets sent: {count} \r", end="")
	count = count + 1
