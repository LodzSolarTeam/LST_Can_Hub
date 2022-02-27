import asyncio

import websockets


WEBSOCKET_CONNECTION_TIMEOUT = 4

class WebSocketConnectWithTimeout(websockets.connect):
    def __init__(self, *args, **kwargs):
        self.connect_timeout = kwargs.pop('connect_timeout')
        super(WebSocketConnectWithTimeout, self).__init__(*args, **kwargs)

    async def __aenter__(self, *args, **kwargs):
        return await asyncio.wait_for(super(WebSocketConnectWithTimeout, self).__aenter__(*args, **kwargs),
                                      timeout=self.connect_timeout)

    async def __aexit__(self, *args, **kwargs):
        return await super(WebSocketConnectWithTimeout, self).__aexit__(*args, **kwargs)