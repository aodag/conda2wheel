import argparse
import os
import pprint
import shutil
import sys
import tarfile
import tempfile
import logging
from wheel.egg2wheel import egg2wheel, egg_info_re
from distlib.metadata import Metadata

logger = logging.getLogger(__name__)


def extract(condafile, workdir):
    with tarfile.open(condafile) as f:
        f.extractall(workdir)


def find_eggifo(workdir):
    for root, dirs, files in os.walk(workdir):
        for d in dirs:
            if d.endswith('.egg-info'):
                yield os.path.join(root, d)


def iter_toplevel(egg):
    with open(os.path.join(egg, 'top_level.txt')) as t:
        for line in t:
            line = line.strip()
            if line:
                yield line

def process_egg(egg):
    logger.debug(egg)
    pkginfo = os.path.join(egg, 'PKG-INFO')
    toplevel = os.path.join(egg, 'top_level.txt')
    if os.path.exists(pkginfo):
        metadata = Metadata(path=pkginfo)
        logger.debug(metadata.todict())

    return metadata

def copy_toplevels(egg, egg_dir):

    with open(os.path.join(egg, 'top_level.txt')) as t:
        top_levels = list(iter_toplevel(egg))
        for top_level in top_levels:
            src = os.path.join(os.path.dirname(egg), top_level)
            dest = os.path.join(egg_dir, top_level)
            logger.debug('copy %s to %s' % (src, dest))
            shutil.copytree(src, dest)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--wheel-dir', '-w', default=os.getcwd())
    parser.add_argument('--debug', action="store_true")
    parser.add_argument('condafile')
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    with tempfile.TemporaryDirectory() as tmp:
        condadir = os.path.join(tmp, 'conda')
        extract(args.condafile, condadir)

        for egg in find_eggifo(condadir):
            metadata = process_egg(egg)
            egg_name = os.path.basename(egg)
            egg_dir = os.path.join(tmp, egg_name)
            copy_toplevels(egg, egg_dir)
            metadata.write(os.path.join(egg_dir, "EGG-INFO"), legacy=True)
            egg_info = egg_info_re.match(os.path.basename(egg_dir)).groupdict()
            egg2wheel(egg_dir, os.path.join(os.getcwd(), args.wheel_dir))