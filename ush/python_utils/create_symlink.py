#!/usr/bin/env python3

import os

def create_symlink(target, symlink):
    """Create a symbolic link to the specified target file. If the symlink argument is a directory,
    a symlink with the same name as the target will be created in that directory.

    Args:
        target: target file
        symlink: symbolic link to target file
    Returns:
        None
    """

    if target is None or symlink is None:
        raise TypeError(f"""Invalid arguments:\n{target=}\n{symlink=}""")

    if not os.path.exists(target):
        msg = f"""
            Cannot create symlink to specified target file because the latter does
            not exist or is not a file:
                target = '{target}'"""
        raise Exception(msg)

    # If the symlink argument is a directory, assume you want an identically named symlink to target
    # in the specified directory. This mimics native Unix behavior.
    if os.path.isdir(symlink):
        symlink=os.path.join(symlink,os.path.basename(target))

    os.symlink(target,symlink)
