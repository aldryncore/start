#!/usr/bin/env python
import os
import shlex
import subprocess
import sys
import yaml


def expandvars(string, env=None):
    """
    os.path.expandvars() does not handle defaults ( ${MYVAR:-default} ) and also
    does not return an empty string for the case where the variable is not set.
    So we are using the default shell and echo itself to escape those pesky
    vars.
    I suggest that next to "naming things" and "cache invalidation", we add
    "escaping" to the list of hardest problems.
    """
    env = env if env is not None else os.environ
    # prepare string for being used inside double quotes
    string = (
        string
        .replace('\\', '\\\\')  # replace \ with \\
        .replace('"', '\\"')    # replace " with \"
    )
    return subprocess.check_output(
        ['sh', '-c', '''printf '%s' "{}"'''.format(string)], env=env)


def parse_command(command, env=None):
    """
    takes a string or a list of args and returns a list of args where any
    shell style environment variables have been expanded.
    """
    env = env if env is not None else os.environ
    if isinstance(command, basestring):
        command = shlex.split(command)
    newcmd = []
    for arg in command:
        newarg = expandvars(arg, env=env)
        newcmd.append(newarg)
    return newcmd


def cli():
    command_name = sys.argv[1]
    extra_args = sys.argv[2:]

    cwd_path = os.path.join(os.getcwd(), 'Procfile')
    env_path = os.environ.get('PROCFILE_PATH')

    if os.path.exists(cwd_path):
        procfile_path = cwd_path
    elif env_path and os.path.exists(env_path):
        procfile_path = env_path
    else:
        sys.exit('no Procfile path defined')

    with open(procfile_path) as fh:
        command = yaml.load(fh)[command_name]

    command = parse_command(command, env=os.environ)
    os.execvpe(command[0], command + extra_args, os.environ)


if __name__ == "__main__":
    cli()
