#!/usr/bin/env python3

import os
import inspect
import shlex
from datetime import datetime, date
from types import ModuleType


def str_to_date(s):
    """Get python datetime object from string.

    Args:
        s: a string
    Returns:
        datetime object or None
    """
    v = None
    try:
        l = len(s)
        if l == 8:
            v = datetime.strptime(s, "%Y%m%d")
        elif l == 10:
            v = datetime.strptime(s, "%Y%m%d%H")
        elif l == 12:
            v = datetime.strptime(s, "%Y%m%d%H%M")
        elif l == 14:
            v = datetime.strptime(s, "%Y%m%d%H%M%S")
    except:
        v = None
    return v


def date_to_str(d, format="%Y%m%d%H%M"):
    """Get string from python datetime object.
    By default it converts to YYYYMMDDHHMM format unless
    told otherwise by passing a different format

    Args:
        d: datetime object
    Returns:
        string in YYYYMMDDHHMM or shorter version of it
    """
    v = d.strftime(format)
    return v


def str_to_type(s, return_string=0):
    """Check if the string contains a float, int, boolean, datetime, or just regular string.
    This will be used to automatically convert environment variables to data types
    that are more convenient to work with. If you don't want this functionality,
    pass return_string = 1

    Args:
        s: a string
        return_string: Set to 1 to return the string itself
                       Set to 2 to return the string itself only for a datetime object
    Returns:
        a float, int, boolean, datetime, or the string itself when all else fails
    """
    s = s.strip("\"'")
    if return_string != 1:
        if s.lower() in ["true", "yes", "yeah"]:
            return True
        if s.lower() in ["false", "no", "nope"]:
            return False
        if s in ["None", "null"]:
            return None
        v = str_to_date(s)
        if v is not None:
            if return_string == 2:
                return s
            return v
        # int
        try:
            v = int(s)
            # treat integers that start with 0 as string
            if len(s) > 1 and s[0] == "0":
                return s
            else:
                return v
        except:
            pass
        # float
        try:
            v = float(s)
            return v
        except:
            pass
    return s


def type_to_str(v):
    """Given a float/int/boolean/date or list of these types, gets a string
    representing their values

    Args:
        v: a variable of the above types
    Returns:
        a string
    """
    if isinstance(v, bool):
        return "TRUE" if v else "FALSE"
    elif isinstance(v, (int, float)):
        pass
    elif isinstance(v, date):
        return date_to_str(v)
    elif v is None:
        return ""
    return str(v)


def list_to_str(v, oneline=False):
    """Given a string or list of string, construct a string
    to be used on right hand side of shell environement variables

    Args:
        v: a string/number, list of strings/numbers, or null string('')
    Returns:
        A string
    """
    if isinstance(v, str):
        return v
    if isinstance(v, list):
        v = [type_to_str(i) for i in v]
        if oneline or len(v) <= 4:
            shell_str = '( "' + '" "'.join(v) + '" )'
        else:
            shell_str = '( \\\n"' + '" \\\n"'.join(v) + '" \\\n)'
    else:
        shell_str = f"{type_to_str(v)}"

    return shell_str


def str_to_list(v, return_string=0):
    """Given a string, construct a string or list of strings.
    Basically does the reverse operation of `list_to_string`.

    Args:
        v: a string
    Returns:
        a string, list of strings or null string('')
    """

    if not isinstance(v, str):
        return v
    v = v.strip()
    if not v:
        return None
    if (v[0] == "(" and v[-1] == ")") or (v[0] == "[" and v[-1] == "]"):
        v = v[1:-1]
        v = v.replace(",", " ")
        tokens = shlex.split(v)
        lst = []
        for itm in tokens:
            itm = itm.strip()
            if itm == "":
                continue
            # bash arrays could be stored with indices ([0]=hello ...)
            if "=" in itm:
                idx = itm.find("=")
                itm = itm[idx + 1 :]
            lst.append(str_to_type(itm, return_string))
        return lst
    return str_to_type(v, return_string)


