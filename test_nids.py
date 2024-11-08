import requests
import nfstream
import sys
import joblib

api_endpoint = "http://localhost:5000/predict"

le = joblib.load("label_encoder_nids.pkl")
scaler = joblib.load("scaler_nids.pkl")
pca = joblib.load("pca_nids.pkl")


def get_features_from_pacp_file(pcap_file):
	flow = nfstream.NFStreamer(
		source=pcap_file, statistical_analysis=False).to_pandas()
	# encode the application_name, application_category_name, user_agent, content_type
	flow['application_name'] = le.fit_transform(flow['application_name'])
	flow['application_category_name'] = le.fit_transform(
		flow['application_category_name'])
	flow['user_agent'] = le.fit_transform(flow['user_agent'])
	flow['content_type'] = le.fit_transform(flow['content_type'])
	# drop the columns which are not required
	flow = flow.drop(['id', 'expiration_id', 'src_ip', 'src_mac', 'src_oui', 'dst_ip', 'dst_mac', 'dst_oui', 'application_is_guessed',
	                 'application_confidence', 'requested_server_name', 'client_fingerprint', 'server_fingerprint'], axis=1)
	flow = flow.drop(["vlan_id", "tunnel_id"], axis=1)
	flow = flow.fillna(0)
	# flow = flow.drop_duplicates()
	# print the coloum name if it has string datatype
	for col in flow.columns:
		if flow[col].dtype == 'object':
			print(col)
	features = flow.values.tolist()
	# features = np.array(features, dtype=np.float32)
	return features

df = get_features_from_pacp_file(sys.argv[1])

for i in range(len(df)):
    data = scaler.transform([df[i]])
    data = pca.transform(data)
    prediction = requests.post(api_endpoint, json={"inputs": data.tolist()[0]})
    print(f"{i+1} : {prediction.json()['prediction']}")