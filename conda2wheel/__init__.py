import argparse
import os
import pprint
import shutil
import sys
import tarfile
import tempfile
import logging
from wheel.egg2wheel import egg2wheel, egg_info_re
from glob import glob
from distlib.metadata import Metadata
from distutils.archive_util import make_archive
import platform
import yaml


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


def copy_to_condadir(condadir, condafile, wheel_dir, tmp_dir):
    extract(condafile, condadir)

    for egg in find_eggifo(condadir):
        metadata = process_egg(egg)
        egg_name = os.path.basename(egg)
        egg_dir = os.path.join(tmp_dir, egg_name)
        copy_toplevels(egg, egg_dir)
        egg_info = os.path.join(egg_dir, "EGG-INFO")
        metadata.write(egg_info, legacy=True)
        egg2wheel(egg_dir, os.path.join(os.getcwd(), wheel_dir))


def copy_to_tempdir(condafile, wheel_dir):
    if not hasattr(tempfile, 'TemporaryDirectory'):
        try:
            tmp = tempfile.mkdtemp()
            condadir = os.path.join(tmp, 'conda')
            copy_to_condadir(condadir, condafile, wheel_dir, tmp)
        except Exception:
            raise
        finally:
            shutil.rmtree(tmp)
    else:
        with tempfile.TemporaryDirectory() as tmp:
            condadir = os.path.join(tmp, 'conda')
            copy_to_condadir(condadir, condafile, wheel_dir, tmp)


def fix_platform(wheel_dir):
    for wheel_file in glob(os.path.sep.join(
            [wheel_dir, '*'])):
        new_wheel_file = wheel_file.replace('-any.', '-%s.' % (platform.machine()))
        new_wheel_file = new_wheel_file.replace('-py', '-cp')
        os.rename(wheel_file, new_wheel_file)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--wheel-dir', '-w', default=os.getcwd())
    parser.add_argument('--debug', action="store_true")
    parser.add_argument('condafile')
    args = parser.parse_args()
    condafiles = glob(args.condafile)

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    for condafile in condafiles:
        wheel_file = copy_to_tempdir(condafile, args.wheel_dir)
    fix_platform(args.wheel_dir)
