import toml

toml_string = """
# This is a TOML document.

title = "TOML file"

[owner]
name = "Nikita Unisikhin"

[server]
host = "127.0.0.1"
port = 100
name = "server"
connection_max = 100

[google.com]
ip="172.217.22.14"
port=53

[yandex.ru]
ip="213.180.204.11"
port=53
"""

parsed_toml = toml.loads(toml_string)
