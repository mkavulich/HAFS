#!/usr/bin/env python3

import logging
import os
import shutil
from datetime import datetime
from textwrap import dedent


def check_for_preexist_dir_file(path, method):
    """Check for a preexisting directory or file and, if present, deal with it
    according to the specified method

    Args:
        path: path to directory
        method: could be any of [ 'delete', 'rename', 'quit' ]
    Returns:
        None
    """

    if method not in ["delete", "rename", "quit"]:
        raise ValueError(f"Invalid method for dealing with pre-existing directory specified: {method=}")

    #If last character of path is a slash, remove it"
    path = path.rstrip('/')
    if os.path.exists(path):
        if method == "delete":
            shutil.rmtree(path)
        elif method == "rename":
            now = datetime.now()
            d = now.strftime("_old_%Y%m%d_%H%M%S")
            new_path = path + d
            logging.info(
                f"""
                Specified directory or file already exists:
                    {path}
                Moving (renaming) preexisting directory or file to:
                    {new_path}"""
            )
            os.rename(path, new_path)
        else:
            raise FileExistsError(
                dedent(
                    f"""
                Specified directory or file already exists
                    {path}"""
                )
            )
