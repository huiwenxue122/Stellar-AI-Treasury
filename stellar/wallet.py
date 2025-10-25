import os
from stellar_sdk import Keypair, Network, TransactionBuilder, Server, Asset

class Wallet:
    def __init__(self, horizon_url: str, passphrase: str, secret_env: str, public_env: str):
        self.server = Server(horizon_url)
        self.passphrase = passphrase
        self.secret = os.environ.get(secret_env)
        self.public = os.environ.get(public_env)
        if not (self.secret and self.public):
            raise RuntimeError("Missing STELLAR keys in env")
        self.kp = Keypair.from_secret(self.secret)

    def asset(self, code: str, issuer: str | None):
        return Asset.native() if code == "XLM" else Asset(code, issuer)