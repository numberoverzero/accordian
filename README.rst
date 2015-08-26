.. image:: https://img.shields.io/travis/numberoverzero/accordian/master.svg?style=flat-square
    :target: https://travis-ci.org/numberoverzero/accordian
.. image:: https://img.shields.io/coveralls/numberoverzero/accordian/master.svg?style=flat-square
    :target: https://coveralls.io/github/numberoverzero/accordian
.. image:: https://img.shields.io/pypi/v/accordian.svg?style=flat-square
    :target: https://pypi.python.org/pypi/accordian
.. image:: https://img.shields.io/github/issues-raw/numberoverzero/accordian.svg?style=flat-square
    :target: https://github.com/numberoverzero/accordian/issues


Event dispatch in Python 3.5 using asyncio

Installation
------------

``pip install accordian``

Getting Started
---------------
::

    import asyncio
    import accordian
    import random

    loop = asyncio.new_event_loop()

    dispatch = accordian.Dispatch(loop=loop)
    dispatch.register("my_event", ["id", "value"])


    @dispatch.on("my_event")
    async def handle(id, value):
        sleep = 5.0 * random.random()
        print("Handling `my_event(id={})` in {} seconds.".format(id, sleep))
        await asyncio.sleep(sleep, loop=loop)
        print("`Completed my_event(id={})`!".format(id))


    ids = range(4)
    values = [random.random() for _ in ids]
    for id, value in zip(ids, values):
        params = {"id": id, "value": value}
        dispatch.trigger("my_event", params)

    loop.create_task(dispatch.start())
    loop.run_until_complete(asyncio.sleep(0.01, loop=loop))
    loop.run_until_complete(dispatch.stop())


Contributing
------------

Contributions welcome!  Please make sure `tox` passes (including flake8) before submitting a PR.

Development
-----------

accordian uses `tox`, `pytest` and `flake8`.  To get everything set up::

    # RECOMMENDED: create a virtualenv with:
    #     mkvirtualenv accordian
    git clone https://github.com/numberoverzero/accordian.git
    pip install tox
    tox
