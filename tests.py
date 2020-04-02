import asyncio
import accordian
import pytest


@pytest.fixture(scope="function")
def ns():
    return accordian.Namespace()


@pytest.fixture(scope="function")
def sig():
    return accordian.Signal()


def test_same_signal(ns):
    """Within a namespace, all references to one name return the same Signal instance"""
    foo = ns.signal("foo")
    same = ns.signal("foo")
    assert foo is same


def test_different_namespaces():
    """The same name across two namespaces are different signals"""
    ns1 = accordian.Namespace()
    ns2 = accordian.Namespace()
    foo = ns1.signal("foo")
    other_foo = ns2.signal("foo")
    assert foo is not other_foo


def test_new_signal():
    """A signal takes an optional name and starts without any receivers"""
    x = accordian.Signal(name="x")
    anon = accordian.Signal()

    assert x.name == "x"
    assert anon.name is None
    assert x.receivers == anon.receivers == []


def test_connect_regular_fn(sig):
    """Signal.connect only accepts coroutine (async def) functions"""
    def regular():
        pass

    with pytest.raises(ValueError) as excinfo:
        sig.connect(regular)
    assert str(excinfo.value).startswith("Signal.connect requires a coroutine function")


def test_connect_async_fn(sig):
    """Signal.connect returns the original function"""
    async def recv():
        pass

    same = sig.connect(recv)
    assert same is recv


def test_connect_multiple_calls(sig):
    """Signal.connect does not add the same function twice"""
    async def recv():
        pass

    assert not sig.receivers
    sig.connect(recv)
    assert sig.receivers == [recv]
    sig.connect(recv)
    assert sig.receivers == [recv]


def test_no_receivers(sig):
    """No work is performed when a signal has no receivers"""
    assert not sig.receivers

    # no tasks to create
    async def send():
        tasks = sig.send(1, 2, 3, foo="bar", baz=None)
        assert not tasks
    asyncio.run(send())

    # no results from receivers
    async def join():
        return await sig.join(1, 2, 3, foo="bar", baz=None)
    results = asyncio.run(join())
    assert not results


def test_send_does_not_invoke(sig):
    """Signal.send does not block for the tasks to be completed"""
    @sig.connect
    async def recv():
        await asyncio.sleep(0)
        calls.append("called")
    calls = []

    async def send():
        [task] = sig.send()
        assert not task.done()
    asyncio.run(send())
    assert not calls


def test_join_joins_results(sig):
    """Signal.join joins results from all receivers"""
    @sig.connect
    async def r1(*a, **kw):
        """inspects the sizes of *args and **kwargs, ignoring type"""
        await asyncio.sleep(0)
        return len(a), len(kw)

    @sig.connect
    async def r2(a, b, *, foo):
        """only accepts foo as a kwarg"""
        await asyncio.sleep(0)
        return a + b, len(foo)

    async def join():
        results = await sig.join(3, 4, foo="hello")
        assert set(results) == {(2, 1), (7, 5)}
    asyncio.run(join())
