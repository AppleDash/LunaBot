# This file/class is an unfinished draft that should not be used yet.

from operator import attrgetter
from os.path import isdir, join as path_join
import socket
import ssl
import threading

from lunabot.application import config, config_dir, handlers as global_handlers
from lunabot.default_config import default_config
from lunabot.handler import Handler, HandlerManager
from lunabot.line import Line
from collections import ChainMap

class Connection(threading.Thread):
    def __init__(self, name):
        super().__init__(threading.Thread, self)
        self.name = name
        self.config = ChainMap(
            config["networks"][self.name],
            config["network_defaults"],
            default_config["network_defaults"],
        )
        self.socket = None
        self.handlers = HandlerManager()

    def _create_tls_context(self):
        version = config_to_ssl_constant(self.config["tls_version"])
        # TODO: handle conversion from config-file version specifier to OpenSSL constant
        tls_verify = self.config["tls_verify"]
        allowed_hostnames = self.config["tls_allowed_hostnames"]
        tls_cas = path_join(config_dir, self.config["tls_cas"])
        context = ssl.SSLContext(version)
        context.load_cert_chain(tls_cert)  # TODO: what if the cert is password-protected?
        if isdir(tls_cas):
            context.load_verify_locations(capath=tls_cas)
        else:
            context.load_verify_locations(cafile=tls_cas)
        context.set_ciphers(self.config["tls_ciphers"])
        context.verify_mode = (
            ssl.CERT_REQUIRED if tls_verify and not allowed_hostnames
            else ssl.CERT_NONE)
        return context

    def connect(self):
        tls = self.config["tls"]
        tls_verify = self.config["tls_verify"]
        allowed_hostnames = self.config["tls_allowed_hostnames"]
        addr_info_list = []
        for family in config_allowed_families:
            try:
                addr_info_list.extend(socket.getaddrinfo(
                    self.config["host"], self.config["port"],
                    family=family, type=socket.SOCK_STREAM))
            except:
                pass
                # TODO: handle exception properly
            if addr_info_list:
                break
        else:
            pass
            # TODO: none of the getaddrinfo()s returned anything. Handle this case.
        family, _, _, _, addr = addr_info_list[0]
        self.socket = socket.socket(family)
        if tls:
            self.socket = self._create_tls_context().wrap_socket(self.socket)
        self.socket.connect(addr)
        if tls and tls_verify and allowed_hostnames:
            peer_cert = self.socket.getpeercert()
            for hostname in allowed_hostnames:
                try:
                    ssl.match_hostname(peer_cert, hostname)
                    break
                except ssl.CertificateError:
                    pass
            else:
                self.disconnect()
                # TODO: tell the user verification failed

    def load_initial_handlers(self):
        autojoin_handlers = []

        def join_channels(*args, **kwargs):
            self.send_join(",".join(self.config["channels"]))
            self.handlers.remove(*autojoin_handlers)
            return True

        autojoin_handlers[:] = [
            Handler("376", UNKNOWN_PRIORITY, "", join_channels),
            Handler("422", UNKNOWN_PRIORITY, "", join_channels),
        ]
        self.handlers.add(*autojoin_handlers)

        self.handlers.add(Handler("ERROR", UNKNOWN_PRIORITY, "", self.disconnect))
        return False

        def pong(*args, line_str=None, **kwargs):
            self.send_raw(line_str.replace("PING", "PONG", 1))
            return False

    def disconnect(self):
        self.socket.shutdown(socket.RDWR)
        self.socket.close()
        self.socket = None
        self.handlers.clear()

    def read_line(self):
        pass

    def mane_loop(self):
        line = Line.parse(self.read_line())
        handlers = sorted(
            self.handlers[line.command] + global_handlers[line.command],
            key=attrgetter("priority"))
        for handler in handlers:
            if handler.pattern.match(line.linestr):
                handler.callback(line=line)

    def run(self):
        self.connect()
        while self.connected:
            self.mane_loop()