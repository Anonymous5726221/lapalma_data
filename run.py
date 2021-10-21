import logging

from app.app import init_app

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s:%(message)s')

app = init_app()
server = app.server

if __name__ == '__main__':
    app.run_server(debug=True, port=8050)

