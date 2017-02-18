import argparse
import os
import pprint
import shutil
import sys
import tarfile
import tempfile
from wheel.egg2wheel import egg2wheel, egg_info_re
from distlib.metadata import Metadata


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
    print(egg)
    pkginfo = os.path.join(egg, 'PKG-INFO')
    toplevel = os.path.join(egg, 'top_level.txt')
    if os.path.exists(pkginfo):
        metadata = Metadata(path=pkginfo)
        pprint.pprint(metadata.todict())

    with open(os.path.join(egg, 'top_level.txt')) as t:
        top_levels = list(iter_toplevel(egg))
        print(top_levels)

    return metadata

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('condafile')
    args = parser.parse_args()

    with tempfile.TemporaryDirectory() as tmp:
        condadir = os.path.join(tmp, 'conda')
        extract(args.condafile, condadir)

        for egg in find_eggifo(condadir):
            metadata = process_egg(egg)
            egg_name = os.path.basename(egg)
            print(egg_name)
            egg_dir = os.path.join(tmp, egg_name)
            # os.mkdir(egg_dir)
            print('copy %s to %s' % (os.path.dirname(egg), egg_dir))
            shutil.copytree(os.path.dirname(egg), egg_dir)
            print(egg_dir)
            print(os.path.basename(egg_dir))
            metadata.write(os.path.join(egg_dir, "EGG-INFO"), legacy=True)
            egg_info = egg_info_re.match(os.path.basename(egg_dir)).groupdict()
            print(egg_info)
            egg2wheel(egg_dir, os.path.join(os.getcwd(), 'wheelhouse'))