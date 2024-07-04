import asyncio
import json
import socket
import time
import traceback
from queue import Queue

from utilities.db_getter import get_session


class BaseEngine:
    def __init__(self, logger, *args, **kwargs):
        self.logger = logger
        self.messages = Queue()

    @property
    def session(self):
        return get_session()

    @staticmethod
    def reply(message, sock):
        try:
            event = message['event']
        except KeyError:
            event = None

        hello = event == 'HELLO'

        if hello:
            sock.send('HI'.encode())

        return hello

    def _handle_socket_error(self, message, port):
        count = message.get('__error_count__', 0)
        if count <= 10:
            message['__error_count__'] = count + 1
            self.messages.put(message)
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
            hello = self.reply(json_message, writer)
            if not hello:
                self.messages.put(json_message)
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

    def _do_work(self, message):
        raise NotImplementedError

    def run_async_job(self, job_id, *args, **kwargs):
        """
        Runs the asynchronous job as specified by server.
        :param job_id:
        :param args:
        :param kwargs:
        :return:
        """
        pass

    def start_worker(self):
        while True:
            try:
                message = self.messages.get()
                self._do_work(message)
            except Exception:
                traceback.print_exc()
                self.session.rollback()
                self.logger.exception(f'Exception while processing message {message}')
            finally:
                self.messages.task_done()
                self.session.close()
                time.sleep(0)

    async def start(self, port, HOST='127.0.0.1'):
        server = await asyncio.start_server(self.handle, HOST, port)
        self.logger.info('Starting engine port=%d' % port)
        worker_count = 4
        # tasks = [self.start_worker() for _ in range(worker_count)]
        # import pdb;pdb.set_trace()
        # await asyncio.gather(*tasks)
        async with server:
            await server.serve_forever()


class CronEngine(BaseEngine):
    name = 'Cron Engine'

    def __init__(self, logger, *args, **kwargs):
        super(CronEngine, self).__init__(logger, *args, **kwargs)

    def _do_work(self, message):
        event = message.get('event')
        if event == 'SEND_VERIFICATION_EMAIL':
            self.run_async_job(message['id'], message['params'])
        else:
            self.logger.warning(f"Invalid event type {event}")
