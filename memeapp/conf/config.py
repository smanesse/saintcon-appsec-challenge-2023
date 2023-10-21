# Any production secrets will get overridden in local_settings
# this file is out-of-scope for vulnerabilities
SECRET_KEY = "4af729dce264a1d5e0fd29bac4cb2ea0bdc9f6135ff04d2ee4e50ad333ed65ea"
PEPPER = "8cce9f214e74162abbc517a34b395c71d3ec41707bd7c42d6e4bfcdce5a9fdfd".encode("utf-8")
BCRYPT_ROUNDS = 4  # should be set higher in prod
SESSION_EXPIRY = 24  # hours
DEBUG = True

# this bit at the end to override with local config

try:
    from conf.local_config import *
except ImportError:
    pass
