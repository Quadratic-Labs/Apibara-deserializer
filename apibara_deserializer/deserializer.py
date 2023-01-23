import asyncio
from datetime import datetime
from typing import Any, Callable, Optional, Type, Union

from apibara.indexer import Info
from apibara.starknet import felt
from apibara.starknet.proto.starknet_pb2 import Event
from starknet_py.net.gateway_client import GatewayClient
from starknet_py.utils.data_transformer.data_transformer import CairoSerializer

from .utils import (
    felt_to_str,
    function_accepts,
    get_block,
    get_block_datetime_utc,
    get_contract,
    get_contract_events,
    int_to_bytes,
)


class BlockNumber(int):
    pass


class Uint256(int):
    pass


# pylint: disable=unused-argument
async def deserialize_block_number(
    block_number: BlockNumber,
    info: Info,
    starknet_event: Event,
    starknet_client: Optional[GatewayClient] = None,
) -> datetime:
    starknet_client = starknet_client or info.context.get("starknet_client")

    assert starknet_client, (
        "starknet_client should be either passed as an argument or provided in"
        " info.context"
    )

    block = await get_block(block_number=block_number, client=starknet_client)
    return get_block_datetime_utc(block)


# serializers could take info, block and event parameter just like from_starknet_event
# see the block_number_serializer above for an example
Serializer = Union[Callable[[Any], Any], Callable[[Any, Info, Event], Any]]


ALL_DESERIALIZERS: dict[Type, Serializer] = {
    int: lambda x: x,  # an int is returned as is
    bool: lambda x: x,  # a bool is returned as is
    BlockNumber: deserialize_block_number,
    bytes: int_to_bytes,
    str: felt_to_str,
}


# pylint: disable=too-many-locals, too-many-arguments, too-many-branches
async def deserialize_apibara_event(
    info: Info,
    starknet_event: Event,
    fields: Optional[dict[str, Type]] = None,
    event_dataclass: Optional[Type] = None,
    event_abi: Optional[dict] = None,
    starknet_client: Optional[GatewayClient] = None,
    deserializers: Optional[dict[Type, Serializer]] = None,
) -> dict:
    # TODO: isn't this more confusing ? Isn't it better to only accept fields param
    # and tell users in the doc that they can use a dataclass and pass the __annotations__
    # field ?
    # fields param is prioritized over event_class if both are passed
    if fields is None:
        if event_dataclass:
            if hasattr(event_dataclass, "__annotations__"):
                fields = event_dataclass.__annotations__
            else:
                raise ValueError(
                    f"{event_dataclass} doesn't have any __annotations__, it should"
                    " be a dataclass"
                )
        else:
            raise ValueError("Either fields or event_dataclass should be passed")

    starknet_client = starknet_client or info.context.get("starknet_client")

    if starknet_client is None:
        raise ValueError(
            "starknet_client should be either passed as an argument or provided in"
            " info.context"
        )

    if deserializers is None:
        deserializers = ALL_DESERIALIZERS

    contract_address = felt.to_int(starknet_event.from_address)
    contract = await get_contract(contract_address, starknet_client)

    event_selector = felt.to_int(starknet_event.keys[0])

    if event_abi is None:
        contract_events = get_contract_events(contract)
        # Takes the abi of the event we want to serialize
        event_abi = contract_events[event_selector]

    # Creates CairoSerializer with contract's identifier manager
    cairo_serializer = CairoSerializer(contract.data.identifier_manager)

    # Transforms cairo data to python (needs types of the values and values)
    event_data = [felt.to_int(b) for b in starknet_event.data]
    python_data = cairo_serializer.to_python(
        value_types=event_abi["data"],
        values=event_data,
    )

    # TODO: validate the matching between the fields and their types
    # in python_data and __annotations__
    kwargs = {}
    for name, field_type in fields.items():
        if deserializer := deserializers.get(field_type):
            if not hasattr(python_data.tuple_value, name):
                raise AttributeError(
                    f"Received event {event_selector}({python_data}) doesn't"
                    f" have attribute named {name}",
                )

            value = getattr(python_data, name)

            # Pass info and event arguments if the serializer accepts them
            if function_accepts(deserializer, ("info", "starknet_event")):
                deserialized_value = deserializer(
                    value,
                    info=info,
                    starknet_event=starknet_event,
                )
            else:
                deserialized_value = deserializer(value)

            if asyncio.iscoroutine(deserialized_value):
                deserialized_value = await deserialized_value

            kwargs[name] = deserialized_value
        else:
            raise ValueError(f"No deserializer found for type {field_type}")

    return kwargs
