# This file/class is an unfinished draft that should not be used yet.

from collections import ChainMap
from operator import attrgetter
import os.path
import socket
import ssl
import threading

import lunabot.config
from lunabot.handler import Handler, HandlerManager, UNKNOWN_PRIORITY
from lunabot.line import Line

global_handlers = HandlerManager()

class Connection(threading.Thread):
    def __init__(self, name, config, config_lock, global_handlers):
        super().__init__()
        self.name = name
        self.config = ChainMap(
            config["networks"][self.name],
            config["network_defaults"],
            lunabot.config.DEFAULT_CONFIG["network_defaults"],
            )
        self.config_lock = config_lock
        self.socket = None
        self.tls_context = None
        self.handlers = HandlerManager()
        # TODO: maybe this should be a `status` attribute?
        self.connected = False
        with self.config_lock:
            self.remaining_tls_versions = iter(self.config["tls_allowed_versions"])

    def _create_tls_context(self):
        try:
            tls_version = self.tls_context.protocol
        except AttributeError:
            try:
                tls_version = next(self.remaining_tls_versions)
            except StopIteration:
                # TODO: log that we've exhausted the allowed TLS versions
                raise
        with self.config_lock:
            tls_verify = self.config["tls_verify"]
            allowed_hostnames = self.config["tls_allowed_hostnames"]
            tls_cas = self.config["tls_ca_path"] and os.path.join(lunabot.config.dir, self.config["tls_ca_path"])
            tls_cert_name = self.config["tls_cert"] and os.path.join(lunabot.config.dir, self.config["tls_cert"])
            tls_ciphers = self.config["tls_ciphers"]
        context = ssl.SSLContext(tls_version)
        if tls_cert_name:
            context.load_cert_chain(tls_cert_name)  # TODO: what if the cert is password-protected?
        if tls_cas:
            if os.path.isdir(tls_cas):
                context.load_verify_locations(capath=tls_cas)
            else:
                context.load_verify_locations(cafile=tls_cas)
        if tls_ciphers:
            context.set_ciphers(tls_ciphers)
        context.verify_mode = (
            ssl.CERT_REQUIRED if tls_verify and not allowed_hostnames
            else ssl.CERT_NONE)
        return context

    def connect(self):
        with self.config_lock:
            host = self.config["host"]
            port = self.config["port"]
            tls = self.config["tls"]
            tls_verify = self.config["tls_verify"]
            allowed_hostnames = self.config["tls_allowed_hostnames"]
        addr_info_list = []
        # TODO: make IP version preference a config option
        # TODO: detect when IPv4 or IPv6 connectivity is broken and fall back to the other one
        for family in (socket.AF_INET6, socket.AF_INET):
            try:
                addr_info_list.extend(socket.getaddrinfo(
                    host, port, family=family, type=socket.SOCK_STREAM))
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
            self.tls_context = self._create_tls_context()
            self.socket = self.tls_context.wrap_socket(self.socket)
        else:
            self.tls_context = None
        try:
            self.socket.connect(addr)
        except ssl.SSLError as exception:
            if not exception.reason == "WRONG_VERSION_NUMBER":
                raise
            # TODO: log that we're trying the next allowed TLS version
            try:
                tls_version = next(self.remaining_tls_versions)
            except StopIteration:
                # TODO: log that we've exhausted the allowed TLS versions
                raise
            else:
                return self.connect()
        if tls and tls_verify and allowed_hostnames:
            peer_cert = self.socket.getpeercert()
            for hostname in allowed_hostnames:
                try:
                    ssl.match_hostname(peer_cert, hostname)
                except ssl.CertificateError:
                    pass
                else:
                    break
            else:
                self.disconnect()
                # TODO: tell the user verification failed
        self.connected = True

    # TODO: make these all plugins.
    # Yes, even the pingpong one.
    def load_initial_handlers(self):
        autojoin_handlers = []

        def join_channels(*args, **kwargs):
            with self.config_lock:
                channels = self.config["channels"]
            self.send_join(",".join(channels))
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
        with self.config_lock:
            nicks = self.config["nicks"]
            username = self.config["username"]
            realname = self.config["realname"]
        self.send_raw("NICK %s" % nicks[0])
        self.send_raw("USER %s * * :%s" % (username, realname))
        while self.connected:
            self.mane_loop()
