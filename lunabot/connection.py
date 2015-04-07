# This file/class is an unfinished draft that should not be used yet.

from collections import ChainMap
from operator import attrgetter
import os.path
import socket
import ssl
import threading

import lunabot.config
from lunabot.handler import HandlerManager
from lunabot.line import Line

global_handlers = HandlerManager()

class Connection(threading.Thread):
    def __init__(self, name, config, config_lock):
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
        self.connected = False
        with self.config_lock:
            self.remaining_tls_versions = iter(self.config["tls_allowed_versions"].copy())

    def _create_tls_context(self):
        try:
            tls_version = self.tls_context.protocol
        except AttributeError:
            try:
                tls_version = next(self.remaining_tls_versions)
            except StopIteration:
                raise
        with self.config_lock:
            tls_verify = self.config["tls_verify"]
            allowed_hostnames = self.config["tls_allowed_hostnames"]
            tls_cas = (
                self.config["tls_ca_path"] and
                os.path.join(lunabot.config.dir, self.config["tls_ca_path"])
                )
            tls_cert_name = (
                self.config["tls_cert"] and
                os.path.join(lunabot.config.dir, self.config["tls_cert"])
                )
            tls_ciphers = self.config["tls_ciphers"]
        context = ssl.SSLContext(tls_version)
        if tls_cert_name:
            context.load_cert_chain(tls_cert_name)
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
        for family in (socket.AF_INET6, socket.AF_INET):
            try:
                addr_info_list.extend(socket.getaddrinfo(
                    host, port, family=family, type=socket.SOCK_STREAM))
            except Exception:
                pass
            if addr_info_list:
                break
        else:
            pass
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
            try:
                tls_version = next(self.remaining_tls_versions)
            except StopIteration:
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
        self.connected = True

    def disconnect(self):
        self.socket.shutdown(socket.SHUT_RDWR)
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
        print("->", str(line))
        handlers = sorted(
            self.handlers[line.command] + global_handlers[line.command],
            key=attrgetter("priority"))
        for handler in handlers:
            if handler.event == line.command:
                handler.callback(connection=self, line=line)

    def run(self):
        self.connect()
        with self.config_lock:
            nicks = self.config["nicks"]
            username = self.config["username"]
            realname = self.config["realname"]
        self.send_raw("NICK %s" % nicks[0])
        self.send_raw("USER %s * * :%s" % (username, realname))
        while self.connected:
            self.mane_loop()
