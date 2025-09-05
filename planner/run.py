import os

# Start Streamlit with correct port and address for Home Assistant ingress
os.system("streamlit run planner.py --server.port=5000 --server.address=0.0.0.0")