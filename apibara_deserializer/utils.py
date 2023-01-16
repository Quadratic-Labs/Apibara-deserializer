from collections import ChainMap
from datetime import datetime, timezone
from functools import lru_cache, wraps
from typing import Callable, Iterable, Union

from apibara.model import BlockHeader
from cachetools import LRUCache, keys
from starknet_py.contract import Contract
from starknet_py.net.client_models import GatewayBlock
from starknet_py.net.gateway_client import GatewayClient


# TODO: check https://docs.openzeppelin.com/contracts-cairo/0.3.1/utilities
def str_to_felt(text: str) -> int:
    if len(text) > 31:
        raise ValueError(
            f"Cannot convert '{text}' to felt because it has more than 31 chars"
            f" ({len(text)})"
        )
    b_text = bytes(text, "ascii")
    return int.from_bytes(b_text, "big")


def felt_to_str(felt: int) -> str:
    length = (felt.bit_length() + 7) // 8
    return felt.to_bytes(length, byteorder="big").decode("utf-8")


def int_to_uint256(a: int) -> tuple:
    """Takes in value, returns uint256-ish tuple."""
    return (a & ((1 << 128) - 1), a >> 128)


def int_to_uint256_dict(a: int) -> dict[str, int]:
    """Takes int value, returns uint256-ish dict."""
    low, high = int_to_uint256(a)
    return {"low": low, "high": high}


def int_to_bytes(a: int) -> bytes:
    length = (a.bit_length() + 7) // 8
    return a.to_bytes(length, byteorder="big")


# def uint256_dict_to_int(a: dict[str, int]) -> int:
#     """Takes uint256-ish dict value, returns int value."""
#     return uint256_to_int((a["low"], a["high"]))


# def uint256_to_int(uint: tuple) -> int:
#     """Takes in uint256-ish tuple, returns value."""
#     return uint[0] + (uint[1] << 128)


# def bytes_to_int(a: bytes) -> int:
#     return int.from_bytes(a, "big")


# def bytes_to_str(a: bytes) -> str:
#     return a.hex()


# def str_to_bytes(a: str) -> bytes:
#     return bytes.fromhex(a)


def async_cached(cache, key=keys.hashkey):
    """Returns decorator function to cache async function results.

    This is a replacement for `@cached()` decorator from cachetools.
    cachetools does not support async at the time of writing.

    Source: https://github.com/aiocoro/async-cached
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            k = key(*args, **kwargs)
            try:
                return cache[k]
            except KeyError:
                pass
            v = await func(*args, **kwargs)
            try:
                cache[k] = v
            except ValueError:
                pass
            return v

        return wrapper

    return decorator


@async_cached(cache=LRUCache(maxsize=128))
async def get_contract(address, client: GatewayClient) -> Contract:
    return await Contract.from_address(address, client=client)


@async_cached(cache=LRUCache(maxsize=128))
async def get_block(block_number: int, client: GatewayClient) -> GatewayBlock:
    return await client.get_block(block_number=block_number)


def get_block_datetime_utc(block: Union[GatewayBlock, BlockHeader]) -> datetime:
    if isinstance(block, GatewayBlock):
        return datetime.fromtimestamp(block.timestamp, timezone.utc)

    if isinstance(block, BlockHeader):
        return block.timestamp.replace(tzinfo=timezone.utc)

    raise ValueError(
        f"block should be either GatewayBlock or BlockHeader, got {block} of type"
        f" {type(block)}"
    )


@lru_cache(maxsize=128)
def get_contract_events(contract: Contract) -> dict:
    return {
        element["name"]: element
        for element in contract.data.abi
        if element["type"] == "event"
    }


def function_accepts(func: Callable, argnames: Iterable) -> bool:
    """Check if the given function has argnames as arguments

    Args:
        func (Callable): the function object
        argnames (Iterable): an iterable of argument names

    Example:
        >>> def foo(x, y, z):
        >>>     pass

        >>> function_accepts(foo, ['x', 'y'])
        >>> True

        >>> function_accepts(foo, ['x', 't'])
        >>> False

    Returns:
        bool: whether the function accepts the arguments or not
    """
    return all(argname in func.__code__.co_varnames for argname in argnames)


def all_annotations(cls) -> ChainMap:
    """Returns a dictionary-like ChainMap that includes annotations for all
    attributes defined in cls or inherited from superclasses."""
    return ChainMap(
        *(c.__annotations__ for c in cls.__mro__ if "__annotations__" in c.__dict__)
    )


def utcnow() -> datetime:
    """Wrapper for datetime.utcnow, it should be used instead of datetime.utcnow
    Tests should mock it to tests functions that uses current time
    """
    # down precision of the time to millisecond to keep it aligned with mongo
    now = datetime.utcnow().replace(tzinfo=timezone.utc)
    millisecond = int(now.microsecond / 10000)
    microsecond = millisecond * 10000
    now = now.replace(microsecond=microsecond)
    return now
