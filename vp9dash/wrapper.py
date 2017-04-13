# Copyright 2017 Eyevinn Technology. All rights reserved
# Use of this source code is governed by a MIT License
# license that can be found in the LICENSE file.
# Author: Jonas Birme (Eyevinn Technology)
import argparse
import logging
import sys
from vp9dash import VP9Dash

logger = logging.getLogger('vp9dash')

def main():
    parser = argparse.ArgumentParser(description='FFMpeg wrapper script to create VP9 MPEG-DASH packages')
    parser.add_argument('source', metavar='SRC', default=None, help='Source file')
    parser.add_argument('output', metavar='OUTPUT', default='out', help='Output name')
    parser.add_argument('--debug', dest='debug', action='store_true', default=False, help='Print debug info')
    parser.add_argument('--nocleanup', dest='nocleanup', action='store_true', default=False, help='Do not remove temp files')
    args = parser.parse_args()

    hdlr = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.WARNING)
    if args.debug:
        logger.setLevel(logging.DEBUG)

    wrapper = VP9Dash(args.source, not args.nocleanup)
    wrapper.toDASH(args.output)

if __name__ == '__main__':
    try:
        main()
    except Exception, err:
        raise