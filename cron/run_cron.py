import asyncio
import json

import traceback

from cron.task_maps import plugins
from utilities.db_getter import get_session


class BaseEngine:
    def __init__(self, logger, *args, **kwargs):
        self.logger = logger
        self.messages = asyncio.Queue()

    @property
    def session(self):
        return get_session()

    @staticmethod
    async def reply(message, writer):
        try:
            event = message['event']
        except KeyError:
            event = None

        hello = event == 'HELLO'

        if hello:
            writer.write('HI'.encode())
            await writer.drain()

        return hello

    def _handle_socket_error(self, message, port):
        count = message.get('__error_count__', 0)
        if count <= 10:
            message['__error_count__'] = count + 1
            asyncio.create_task(self.messages.put(message))
        else:
            message.pop('__error_count__', None)
            json_message = json.dumps(message)
            self.logger.exception(f'Timed out while sending {json_message} at port {port}')

    async def handle(self, reader, writer):
        data = await reader.read(1024)
        message = data.decode()
        self.logger.info('Received new message %s' % message)

        try:
            json_message = json.loads(message)
            hello = await self.reply(json_message, writer)
            if not hello:
                await self.messages.put(json_message)
        except Exception:
            self.logger.exception('Could not process received message %s' % message)
        finally:
            writer.close()

    async def send_event(self, msg, port, HOST='127.0.0.1'):
        json_message = json.dumps(msg)
        try:
            reader, writer = await asyncio.open_connection(HOST, port)
            writer.write(json_message.encode('utf-8'))
            await writer.drain()
            writer.close()
        except asyncio.TimeoutError:
            self._handle_socket_error(msg, port)
        except ConnectionRefusedError:
            self.logger.warning(f'Service at host:{HOST} and port: {port} is refusing connections.')
        except Exception:
            self.logger.exception(f'Exception while sending message {json_message}.')

    async def _do_work(self, message):
        raise NotImplementedError

    async def worker(self):
        while True:
            try:
                message = await self.messages.get()
                await self._do_work(message)
            except Exception:
                traceback.print_exc()
                self.session.rollback()
                self.logger.exception(f'Exception while processing message')
            finally:
                self.messages.task_done()
                self.session.close()

    async def start(self, port, HOST='127.0.0.1'):
        server = await asyncio.start_server(self.handle, HOST, port)
        self.logger.info('Starting engine port=%d' % port)
        # Create worker tasks
        workers = [asyncio.create_task(self.worker()) for _ in range(4)]
        async with server:
            await asyncio.gather(server.serve_forever(), *workers)


class CronEngine(BaseEngine):
    name = 'Cron Engine'

    def __init__(self, logger, *args, **kwargs):
        super(CronEngine, self).__init__(logger, *args, **kwargs)

    async def _do_work(self, message):
        event = message.get('event')
        if event == 'SEND_VERIFICATION_EMAIL':
            print('run_cron')
            await self.run_async_job(event, message['params'])
        elif event == 'SEND_PASSWORD_RESET_LINK':
            print('run_cron')
            await self.run_async_job(event, message['params'])
        else:
            self.logger.warning(f"Invalid event type {event}")

    async def run_async_job(self, event, params):
        # Simulate an asynchronous job
        self.logger.info(f"Running async job {event}")
        event_plugin = plugins.get(event)

        if event_plugin:
            try:
                event_plugin(**params)
                self.logger("Task Completed")
            except Exception as e:
                self.logger.warning(f"Error Occured.{str(e)}")
        else:
            self.logger("Invalid Plugin")


if __name__ == '__main__':
    import logging

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger('CronEngine')

    cron_engine = CronEngine(logger)

    try:
        asyncio.run(cron_engine.start(port=8888))
    except KeyboardInterrupt:
        logger.info("Shutting down...")
