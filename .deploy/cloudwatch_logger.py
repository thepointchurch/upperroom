import logging
import logging.handlers
import os
import pickle
import signal
import socket
import socketserver
import sys

import boto.logs
import boto.utils

logger = logging.getLogger('cloudwatch')


class LogGroup(object):
    def __init__(self, cw, name):
        self.cw = cw
        self.name = name

        need_group = True
        for group in self.cw.describe_log_groups()['logGroups']:
            if group['logGroupName'] == self.name:
                need_group = False
                break

        if need_group:
            self.cw.create_log_group(self.name)
            logger.info('Created new log group: %s', self.name)


class LogStream(object):
    def __init__(self, group, name):
        self.group = group
        self.name = name
        self.next_token = None

        need_stream = True
        streams = self.group.cw.describe_log_streams(self.group.name)
        for stream in streams['logStreams']:
            if stream['logStreamName'] == self.name:
                need_stream = False
                self.next_token = stream['uploadSequenceToken']
                break

        if need_stream:
            self.group.cw.create_log_stream(self.group.name, self.name)
            logger.info('Created new log stream: %s:%s',
                        self.group.name, self.name)

    def put_events(self, events):
        x = self.group.cw.put_log_events(self.group.name,
                                         self.name,
                                         events,
                                         self.next_token)
        self.next_token = x['nextSequenceToken']


class UDPLogHandler(socketserver.BaseRequestHandler):
    groups = {}
    streams = {}

    id = boto.utils.get_instance_identity()
    cw = boto.logs.connect_to_region(id['document']['region'])

    def handle(self):
        data = self.request[0].strip()
        rec = logging.makeLogRecord(pickle.loads(data[4:]))

        try:
            group = UDPLogHandler.groups[rec.group]
        except KeyError:
            group = LogGroup(UDPLogHandler.cw, rec.group)
            UDPLogHandler.groups[rec.group] = group
        except AttributeError:
            logger.error('No log group specified: %s' % str(rec))
            return
        try:
            stream = UDPLogHandler.streams[rec.stream]
        except KeyError:
            stream = LogStream(group, rec.stream)
            UDPLogHandler.streams[rec.stream] = stream
        except AttributeError:
            logger.error('No log stream specified: %s' % str(rec))
            return

        try:
            message = rec.message_formatted
        except AttributeError:
            message = rec.getMessage()

        stream.put_events([
            {
                'timestamp': rec.created*1000.0,
                'message': message,
            }])


if __name__ == '__main__':
    logger.setLevel(logging.DEBUG)
    h = logging.handlers.SysLogHandler(address='/dev/log')
    h.ident = 'cloudwatch: '
    logger.addHandler(h)
    logger.addHandler(logging.StreamHandler())

    try:
        socket_name = sys.argv[1]
    except IndexError:
        socket_name = os.getenv('CLOUDWATCH_LOG_PATH', ':1514')
    if not socket_name:
        logger.error('No socket provided')
        sys.exit(1)

    server = None

    def cleanup():
        if socket_name[0] == ':':
            return

        logger.info('Cleaning up socket at %s', socket_name)
        try:
            os.unlink(socket_name)
        except FileNotFoundError:  # noqa
            pass

    def signal_term_handler(signal, frame):
        cleanup()
        sys.exit(0)

    signal.signal(signal.SIGTERM, signal_term_handler)
    signal.signal(signal.SIGINT, signal_term_handler)

    try:
        if socket_name[0] == ':':
            server = socketserver.UDPServer(('localhost',
                                             int(socket_name[1:])),
                                            UDPLogHandler)
        else:
            os.umask(0)
            server = socketserver.UnixDatagramServer(socket_name,
                                                     UDPLogHandler)
        logger.info('Listening at %s', socket_name)

        server.serve_forever()

    except (socket.error, OSError) as e:
        logger.exception(str(e))
        sys.exit(2)

    cleanup()
