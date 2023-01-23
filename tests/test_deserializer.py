import json
from unittest.mock import Mock

from apibara.starknet.proto.starknet_pb2 import Event
from google.protobuf.json_format import Parse
from starknet_py.net.gateway_client import GatewayClient

from apibara_deserializer import deserialize_apibara_event

STARKNET_NETWORK_URL = "https://alpha-mainnet.starknet.io"


async def test_deserialize_apibara_event():
    starknet_client = GatewayClient(STARKNET_NETWORK_URL)
    info = Mock()

    class Transfer:
        from_: bytes
        to: bytes
        amount: int

    event_abi = {
        "data": [
            {"name": "from_", "type": "felt"},
            {"name": "to", "type": "felt"},
            {"name": "amount", "type": "felt"},
        ],
        "keys": [],
        "name": "Transfer",
        "type": "event",
    }

    starknet_event_json = json.dumps(
        {
            "fromAddress": {
                "loLo": "332481695008573172",
                "loHi": "10275357600199264326",
                "hiLo": "4962358456359875611",
                "hiHi": "1540996537167924679",
            },
            "keys": [
                {
                    "loLo": "43291672051021844",
                    "loHi": "9523478383738879299",
                    "hiLo": "4202873905533468465",
                    "hiHi": "17001379762819667689",
                }
            ],
            "data": [
                {
                    "loLo": "74454628635187476",
                    "loHi": "17132411491813792576",
                    "hiLo": "11818884661055719754",
                    "hiHi": "6184059052638882344",
                },
                {
                    "loLo": "283030266857923045",
                    "loHi": "5107303412481486643",
                    "hiLo": "4813884544585179479",
                    "hiHi": "6308492063849770993",
                },
                {"hiHi": "1000"},
            ],
        }
    )

    starknet_event = Parse(starknet_event_json, Event())

    expected_deserialized_event = {
        "from_": (
            b"\x01\x08\x84\x17\x1b\xaf\x19\x14\xed\xc2\x8dz\xfba\x9b@"
            b"\xa4\x05\x1c\xfa\xe7\x8a\tJU\xd20\xf1\x9e\x94J("
        ),
        "to": (
            b"\x03\xed\x86\x874\xc0!\xe5F\xe0\xc9d\xdd\x19o3B\xceZ|"
            b'\xfd\xbe!WW\x8cD\x1b\xb6"\xef\xf1'
        ),
        "amount": 1000,
    }

    deserialized_event = await deserialize_apibara_event(
        info=info,
        starknet_event=starknet_event,
        event_dataclass=Transfer,
        event_abi=event_abi,
        starknet_client=starknet_client,
    )

    assert deserialized_event == expected_deserialized_event
