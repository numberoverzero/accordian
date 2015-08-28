def test_start_idempotent(loop, BasicTask):
    """ Calling start multiple times is safe """
    task = BasicTask(loop=loop)

    loop.run_until_complete(task.start())
    assert task.running

    loop.run_until_complete(task.start())
    assert task.running


def test_stop_invokes_shutdown(loop, BasicTask):
    """ stop awaits on _start_shutdown, _complete_shutdown """
    task = BasicTask(loop=loop)

    loop.run_until_complete(task.start())
    assert task.calls == ["start"]

    loop.run_until_complete(task.stop())
    assert task.calls == ["start", "start shutdown", "complete shutdown"]


def test_stop_idempotent(loop, BasicTask):
    """ Calling stop multiple times is safe """
    task = BasicTask(loop=loop)

    loop.run_until_complete(task.start())
    assert task.running

    loop.run_until_complete(task.stop())
    assert not task.running

    loop.run_until_complete(task.stop())
    assert not task.running
