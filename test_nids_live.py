import requests
import nfstream
from os import listdir
import joblib

api_endpoint = "http://localhost:5000/predict"

network_interfaces = listdir("/sys/class/net/")
network_interfaces.remove("lo")

for i in range(len(network_interfaces)):
    print(f"{i+1} : {network_interfaces[i]}")

user_input = int(input(f"Select one network interface:"))


live_capture = nfstream.NFStreamer(
    source=network_interfaces[user_input-1], statistical_analysis=False, promiscuous_mode=True, idle_timeout=10)

le = joblib.load("label_encoder_nids.pkl")
scaler = joblib.load("scaler_nids.pkl")
pca = joblib.load("pca_nids.pkl")

required_features = ['src_port', 'dst_port', 'protocol', 'ip_version', 'vlan_id',
            'tunnel_id', 'bidirectional_first_seen_ms',
            'bidirectional_last_seen_ms', 'bidirectional_duration_ms',
            'bidirectional_packets', 'bidirectional_bytes', 'src2dst_first_seen_ms',
            'src2dst_last_seen_ms', 'src2dst_duration_ms', 'src2dst_packets',
            'src2dst_bytes', 'dst2src_first_seen_ms', 'dst2src_last_seen_ms',
            'dst2src_duration_ms', 'dst2src_packets', 'dst2src_bytes',
            'application_name', 'application_category_name', 'user_agent',
            'content_type']

count = 1

for packet in live_capture:
    data = [packet.src_port, packet.dst_port, packet.protocol, packet.ip_version, packet.bidirectional_first_seen_ms, packet.bidirectional_last_seen_ms, packet.bidirectional_duration_ms, packet.bidirectional_packets, packet.bidirectional_bytes, packet.src2dst_first_seen_ms, packet.src2dst_last_seen_ms, packet.src2dst_duration_ms, packet.src2dst_packets, packet.src2dst_bytes, packet.dst2src_first_seen_ms, packet.dst2src_last_seen_ms, packet.dst2src_duration_ms, packet.dst2src_packets, packet.dst2src_bytes]
    data.append(le.fit_transform([packet.application_name])[0])
    data.append(le.fit_transform([packet.application_category_name])[0])
    data.append(le.fit_transform([packet.user_agent])[0])
    data.append(le.fit_transform([packet.content_type])[0])
    data = scaler.transform([data])
    data = pca.transform(data)
    # print(data)
    prediction = requests.post(api_endpoint, json={"inputs":data.tolist()[0]})
    print(f"{count} : {prediction.json()['prediction']}")
    count = count + 1
