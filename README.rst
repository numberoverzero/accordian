.. image:: https://img.shields.io/travis/numberoverzero/accordian/master.svg?style=flat-square
    :target: https://travis-ci.org/numberoverzero/accordian
.. image:: https://img.shields.io/pypi/v/accordian.svg?style=flat-square
    :target: https://pypi.python.org/pypi/accordian
.. image:: https://img.shields.io/github/issues-raw/numberoverzero/accordian.svg?style=flat-square
    :target: https://github.com/numberoverzero/accordian/issues


Event dispatch in Python 3.8 using asyncio

Installation
------------

``pip install accordian``

Getting Started
---------------
::

    import asyncio
    from accordian import signal
    my_event = signal("my_event")

    @my_event.connect
    async def pow(x, y):
        await asyncio.sleep(0.1)
        print(f"pow({x}, {y})")
        return x ** y

    @my_event.connect
    async def diff(x, y):
        await asyncio.sleep(0.2)
        print(f"diff({x}, {y})")
        return max(x, y) - min(x, y)


    # create events without blocking
    async def create():
        my_event.send(4, 6)
        my_event.send(0, 1)
    asyncio.run(create())


    # or block and collect results from all receivers
    async def collect():
        results = await my_event.join(10, 3)
        assert set(results) == {1000, 7}
    asyncio.run(collect())


    # signals without receivers return no results
    async def empty():
        sig = signal("unknown")
        results = await sig.join(1, "foo", None)
        assert results == []
    asyncio.run(empty())

Namespaces
==========

By default, ``accordian.signal`` creates signals in a global namespace.  You can create your own namespaces to
group signals together.  Here, a processor is passed the region and stage to create deployment tasks::

    from accordian import Namespace
    regions = {"east": Namespace(), "west": Namespace()}


    @regions["east"].signal("dev").connect
    async def deploy_east_dev(s3_url, creds):
        ...

    @regions["east"].signal("prod").connect
    async def deploy_east_prod(s3_url, creds):
        # remove pre-prod feature flags
        await sanitize_prod(s3_url, "east")
        ...

    @regions["west"].signal("prod").connect
    async def deploy_west_prod(s3_url, creds):
        # legacy region shims
        await patch_west_bundle(s3_url)
        await sanitize_prod(s3_url, "west")
        ...


    async def deploy(region, stage):
        s3_url = await bundle_for_region(region, stage)
        creds = await creds_for_region(region, stage)
        signal = regions[region].signal(stage)

        # create the deployment task without waiting
        signal.send(s3_url, creds)


    # create deployment tasks
    asyncio.run(deploy("east", "dev"))
    asyncio.run(deploy("west", "prod"))


    # wait for deployments to complete
    async def wait_for_tasks():
        running = asyncio.all_tasks()
        await asyncio.wait(running)
    asyncio.run(wait_for_tasks())

Contributing
------------

Contributions welcome!  Please make sure ``tox`` passes before submitting a PR.

Development
-----------

To set up a virtualenv and run the test suite::

    git clone https://github.com/numberoverzero/accordian.git
    make venv
    make

