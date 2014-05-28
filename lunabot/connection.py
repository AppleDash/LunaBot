# This file/class is an unfinished draft that should not be used yet.

from operator import attrgetter
from os.path import isdir, join as path_join
import socket
import ssl
import threading

#from lunabot.application import config, config_dir, handlers as global_handlers
from lunabot.default_config import default_config
from lunabot.handler import Handler, HandlerManager, UNKNOWN_PRIORITY
from lunabot.line import Line
from collections import ChainMap

global_handlers = HandlerManager()

class Connection(threading.Thread):
    def __init__(self, name, config, config_dir):
        super().__init__()
        self.name = name
        self.config = ChainMap(
            config["networks"][self.name],
            config["network_defaults"],
            default_config["network_defaults"],
            )
        self.socket = None
        self.handlers = HandlerManager()
        # TODO: maybe this should be a `status` attribute?
        self.connected = False

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
        # TODO: make IP version preference a config option
        for family in (socket.AF_INET6, socket.AF_INET):
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
        self.connected = True

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

        #return False

        def pong(*args, line_str=None, **kwargs):
            self.send_raw(line_str.replace("PING", "PONG", 1))
            return False

        self.handlers.add(Handler("PING", UNKNOWN_PRIORITY, "", pong))

    def disconnect(self):
        self.socket.shutdown(socket.RDWR)
        self.socket.close()
        self.socket = None
        self.handlers.clear()

    def send_raw(self, data):
        print("<-", data)
        self.socket.send(bytes(data + "\r\n", encoding="utf-8"))

    def send_join(self, channels):
        self.send_raw("JOIN %s" % channels)

    def read_line(self):
        out = ""
        while 1:
            c = self.socket.recv(1).decode("utf-8")
            if c is None or c == "":
                return None
            if c == "\n":
                return out.strip()
            out += c

    def mane_loop(self):
        line = Line.parse(self.read_line())
        print("->", line.linestr)
        handlers = sorted(
            self.handlers[line.command] + global_handlers[line.command],
            key=attrgetter("priority"))
        for handler in handlers:
            if handler.event == line.command and handler.pattern.match(line.linestr):
                handler.callback(line=line, line_str=line.linestr)

    def run(self):
        self.connect()
        self.load_initial_handlers()
        # TODO: what about `CAP`s?
        # TODO: what if that nick is taken?
        self.send_raw("NICK %s" % self.config["nicks"][0])
        self.send_raw("USER %s * * :%s" % (self.config["username"], self.config["realname"]))
        while self.connected:
            self.mane_loop()
