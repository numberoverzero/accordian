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
    """Signal.connect does not de-dupe the same function"""
    async def recv():
        pass

    assert not sig.receivers
    sig.connect(recv)
    sig.connect(recv)
    assert sig.receivers == [recv, recv]
