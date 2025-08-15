import signal
from socket import socketpair, SOCK_DGRAM

class QtSignalHandler:
    """
    Gracefully handles OS signals (like Ctrl+C) in a Qt application.

    Uses a socket pair to integrate Python's signal system with the
    Qt event loop, ensuring immediate handling without relying on focus.
    """

    def __init__(self, qt_app, QAbstractSocket):
        self._app = qt_app
        self._old_fd = None

        # Create socket pair: Python writes, Qt reads
        self._write_sock, self._read_sock = socketpair(type=SOCK_DGRAM)
        self._qt_sock = QAbstractSocket(QAbstractSocket.UdpSocket, qt_app)
        self._qt_sock.setSocketDescriptor(self._read_sock.fileno())
        self._write_sock.setblocking(False)

        # Redirect Python signals to the socket
        self._old_fd = signal.set_wakeup_fd(self._write_sock.fileno())

        # Dummy initial handler to prevent Qt warnings
        self._qt_sock.readyRead.connect(lambda: None)
        # Real handler for signals
        self._qt_sock.readyRead.connect(self._on_signal)

    def install(self):
        """Install Ctrl+C handler to exit the application with code 130."""
        signal.signal(signal.SIGINT, lambda *_: self._app.exit(130))

    def _on_signal(self):
        """Read the byte sent from Python signal to trigger Qt slot."""
        _ = self._qt_sock.readData(1)

    def __del__(self):
        """Restore previous wakeup fd if it existed."""
        if self._old_fd is not None:
            signal.set_wakeup_fd(self._old_fd)
