import accordian
import pytest


@pytest.fixture(scope="function")
def ns():
    return accordian.Namespace()


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
