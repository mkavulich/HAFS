#!/usr/bin/env python3
  
"""
User interface to create a workflow xml for running METplus verification tasks
"""

import argparse
import copy
import logging
import os
import shutil
import sys


from pathlib import Path
from textwrap import dedent

import yaml

from get_crontab_contents import add_crontab_line
from python_utils import (
    cfg_to_yaml_str,
    check_structure_dict,
    check_for_preexist_dir_file,
    create_symlink,
    flatten_dict,
    str_to_list,
)

import uwtools.api.template as uwtemplate
import uwtools.api.config as uwconfig
import uwtools.api.rocoto as uwrocoto


def generate_vx_workflow(vx_config):
    """Function to generate the rocoto XML for running verification with METplus in the HAFS app.
    The input is a dictionary containing the appropriate settings for a given experiment; see
    config_defaults.yaml for the available options.

    Args:
    """

    # First of all, expand experiment directory if necessary, then create path
    vx_config["workflow"].update({ "EXPTDIR": os.path.abspath(vx_config["workflow"].get("EXPTDIR")) })
    exptdir = vx_config["workflow"].get("EXPTDIR")
    preexisting_dir_method = vx_config["workflow"].get("PREEXISTING_DIR_METHOD")
    try:
        check_for_preexist_dir_file(exptdir, preexisting_dir_method)
    except ValueError:
        logger.exception(
            f"""
            Check that the following values are valid:
            EXPTDIR {exptdir}
            PREEXISTING_DIR_METHOD {preexisting_dir_method}
            """
        )
        raise
    except FileExistsError:
        errmsg = dedent(
            f"""
            EXPTDIR ({exptdir}) already exists, and PREEXISTING_DIR_METHOD = {preexisting_dir_method}

            To ignore this error, delete the directory, or set 
            PREEXISTING_DIR_METHOD = delete, or
            PREEXISTING_DIR_METHOD = rename
            in your config file.
            """
        )
        raise FileExistsError(errmsg) from None

    os.mkdir(exptdir)

    # Set the full path to the rocoto workflow xml file for verification. 
    vx_xml_fn = vx_config["workflow"]["VX_XML_FN"]
    vx_xml_fp = os.path.join(
        vx_config["workflow"]["EXPTDIR"],
        vx_xml_fn,
    )

    # Create a symlink in the experiment directory that points to the workflow
    # launch script, and the utility needed to read the var_defns yaml file from bash
    wflow_launch_script_fp = vx_config["workflow"]["LAUNCH_SCRIPT_FP"]
    wflow_launch_script_fn = vx_config["workflow"]["LAUNCH_SCRIPT_FN"]
    create_symlink(wflow_launch_script_fp, os.path.join(exptdir, wflow_launch_script_fn))
    create_symlink(os.path.join(vx_config["user"]["USHdir"], "bash_utils", "source_yaml.sh"), exptdir)

    # Expand all references to other variables and populate jinja templates
#    vx_config = uwconfig.get_yaml_config(vx_config)
    print("Before deref:\n\n")
    print(vx_config)
    vx_config.dereference()
    print("After deref:\n\n")
    print(vx_config)


#    # Call uwtools "uwtemplate.render" to generate Rocoto XML from yaml template
#    logging.debug("Calling uwtools 'uwtemplate.render' to generate Rocoto XML from yaml template")
#    logging.debug("uwtemplate.render(input_file = template_xml_fp,output_file = vx_xml_fp,values_src = rocoto_yaml_fp)")
#    rocoto_yaml_fp = vx_config["workflow"]["WFLOW_YAML_FP"]
#    logging.debug(f"{template_xml_fp=}")
#    logging.debug(f"{vx_xml_fp=}")
#    logging.debug(f"{rocoto_yaml_fp=}")
#    uwtemplate.render(
#        input_file = template_xml_fp,
#        output_file = vx_xml_fp,
#        values_src = rocoto_yaml_fp,
#        )

    # Write the variable definitions file
#    all_lines = cfg_to_yaml_str(vx_config)
#    var_defns_fp = vx_config["workflow"]["VAR_DEFNS_FP"]
#    var_defns_cfg = copy.deepcopy(vx_config)
#    with open(var_defns_fp, "a") as f:
#        f.write(cfg_to_yaml_str(var_defns_cfg))
    vx_config.dereference()
    vx_config.dump(Path(vx_config["workflow"]["VAR_DEFNS_FP"]))
