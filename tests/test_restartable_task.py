import accordian


def test_start_idempotent(run, loop):
    ''' Calling `RestartableTask.start` multiple times is safe '''
    task = accordian.RestartableTask(loop)
    assert not task.running

    run(task.start())
    assert task.running

    run(task.start())
    assert task.running
