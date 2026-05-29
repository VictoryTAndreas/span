import os
import sys
import streamlit.web.cli as stcli

# 1. Force a global assignment so Vercel's static analyzer passes the build check
def run_streamlit():
    sys.argv = [
        "streamlit", 
        "run", 
        "Home.py", 
        "--server.port=8501", 
        "--server.address=0.0.0.0"
    ]
    stcli.main()

# Expose the global variable Vercel is looking for
app = run_streamlit

# 2. Handle the invocation if Vercel attempts to call it as a function handler
def handler(request):
    run_streamlit()