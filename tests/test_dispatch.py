import asyncio
import pytest


def test_start_idempotent(loop, dispatch):
    loop.run_until_complete(dispatch.start())
    assert dispatch.running

    loop.run_until_complete(dispatch.start())
    assert dispatch.running

    # Prevent complaints about destroying a pending task
    loop.run_until_complete(dispatch.stop())


def test_stop_idempotent(loop, dispatch):
    loop.run_until_complete(dispatch.start())
    assert dispatch.running

    loop.run_until_complete(dispatch.stop())
    assert not dispatch.running

    loop.run_until_complete(dispatch.stop())
    assert not dispatch.running


def test_clean_stop(loop, dispatch):
    """ Stop ensures the main dispatch loop shuts down gracefully """
    loop.run_until_complete(dispatch.start())
    loop.run_until_complete(dispatch.stop())


def test_unknown_event(dispatch):
    """
    An exception should be thrown when trying to register a
    handler for an unknown event.
    """
    with pytest.raises(ValueError):
        dispatch.on("unknown")


def test_register(dispatch):
    event = "my-event"
    params = ["x", "y", "z"]
    dispatch.register(event, params)
    assert "my-event" in dispatch._handlers


def test_register_twice(dispatch):
    event = "my-event"
    params = ["x", "y", "z"]
    dispatch.register(event, params)

    with pytest.raises(ValueError):
        dispatch.register(event, params)


def test_register_running(dispatch, loop):
    event = "my-event"
    params = ["x", "y", "z"]
    loop.run_until_complete(dispatch.start())

    with pytest.raises(RuntimeError):
        dispatch.register(event, params)

    # Prevent complaints about destroying a pending task
    loop.run_until_complete(dispatch.stop())


def test_unregister_unknown(dispatch):
    assert "unknown-event" not in dispatch._handlers
    dispatch.unregister("unknown-event")


def test_unregister_running(dispatch, loop):
    event = "my-event"
    params = ["x", "y", "z"]
    dispatch.register(event, params)

    loop.run_until_complete(dispatch.start())
    with pytest.raises(RuntimeError):
        dispatch.unregister(event)

    # Prevent complaints about destroying a pending task
    loop.run_until_complete(dispatch.stop())


def test_single_handler(dispatch, loop):
    event = "my-event"
    dispatch.register(event, ["foo", "bar"])
    expected = {"foo": 4, "bar": 5}
    called = False

    @dispatch.on(event)
    async def handle(kwargs):
        nonlocal called
        assert kwargs == expected
        called = True

    loop.run_until_complete(dispatch.start())
    loop.run_until_complete(dispatch.trigger(event, expected))
    loop.run_until_complete(dispatch.stop())
    assert called


def test_clear(dispatch, loop):
    event = "my-event"
    kwargs = {"foo": 4}
    dispatch.register(event, ["foo"])

    @dispatch.on(event)
    async def handle(kwargs):
        assert kwargs["foo"] == 4

    loop.run_until_complete(dispatch.trigger(event, kwargs))
    assert dispatch.events
    dispatch.clear()
    assert not dispatch.events


def test_trigger_unknown(dispatch, loop):
    for task in [
        dispatch.start(),
        dispatch.trigger("unknown-event", {"not": "used"}),
        dispatch.stop()
    ]:
        loop.run_until_complete(task)


def test_event_dispatch_not_running(dispatch, loop):
    event = "my-event"
    kwargs = {"foo": 4}
    dispatch.register(event, ["foo"])

    @dispatch.on(event)
    async def handle(kwargs):
        assert kwargs["foo"] == 4

    handler = dispatch._handlers[event]

    with pytest.raises(RuntimeError):
        handler(kwargs)


def test_register_non_async(dispatch, loop):
    """ Event handler will be wrapped in coro if not already async """
    event = "my-event"
    dispatch.register(event, ["foo", "bar"])
    expected = {"foo": 4, "bar": 5}
    called = False

    @dispatch.on(event)
    def handle(kwargs):
        nonlocal called
        assert kwargs == expected
        called = True

    loop.run_until_complete(dispatch.start())
    loop.run_until_complete(dispatch.trigger(event, expected))
    loop.run_until_complete(dispatch.stop())
    assert called


def test_extra_missing_kwargs(dispatch, loop):
    """
    Unexpected kwargs aren't passed to handlers,
    and missing kwargs aren't set to any default value.
    """
    event = "my-event"
    dispatch.register(event, ["foo", "bar"])

    expected = {"foo": 4}
    actual = {"foo": 4, "extra field": "not passed on"}

    @dispatch.on(event)
    def handle(kwargs):
        assert kwargs == expected

    loop.run_until_complete(dispatch.start())
    loop.run_until_complete(dispatch.trigger(event, actual))
    loop.run_until_complete(dispatch.stop())


def test_graceful_cleanup_handler(dispatch, loop):
    event = "my-event"
    dispatch.register(event, [])
    handler = dispatch._handlers[event]
    called = False

    @dispatch.on(event)
    async def handle(kwargs):
        nonlocal called
        # Don't complete the handler until the dispatch
        # has started shutting down
        while handler.running:
            await asyncio.sleep(0, loop=loop)
        called = True

    loop.run_until_complete(dispatch.start())
    loop.run_until_complete(dispatch.trigger(event, {}))
    loop.run_until_complete(dispatch.stop())
    assert called


def test_events_no_block(dispatch, loop):
    """ Handlers for one event do not block handlers for another event """
    dispatch.register("A", [])
    dispatch.register("B", [])
    called = []

    # We'll trigger an "A" event first, but it won't complete until it sees
    # the "B" in called ("B" handler finishes first)
    @dispatch.on("A")
    async def handle_a(kwargs):
        while "B" not in called:
            await asyncio.sleep(0, loop=loop)
        called.append("A")

    @dispatch.on("B")
    async def handle_a(kwargs):
        called.append("B")

    loop.run_until_complete(dispatch.start())
    loop.run_until_complete(dispatch.trigger("A", {}))
    loop.run_until_complete(dispatch.trigger("B", {}))
    loop.run_until_complete(dispatch.stop())
    assert called == ["B", "A"]