#    uwconfig.realize(input_config=vx_config,output_file=vx_config["workflow"]["VAR_DEFNS_FP"],stdin_ok=True)

#    # Load the workflow from the rocoto: section (defined in workflow_blocks file(s))
#    # Write to an experiment yaml file
#    uwconfig.realize(
#        input_config=uwconfig.get_yaml_config(vx_config["rocoto"]),
#        output_file=experiment_file,
#        update_config=experiment_config,
#    )

    # Create rocoto xml by reading var_defns file we just created
    rocoto_valid = uwrocoto.realize(config=vx_config["rocoto"], output_file=vx_config["workflow"]["WFLOW_YAML_FP"])
    if not rocoto_valid:
        sys.exit(1)

    # To have a record of how this experiment/workflow was generated, copy
    # the user configuration file to the experiment directory.
    shutil.copy(os.path.join(vx_config["user"]["USHdir"], config["workflow"]["VX_CONFIG_FN"]), vx_config["workflow"]["EXPTDIR"])

    # For convenience, print out the commands that need to be issued on the
    # command line in order to launch the workflow and to check its status.
    # Also, print out the line that should be placed in the user's cron table
    # in order for the workflow to be continually resubmitted.
    vx_xml = vx_config["workflow"]["VX_XML_FN"]
    wflow_db_fn = f"{os.path.splitext(vx_xml)[0]}.db"
    rocotorun_cmd = f"rocotorun -w {vx_xml} -d {wflow_db_fn} -v 10"
    rocotostat_cmd = f"rocotostat -w {vx_xml} -d {wflow_db_fn} -v 10"

    logging.info(
            f"""
            To launch the workflow, issue the rocotorun command, as follows:

              > {rocotorun_cmd}

            To check on the status of the workflow, issue the rocotostat command:

              > {rocotostat_cmd}

            """
        )

    # If we got to this point everything was successful: move the log
    # file to the experiment directory.
#    os.rename(logfile, vx_config["workflow"]["EXPTDIR"])


