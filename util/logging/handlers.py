import logging.handlers


class CloudwatchHandler(logging.handlers.DatagramHandler):
    def __init__(self, group, stream, sock=':1514'):
        if sock[0] == ':':
            super(logging.handlers.DatagramHandler,
                  self).__init__('localhost', int(sock[1:]))
        else:
            super(logging.handlers.DatagramHandler,
                  self).__init__(sock, None)
        self.group = group
        self.stream = stream

    def emit(self, record):
        record.group = self.group
        record.stream = self.stream
        record.message_formatted = self.format(record)
        super(logging.handlers.DatagramHandler, self).emit(record)
