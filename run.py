import logging
import os

from app.app import app, server


logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO").upper(), format='%(asctime)s - %(funcName)s - %(levelname)s:%(message)s')

if __name__ == '__main__':
    app.run_server(debug=True, port=8050)
