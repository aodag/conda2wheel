from setuptools import setup, find_packages


__author__ = 'Atsushi Odagiri'

requires = [
    "distlib",
    "wheel",
]


setup(
    name="conda2wheel",
    author=__author__,
    zip_safe=False,
    install_requires=requires,
)
