from os.path import dirname, abspath, join, exists
from setuptools import setup

try:
    from pypandoc import convert
    read_md = lambda f: convert(f, 'rst')
except ImportError:
    print("warning: pypandoc module not found, could not convert Markdown to RST")
    read_md = lambda f: open(f, 'r').read()

long_description = None
if exists("README.md"):
    long_description = read_md("README.md")

install_reqs = [req for req in open(abspath(join(dirname(__file__), 'requirements.txt')))]

setup(
    name = "vp9dash",
    version = "0.0.1",
    author = "Jonas Birme",
    author_email = "jonas.birme@eyevinn.se",
    description = "FFMpeg wrapper script to create VP9 MPEG-DASH packages",
    long_description=long_description,
    license = "MIT",
    install_requires=install_reqs,
    url = "https://github.com/Eyevinn/vp9-dash",
    packages = ['vp9dash' ],
    entry_points = {
        'console_scripts': [
            'vp9-dash=vp9dash.wrapper:main',
        ]
    }
)

