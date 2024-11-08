import streamlit as st
import os
from io import StringIO
import requests
import nfstream
import sys
import joblib
import pefile
import re
import sys
import requests

st.set_page_config(page_title="Intrusion Detection System", page_icon="🔒", layout="wide")

api_endpoint = 'http://localhost:5000/predict'

tabs = st.tabs(["Network Intrusion Detection System", "File Intrusion Detection System"])

with tabs[0]:
	st.header("Network Intrusion Detection System")
	st.markdown("Upload a pcap file to check if it is malicious or not.")
	uploaded_file = st.file_uploader("Choose a pcap file", type="pcap")
	if uploaded_file is not None:
		with open(os.path.join("uploads/", uploaded_file.name), "wb") as f:
			f.write(uploaded_file.getbuffer())
  
		st.write("File uploaded successfully.")
		if st.button("Predict"):
			st.write("Predicting...")

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


			df = get_features_from_pacp_file("uploads/"+uploaded_file.name)

			for i in range(len(df)):
			    data = scaler.transform([df[i]]);data = pca.transform(data);prediction = requests.post(api_endpoint, json={"inputs": data.tolist()[0]});st.write(f"Packet Number {i+1} : {'safe' if prediction.json()['prediction'] == 0 else 'malicious'}")



    
with tabs[1]:
	st.header("File Intrusion Detection System")
	st.markdown("Upload a file to check if it is malicious or not.")
	uploaded_file = st.file_uploader("Choose a file", type="exe")
	if uploaded_file is not None:
		st.write("File uploaded successfully.")
		with open(os.path.join("uploads/", uploaded_file.name), "wb") as f:
			f.write(uploaded_file.getbuffer())
		if st.button("Predict "):
			st.write("Predicting...")
			model_endpoint = 'http://localhost:5000/predict'
			from test_fids import get_features
			data = get_features("uploads/"+uploaded_file.name)
			features = [float(data[i]) for i in range(7)]
			prediction = requests.post(model_endpoint, json={'inputs': features}).json()['prediction']
			if prediction == 0:
				st.info("File is safe.")
			else:
				st.warning("File is suspected to be malicious.")
