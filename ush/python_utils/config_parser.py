#!/usr/bin/env python3

import os


def structure_dict(dict_o, dict_t):
    """Structure a dictionary based on a template dictionary

    Args:
        dict_o: dictionary to structure (flat one level structure)
        dict_t: template dictionary used for structuring
    Returns:
        A dictionary with contents of dict_o following structure of dict_t
    """
    struct_dict = {}
    for k, v in dict_t.items():
        if isinstance(v, dict):
            r = structure_dict(dict_o, v)
            if r:
                struct_dict[k] = r
        elif k in dict_o.keys():
            struct_dict[k] = dict_o[k]
    return struct_dict


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


