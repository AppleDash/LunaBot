from copy import deepcopy
import json
import ssl
import threading

# TODO: These should really be immutable…

DEFAULT_CONFIG = {
    "global": {
        "command_prefixes": ["!", "{nick}: ", "{nick}, "],
        "modules": [
            "modules/*.py",
            ],
        },

    "network_defaults": {
        "host": None,
        "port": 6697,
        "tls": True,
        "tls_allowed_versions": ["TLS 1.2", "TLS 1.1", "TLS 1.0", "SSL 3"],
        "tls_ciphers": "HIGH:MEDIUM:LOW:!aNULL:!eNULL:@STRENGTH",
        "tls_verify": True,
        "tls_ca_path": "/etc/ssl/certs/ca-certificates.crt",
        "tls_allowed_hostnames": None,
        "tls_cert": None,
        "nicks": ["LunaBot"],
        "username": "lunabot",
        "realname": "LunaBot",
        },

    "networks": {},
    }

# Not just a dict literal because not all versions of Python have all these constants
# TODO: There's got to be a better way to do these conversions.
TLS_VERSIONS_FROM_STR = {}
try:
    TLS_VERSIONS_FROM_STR["SSL 2"] = ssl.PROTOCOL_SSLv2
except AttributeError:
    pass
try:
    TLS_VERSIONS_FROM_STR["SSL 2|3"] = ssl.PROTOCOL_SSLv23
except AttributeError:
    pass
try:
    TLS_VERSIONS_FROM_STR["SSL 3"] = ssl.PROTOCOL_SSLv3
except AttributeError:
    pass
try:
    TLS_VERSIONS_FROM_STR["TLS 1.0"] = ssl.PROTOCOL_TLSv1
except AttributeError:
    pass
try:
    TLS_VERSIONS_FROM_STR["TLS 1.1"] = ssl.PROTOCOL_TLSv1_1
except AttributeError:
    pass
try:
    TLS_VERSIONS_FROM_STR["TLS 1.2"] = ssl.PROTOCOL_TLSv1_2
except AttributeError:
    pass
TLS_VERSIONS_TO_STR = {value: key for key, value in TLS_VERSIONS_FROM_STR.items()}

def load(filename):
    with open(filename, "r") as file:
        config = json.load(file)
    try:
        config["network_defaults"]["tls_allowed_versions"] = [TLS_VERSIONS_FROM_STR[version] for version in config["network_defaults"]["tls_allowed_versions"]]
    except KeyError:
        # The network defaults config doesn't have a "tls_allowed_versions" list.
        # Nothing to do here.
        pass
    # Instead of adding a try-except block to catch KeyErrors,
    # we'll just get an empty dict and iterate over it.
    for network_config in config.get("networks", {}).values():
        try:
            network_config["tls_allowed_versions"] = [TLS_VERSIONS_FROM_STR[version] for version in network_config["tls_allowed_versions"]]
        except KeyError:
            # This network's config doesn't have a "tls_allowed_versions" list.
            # Nothing to do here.
            pass
    with current_lock:
        current.clear()
        current.update(config)

def _dump(filename, config):
    try:
        config["network_defaults"]["tls_allowed_versions"] = [TLS_VERSIONS_TO_STR[version] for version in config["network_defaults"]["tls_allowed_versions"]]
    except KeyError:
        # The network defaults config doesn't have a "tls_allowed_versions" list.
        # Nothing to do here.
        pass
    # Instead of adding a try-except block to catch KeyErrors,
    # we'll just get an empty dict and iterate over it.
    for network_config in config.get("networks", {}).values():
        try:
            network_config["tls_allowed_versions"] = [TLS_VERSIONS_TO_STR[version] for version in network_config["tls_allowed_versions"]]
        except KeyError:
            # This network's config doesn't have a "tls_allowed_versions" list.
            # Nothing to do here.
            pass
    try:
        with open(filename, "w") as file:
            json.dump(config, file, sort_keys=True, indent=4, separators=(',', ': '))
    except FileNotFoundError:
        parent_dir = os.path.dirname(os.path.normpath(filename))
        try:
            makedirs(parent_dir, exist_ok=True)
        except OSError as exception:
            if exception.errno == errno.EEXIST and os.path.isdir(parent_dir):
                return _dump(filename, config)
            else:
                raise

def dump(filename):
    if config is None:
        # Don't modify the instance of the config everything else is using.
        with current_lock:
            config = deepcopy(current)
    return _dump(filename, config)

current = {}
# TODO: This should really be a shared lock, yes?
current_lock = threading.RLock()
