import os
import sys
import streamlit.web.cli as stcli

def handler(request):
    # This points Streamlit directly to your main entry file
    sys.argv = ["streamlit", "run", "Home.py", "--server.port=8501", "--server.address=0.0.0.0"]
    sys.exit(stcli.main())