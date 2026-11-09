from base64 import b64encode
from time import time
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.backends import default_backend


class AuthIntent:
    @staticmethod
    def get_auth_intent(session) -> dict | None:
        try:
            private_key = ec.generate_private_key(ec.SECP256R1(), default_backend())
            public_key = private_key.public_key()

            client_public_key = b64encode(
                public_key.public_bytes(
                    encoding=serialization.Encoding.DER,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo,
                )
            ).decode('utf-8')

            client_epoch_timestamp = str(int(time()))

            response = session.get('https://apis.roblox.com/hba-service/v1/getServerNonce')
            server_nonce = response.text.strip("'")

            payload = f'{client_public_key}|{client_epoch_timestamp}|{server_nonce}'
            signature = private_key.sign(payload.encode('utf-8'), ec.ECDSA(hashes.SHA256()))
            sai_signature = b64encode(signature).decode('utf-8')

            return {
                'clientEpochTimestamp': client_epoch_timestamp,
                'clientPublicKey': client_public_key,
                'saiSignature': sai_signature,
                'serverNonce': server_nonce,
            }
        except Exception:
            return None