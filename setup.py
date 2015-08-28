from setuptools import setup


def get_version():
    with open("accordian.py") as f:
        for line in f:
            if line.startswith("__version__"):
                return eval(line.split("=")[-1])

setup(
    name='accordian',
    version=get_version(),
    description='Event dispatch in Python 3.5 using asyncio',
    long_description=open('README.rst').read(),
    author='Joe Cross',
    author_email='joe.mcross@gmail.com',
    url='http://github.com/numberoverzero/accordian/',
    py_modules=['accordian'],
    install_requires=[],
    license='MIT',
    platforms='any',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='async asyncio dispatch'
)
