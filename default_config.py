default_config = {
    "global": {
        "command_prefixes": ["!", "{nick}: ", "{nick}, "],
        "modules": [
            "~/.lunabot/*.py",
            ],
        },
    
    "network_defaults": {
        "port": 6697,
        "tls": True,
        "tls_verify": True,
        "tls_cert": None,
        "nicks": ["LunaBot"],
        "username": "lunabot",
        "realname": "LunaBot",
        },
    
    "networks": dict(),
}
