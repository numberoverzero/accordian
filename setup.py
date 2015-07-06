from setuptools import setup, find_packages


setup(
    name='accordian',
    version='0.2.0',
    description='Event dispatch in Python 3.5 using asyncio',
    long_description=open('README.md').read(),
    author='Joe Cross',
    author_email='joe.mcross@gmail.com',
    url='http://github.com/numberoverzero/accordian/',
    py_modules=['accordian'],
    packages=find_packages(exclude=('tests', 'examples')),
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
    keywords='async asyncio'
)
