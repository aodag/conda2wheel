import os
from setuptools import setup, find_packages


here = os.path.dirname(__file__)

__version__ = '0.1'

__author__ = 'Atsushi Odagiri'
__author_email__ = 'aodagx@gmail.com'


def _read(filename):
    try:
        with open(os.path.join(here, filename)) as f:
            return f.read()
    except Exception:
        return ""

requires = [
    "distlib",
    "wheel",
]

points = {
    "console_scripts": [
        "conda2wheel=conda2wheel:main",
    ]
}

setup(
    name="conda2wheel",
    author=__author__,
    author_email=__author_email__,
    url="https://github.com/aodag/conda2wheel",
    version=__version__,
    zip_safe=False,
    packages=find_packages(),
    description="``conda2wheel`` converts conda format packages to wheel format packages.",
    long_description=_read("README.rst") + "\n" + _read("ChangeLog.rst"),
    install_requires=requires,
    entry_points=points,
)
