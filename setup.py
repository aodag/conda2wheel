from setuptools import setup, find_packages


__author__ = 'Atsushi Odagiri'

requires = [
    "distlib",
]


setup(
    name="conda2wheel",
    author=__author__,
    install_requires=requires,
)
