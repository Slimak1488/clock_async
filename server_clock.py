from aiohttp import web
from autobahn.asyncio.websocket import WebSocketServerProtocol, WebSocketServerFactory
import asyncio, aiohttp_jinja2, jinja2, datetime, time


@aiohttp_jinja2.template('clock.html')
async def handler(request):
    return aiohttp_jinja2.render_template('clock.html', request, context = {})


async def init(loop):
    app = web.Application(loop=loop)
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('templates'))
    app['static_root_url'] = '/static'
    app.router.add_static('/static', 'static', name='static')
    app.router.add_route('GET', '/', handler)
    srv = await loop.create_server(app.make_handler(), '127.0.0.1', 5000)
    print('serving on', srv.sockets[0].getsockname())
    return srv


class MyServerProtocol(WebSocketServerProtocol):

    def onConnect(self, request):
        print("Client connecting: {0}".format(request.peer))
        asyncio.ensure_future(self._timer())

    async def _timer(self):
        while True:
            print('timeout')
            payload_m = datetime.datetime.now().strftime('%M')
            payload_h = datetime.datetime.now().strftime('%H')
            self.sendMessage( payload_h.encode(), False)
            self.sendMessage(payload_m.encode(), False)
            await asyncio.sleep(2)

    def onOpen(self):
        print("WebSocket connection open.")

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))


if __name__ == '__main__':
    factory = WebSocketServerFactory("ws://127.0.0.1:9000")
    factory.protocol = MyServerProtocol
    loop = asyncio.get_event_loop()
    coro = loop.create_server(factory, '127.0.0.1', 9000)
    server = loop.run_until_complete(coro)
    loop.run_until_complete(init(loop))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.close()
        loop.close()