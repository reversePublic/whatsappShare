from consonance.structs.keypair import KeyPair
from consonance.structs.publickey import PublicKey
from consonance.protocol import WANoiseProtocol
from consonance.config.client import ClientConfig
from consonance.streams.segmented.wa import WASegmentedStream
from consonance.streams.arbitrary.arbitrary_socket import SocketArbitraryStream
from consonance.config.templates.useragent_iPhone import iPhoneUserAgentConfig
import consonance
import uuid
import dissononce
import socket
import logging
import sys
import base64
from axolotl.ecc.curve import Curve

consonance.logger.setLevel(logging.DEBUG)
dissononce.logger.setLevel(logging.DEBUG)

# username is phone number
USERNAME = 77472412416
# on Android fetch client_static_keypair from /data/data/com.whatsapp/shared_prefs/keystore.xml
KEYPAIR = KeyPair.from_bytes(
    base64.b64decode(b"8Ccclxofr7K1KIY2Y2DUjzyTRmsUM1z1jXj9Nzx9mVRtf3toEZBMgkmCMq4gKWVdwftl3DULtMyO15YfIbJOAA==")
)

ENC_PUBKEY = Curve.decodePoint(
    bytearray([
        5, 142, 140, 15, 116, 195, 235, 197, 215, 166, 134, 92, 108,
        60, 132, 56, 86, 176, 97, 33, 204, 232, 234, 119, 77, 34, 251,
        111, 18, 37, 18, 48, 45
    ])
)

WA_PUBLIC = PublicKey(ENC_PUBKEY.publicKey)
# same phone_id/fdid used at registration.
# on Android it's phoneid_id under /data/data/com.whatsapp/shared_prefs/com.whatsapp_preferences.xml
PHONE_ID = uuid.uuid4().__str__()
# create full configuration which will translate later into a protobuf payload
CONFIG = ClientConfig(
    username=USERNAME,
    passive=True,
    useragent=iPhoneUserAgentConfig(
        app_version="2.20.102",
        phone_id=PHONE_ID
    ),
    pushname="consonance",
    short_connect=True
)
ENDPOINT = ("g.whatsapp.net", 443)
HEADER = b"WA\x04\x01"

if __name__ == "__main__":
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(ENDPOINT)
    # send WA header indicating protocol version
    s.send(HEADER)
    # use WASegmentedStream for sending/receiving in frames
    stream = WASegmentedStream(SocketArbitraryStream(s))
    # initialize WANoiseProtocol 2.1
    wa_noiseprotocol = WANoiseProtocol(4, 1)
    # start the protocol, this should attempt a IK handshake since we
    # specifying the remote static public key. The handshake should
    # succeeds if the WA_PUBLIC is valid, but authentication should fail.
    if wa_noiseprotocol.start(stream, CONFIG, KEYPAIR, rs=WA_PUBLIC):
        print("Handshake completed, checking authentication...")
        # we are now in transport phase, first incoming data
        # will indicate whether we are authenticated
        first_transport_data = wa_noiseprotocol.receive()
        # fourth byte is status, 172 is success, 52 is failure
        if first_transport_data[3] == 172:
            print("Authentication succeeded")
        elif first_transport_data[3] == 52:
            print("Authentication failed")
            sys.exit(1)
        else:
            print("Unrecognized authentication response: %s" % (first_transport_data[3]))
            sys.exit(1)
    else:
        print("Handshake failed")
        sys.exit(1)
