from consonance.structs.keypair import KeyPair
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

consonance.logger.setLevel(logging.DEBUG)
dissononce.logger.setLevel(logging.DEBUG)

# username is phone number
USERNAME = 6283890513211
# on Android fetch client_static_keypair from /data/data/com.whatsapp/shared_prefs/keystore.xml
KEYPAIR = KeyPair.from_bytes(
    base64.b64decode(b"kDZxVPzYhrNKHA2YczenBX495Lfk5eEPNdRV98Eq5Ut1EMsXJP7I1U0jBwmIwchXylf7SdVV25hDLwmr1JgWVQ==")
)
# same phone_id/fdid used at registration.
# on Android it's phoneid_id under /data/data/com.whatsapp/shared_prefs/com.whatsapp_preferences.xml
PHONE_ID = '55a6dced-cfb6-4851-b816-18ab591f1e8a'
# create full configuration which will translate later into a protobuf payload
CONFIG = ClientConfig(
    username=USERNAME,
    passive=True,
    useragent=iPhoneUserAgentConfig(
        app_version="2.22.16.77",
        phone_id=PHONE_ID
    ),
    pushname="wer u",
    short_connect=True
)
PROTOCOL_VERSION = (5, 2)
ENDPOINT = ("e1.whatsapp.net", 443)
HEADER = b"WA" + bytes(PROTOCOL_VERSION)

if __name__ == "__main__":
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(ENDPOINT)
    # send WA header indicating protocol version
    s.send(HEADER)
    # use WASegmentedStream for sending/receiving in frames
    stream = WASegmentedStream(SocketArbitraryStream(s))
    # initialize WANoiseProtocol
    wa_noiseprotocol = WANoiseProtocol(*PROTOCOL_VERSION)
    # start the protocol, this should a XX handshake since
    # we are not passing the remote static public key
    try:
        wa_noiseprotocol.start(stream, CONFIG, KEYPAIR)
        print("Handshake completed, checking authentication...")
        # we are now in transport phase, first incoming data
        # will indicate whether we are authenticated
        first_transport_data = wa_noiseprotocol.receive()
        # fourth + fifth byte are status, [237, 38] is failure
        if first_transport_data[3] == 51:
            print("Authentication succeeded")
        elif list(first_transport_data[3:5]) == [237, 38]:
            print("Authentication failed")
            sys.exit(1)
        else:
            print("Unrecognized authentication response: %s" % (first_transport_data[3]))
            sys.exit(1)
    except:
        print("Handshake failed")
        sys.exit(1)
