import accordian


def test_start_idempotent(loop):
    ''' Calling `RestartableTask.start` multiple times is safe '''
    task = accordian.RestartableTask(loop=loop)
    assert not task.running

    loop.run_until_complete(task.start())
    assert task.running

    loop.run_until_complete(task.start())
    assert task.running


def test_stop_invokes_shutdown(loop, BasicTask):
    ''' `RestartableTask.stop` awaits on _start_shutdown, _complete_shutdown '''
    task = BasicTask(loop=loop)

    loop.run_until_complete(task.start())
    assert task.calls == ["start"]

    loop.run_until_complete(task.stop())
    assert task.calls == ["start", "start shutdown", "complete shutdown"]
