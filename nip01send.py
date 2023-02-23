import json
import base64
import secrets
import time
import binascii
import secp256k1
import websockets

from cffi import FFI
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from hashlib import sha256

from typing import Tuple


# Convert a hex string to bytes
def hex_to_bytes(hex_string):
    return bytes.fromhex(hex_string)

# Convert bytes to a hex string
def bytes_to_hex(byte_string):
    return byte_string.hex()

# Convert a base64-encoded string to bytes
def base64_to_bytes(base64_string):
    return base64.b64decode(base64_string)

# Convert bytes to a base64-encoded string
def bytes_to_base64(byte_string):
    return base64.b64encode(byte_string).decode()


class NostrEvent:
    def __init__(self, privkey, content, tags=None):
        self.privkey = privkey  # private key
        self.pubkey = ''  # convert VerifyingKey to string
        self.created_at = int(time.time())
        self.kind = 1
        self.tags = []
        self.content = content

    async def sign(self):
        
        # Key derivations
        sk = secp256k1.PrivateKey(bytes.fromhex(self.privkey))
        self.pubkey = sk.pubkey.serialize()[1:]

        # use privkey to sign the message
        obj = [
            0,
            self.pubkey.hex(),
            self.created_at,
            self.kind,
            self.tags,
            self.content
        ]

        #print(f"sk: {self.privkey}\nvk: {self.pubkey.hex()}\n")

        obj_json = json.dumps(obj, separators=(",", ":"), ensure_ascii=False)
        obj_hash = sha256(obj_json.encode("utf-8")).digest()

        signature = sk.schnorr_sign(obj_hash, None, raw=True)

        #print(signature)

        event = {
            "id": obj_hash.hex(),
            "pubkey": self.pubkey.hex(),  # convert bytes to string
            "created_at": obj[2],
            "kind": obj[3],
            "tags": obj[4],
            "content": obj[5],
            "sig": bytes_to_hex(signature)
        }

        #print(event)
        event_json = json.dumps(event, separators=(",", ":"), ensure_ascii=False)
        return event


# broadcast the event
async def broadcast_signed_event(signed_event: dict, relay_endpoint: str) -> Tuple[bool, str]:
    # create json string with "EVENT" at the start per NIP01
    event_json = json.dumps(["EVENT", signed_event])
    #print(event_json)
    #return event_json

    try:
        async with websockets.connect(relay_endpoint) as websocket:
            await websocket.send(event_json)
            response = await websocket.recv()

            if response == "SUCCESS":
                return True, response
            else:
                return False, response
    except Exception as e:
        return False, str(e) 