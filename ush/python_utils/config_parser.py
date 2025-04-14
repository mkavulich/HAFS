#!/usr/bin/env python3

import os


def check_structure_dict(dict_o, dict_t):
    """Check if a dictionary's structure follows a template.
    The invalid entries are returned as a dictionary.
    If all entries are valid, returns an empty dictionary

    Args:
        dict_o: target dictionary
        dict_t: template dictionary to compare structure to
    Returns:
        dict:  Invalid key-value pairs.
    """
    inval = {}
    for k, v in dict_o.items():
        if k in dict_t.keys():
            v1 = dict_t[k]
            if isinstance(v, dict) and isinstance(v1, dict):
                r = check_structure_dict(v, v1)
                if r:
                    inval.update(r)
        else:
            inval[k] = v
    return inval


