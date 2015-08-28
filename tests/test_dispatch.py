import accordian
import pytest


def test_unknown_event(loop):
    """
    An exception should be thrown when trying to register a
    handler for an unknown event.
    """
    dispatch = accordian.Dispatch(loop=loop)
    with pytest.raises(ValueError):
        dispatch.on("unknown")


def test_clean_stop(loop):
    dispatch = accordian.Dispatch(loop=loop)
    loop.run_until_complete(dispatch.start())
    loop.run_until_complete(dispatch.stop())
