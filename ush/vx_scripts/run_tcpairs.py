#!/usr/bin/env python3

"""
Runtime script for UFS Verification TCPAIRS task
"""

import argparse

try:
    import uwtools.api.config as uwconfig
except ImportError:
    raise ImportError("Could not load uwtools, have you loaded your conda environment correctly?")


if __name__ == "__main__":
    #Parse arguments
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Script will be run with more verbose output')
    parser.add_argument('-c', '--config_file', type=str, default='var_defns.yaml',
                        help='Config file containing experiment settings')
    pargs = parser.parse_args()

    config_d=uwconfig.get_yaml_config(pargs.config_file)

    print(config_d)

