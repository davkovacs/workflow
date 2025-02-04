import click
from wfl.configset import ConfigSet, OutputSpec
from ase.io.extxyz import key_val_str_to_dict


def _to_ConfigSet(ctx, param, value):
    return ConfigSet(value)

def inputs(f):
    """Add a standard option for the ConfigSet inputs"""
    f = click.option("--inputs", "-i", required=True, multiple=True, callback=_to_ConfigSet,
                    help='Input xyz file(s) to create ConfigSet from')(f) 
    return f


def _to_OutputSpec(ctx, param, value):
    return OutputSpec(value)


def outputs(f):
    """Add a standard option for the OutputSpec outputs"""
    f = click.option('--outputs', '-o', required=True, callback=_to_OutputSpec,
                     help="Ouput file to create OutputSpec from.")(f)
    return f

def _parse_extra_info(ctx, param, value):
    if value is not None:
        return key_val_str_to_dict(value)
    else:
        return {}

def extra_info(f):
    """Parse key=val string and return a dictionary"""
    f = click.option("--extra-info", "-i", callback=_parse_extra_info, help="Extra key=val pairs to add to Atoms.info")(f)
    return f

def param_fname(f):
    f = click.option("--param-fname", type=click.Path(), help="Path to the potential parameter file")(f)
    return f

def prop_prefix(f):
    f = click.option("--prop-prefix", "-p", help='Prefix to be pre-pended to all evaluate properties. Defaults to "gap_"/"ace_"/"mace_" as appropriate')(f)
    return f


def num_inputs_per_python_subprocess(f):
    f = click.option('--num-inputs-per-python-subprocess', default=10, 
    show_default=True, type=click.INT, 
    help="Number of configs to be evaluated per each calculator initialization")(f)
    return f