def load_config_populate_dict(homedir, default_config, user_config, machine_config):
    """Load in the default, machine, and user configuration files into
    Python dictionaries. Return the combined workflow dictionary. If duplicate values are encountered,
    duplicates are treated in priority of user config > machine config > default config

    Args:
      homedir            (str): Path to the top-level HAFS directory
      default_config     (str): Path to the default config YAML
      user_config        (str): Path to the user-provided config YAML
      machine_config     (str): Path to the machine-specific config YAML

    Returns:
      Python dict of configuration settings from YAML files.
    """

    ushdir = os.path.join(homedir, "ush")

    # Load the default config.
    logging.debug(f"Loading config defaults file {default_config}")
    cfg_d = uwconfig.get_yaml_config(default_config)
    logging.debug(f"Read in the following values from config defaults file:\n")
    logging.debug(cfg_d)

    # Set "Home" directory, the top-level HAFS directory, and "ush" directory
    cfg_d["user"]["HOMEdir"] = homedir
    cfg_d["user"]["USHdir"] = ushdir

    # Load the user config file, then ensure all user-specified
    # variables correspond to a default value.
    if not os.path.exists(user_config):
        raise FileNotFoundError(
            f"""
            User config file not found:
            user_config = {user_config}
            """
        )

    try:
        cfg_u = uwconfig.get_yaml_config(user_config)
        logging.debug(f"Read in the following values from YAML config file {user_config}:\n")
        logging.debug(cfg_u)
    except:
        errmsg = dedent(
            f"""\n
            Could not load YAML config file:  {user_config}
            Reference the above traceback for more information.
            """
        )
        raise Exception(errmsg)

    # NO EQUIVALENT IN UWTOOLS
    # Make sure the keys in user config match those in the default
    # config.
    invalid = check_structure_dict(cfg_u, cfg_d)

    # Task and metatask entries can be added arbitrarily under the
    # rocoto section. Remove those from invalid if they exist
    for key in invalid.copy().keys():
        if key.split("_", maxsplit=1)[0] in ["task", "metatask"]:
            invalid.pop(key)
            logging.info(f"Found and allowing key {key}")

    if invalid:
        errmsg = f"Invalid key(s) specified in {user_config}:\n"
        for entry in invalid:
            errmsg = errmsg + f"{entry} = {invalid[entry]}\n"
        errmsg = errmsg + f"\nCheck {default_config} for allowed user-specified variables\n"
        raise Exception(errmsg)

    # Mandatory variables *must* be set in the user's config; the default value is invalid
    mandatory = ["user.MACHINE", "user.ACCOUNT", "hafs.DATE_FIRST_CYCL"]
    for val in mandatory:
        sect, key = val.split(".")
        user_setting = cfg_u.get(sect, {}).get(key)
        if user_setting is None:
            raise Exception(
                f"""Mandatory variable "{val}" not found in
            user config file {user_config}"""
            )

    # Load the machine config file
    machine = cfg_u.get("user").get("MACHINE").upper()
    cfg_d["user"]["MACHINE"] = machine

    if not machine_config:
        machine_file = os.path.join(ushdir, "machine", f"{machine.lower()}.yaml")

    if not os.path.exists(machine_file):
        raise FileNotFoundError(
            dedent(
                f"""
            The machine file {machine_file} does not exist.
            Check that you have specified the correct machine
            ({machine}) in your config file {user_config}"""
            )
        )
    logging.debug(f"Loading machine defaults file {machine_file}")
    machine_cfg = uwconfig.get_yaml_config(machine_file)

    # CAN WE USE get_yaml_config HERE? CHECK MPAS APP
    # Put the entries expanded under taskgroups in tasks
    workflow_blocks = []
    parmwflow=os.path.join(cfg_d["user"]["HOMEdir"],"parm","wflow")
    for b in cfg_d["user"]["workflow_blocks"]:
        workflow_blocks.append(os.path.join(parmwflow,b))
    workflow_config = None
    for workflow_block in workflow_blocks:
        if not os.path.isfile(workflow_block):
            msg=f"\n{workflow_block} not found in {parmwflow}\n"
            msg+="Check the value of 'workflow_blocks' in your config file"
            raise FileNotFoundError(msg)
        if workflow_config is None:
            workflow_config = uwconfig.get_yaml_config(workflow_block)
        else:
            workflow_config.update_values(uwconfig.get_yaml_config(workflow_block))
    workflow_config.update_values(cfg_d)


    # DO NOT NEED THIS IF WE ARE USING UW ROCOTO GENERATION
    def add_jobname(tasks):
        """ Add the jobname entry for all the tasks in the workflow """

        if not isinstance(tasks, dict):
            return
        for task, task_settings in tasks.items():
            task_type = task.split("_", maxsplit=1)[0]
            if task_type == "task":
                # Use the provided attribute if it is present, otherwise use
                # the name in the key
                tasks[task]["jobname"] = \
                    task_settings.get("attrs", {}).get("name") or \
                    task.split("_", maxsplit=1)[1]
            elif task_type == "metatask":
                add_jobname(task_settings)


    # Add jobname entry to each remaining task
#    add_jobname(workflow_config["tasks"])

    # Update default config with the constants, the machine config, and
    # then the user_config
    # Recall: update_dict updates the second dictionary with the first,
    # and so, we update the default config settings in place with all
    # the others.

    #
    for cfg in [workflow_config,machine_cfg,cfg_u]:
        cfg_d.update_values(cfg)


    cfg_d.dereference()


    # Do any conversions of data types
    for sect, settings in cfg_d.items():
        for k, v in settings.items():
            if not (v is None or v == "") and isinstance(v, str):
                cfg_d[sect][k] = str_to_list(v)

    return cfg_d


