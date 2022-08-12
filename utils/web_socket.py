import ssl

import websockets

TIMEOUT = 10  # seconds

ssl_context = ssl.create_default_context()


def get_websocket_connection(url):
    if url[0:3] == "wss":
        return websockets.connect(url, ssl_context)
    else:
        return websockets.connect(url)
