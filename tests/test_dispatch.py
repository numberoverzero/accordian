import asyncio
import accordian
import pytest


def test_unknown_event():
    '''
    An exception should be thrown when trying to register a
    handler for an unknown event.
    '''
    loop = asyncio.new_event_loop()
    dispatch = accordian.Dispatch(loop)
    with pytest.raises(ValueError):
        dispatch.on("unknown")