def validate_config(config):
    """
    Validates the values in the provided config dictionary against acceptable values in 
    '"valid_param_vals.yaml'. Also runs any necessary consistency checks between variables.
    """

    #
    # -----------------------------------------------------------------------
    #
    # Check validity of parameters in one place, here in the end.
    #
    # -----------------------------------------------------------------------
    #

    # CHECK PR FOR THIS LOOP: https://github.com/NOAA-GSL/ufs-srweather-app/pull/263/files
    # loop through the flattened config and check validity of params
    cfg_v = uwconfig.get_yaml_config(os.path.join(ushdir, "valid_param_vals.yaml"))
    for k, v in flatten_dict(config).items():
        if v is None or v == "":
            continue
        vkey = "valid_vals_" + k
        if (vkey in cfg_v):
            if (type(v) == list):
                if not(all(ele in cfg_v[vkey] for ele in v)):
                    raise Exception(
                        dedent(f"""
                        The variable
                            {k} = {v}
                        in the user's configuration has at least one invalid value.  Possible values are:
                            {k} = {cfg_v[vkey]}"""
                    ))
            else:
                if not (v in cfg_v[vkey]):
                    raise Exception(
                        dedent(f"""
                        The variable
                            {k} = {v}
                        in the user's configuration does not have a valid value.  Possible values are:
                            {k} = {cfg_v[vkey]}"""
                    ))

    return config


def add_workflow_to_cron(mins,config,debug):
    """
    Adds the workflow launch script to crontab, so that the rocoto workflow will be advanced
    automatically at the specified interval

    Args:
      mins     (int): Number of minutes between calls to script
      config  (dict): Python dict of configuration settings from YAML files.
      debug   (bool): Debug mode, run with additional output

    Returns:
      None
    """

    launch_script_fn = config["workflow"].get("LAUNCH_SCRIPT_FN")
    launch_log_fn = config["workflow"].get("LAUNCH_LOG_FN")
    exptdir = config["workflow"].get("EXPTDIR")
    crontab_line = (f"""*/{mins} * * * * cd {exptdir} && ./{launch_script_fn} TRUE >> ./{launch_log_fn} 2>&1"""
    )

    add_crontab_line(called_from_cron=False,crontab_line=crontab_line,exptdir=exptdir,debug=debug)

def setup_logging(logfile: str = "log.generate_hafs_vx_workflow", debug: bool = False) -> None:
    """
    Sets up logging, printing high-priority (INFO and higher) messages to screen, and printing all
    messages with detailed timing and routine info in the specified text file.
    """
    logging.getLogger().setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(name)-16s %(levelname)-8s %(message)s")

    fh = logging.FileHandler(logfile, mode='a')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logging.getLogger().addHandler(fh)

    logging.debug(f"Finished setting up debug file logging in {logfile}")
    console = logging.StreamHandler()
    if debug:
        console.setLevel(logging.DEBUG)
    else:
        console.setLevel(logging.INFO)
    logging.getLogger().addHandler(console)
    logging.debug("Logging set up successfully")


if __name__ == "__main__":

    #Parse arguments
    parser = argparse.ArgumentParser(
                     description="Script for setting up a HAFS verification workflow"\
                     "according to the parameters specified in the config file\n")

    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Script will be run with more verbose output')
    parser.add_argument('-d', '--default_config', type=str, default='config_defaults.yaml',
                        help='File name for default configuration file')
    parser.add_argument('-u', '--user_config', type=str, default='config_vx.yaml',
                        help='File name for user configuration file')
    parser.add_argument('-m', '--machine_config', type=str, default='',
                        help='File name for machine configuration file')
    parser.add_argument('-c', '--crontab_launch', action='store_true',
                        help= 'Add verification workflow to crontab for automatic task submission')
    parser.add_argument('--mins', type=int, default=5,
                        help='If adding workflow to crontab, the interval in minutes between calls')

    pargs = parser.parse_args()

    # Set "Home" directory, the top-level HAFS directory
    homedir = os.path.abspath(os.path.dirname(__file__) + os.sep + os.pardir)

    # Setup logging
    logfile = f"{homedir}/ush/log.generate_vx_wflow"
    setup_logging(logfile, pargs.verbose)


    # Read default config, user config, and machine file to populate the vx workflow directory
    config = load_config_populate_dict(homedir, pargs.default_config, pargs.user_config, pargs.machine_config)

    # Check for invalid config settings
#    config = validate_config(config)

    # Generate experiment files
    generate_vx_workflow(config)

    # If requested (via config settings), add vx workflow to crontab.
    add_workflow_to_cron(pargs.mins,config,pargs.verbose)
