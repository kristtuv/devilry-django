from os import listdir, getcwd
from os.path import dirname, abspath, join, exists
from subprocess import call
from sys import argv
from os import environ

def getdir(filepath):
    """ Get the directory component of the given *filepath*. """
    return abspath(dirname(filepath))

def getthisdir():
    """ Get the directory containing this module (and all commands). """
    return getdir(__file__)

def getprogname():
    """ Get the current progname (I.E.: devilryadmin.py dosomethingcool) """
    return 'devilryadmin.py {0}'.format(environ['DEVILRYADMIN_COMMANDNAME'])

def getreporoot():
    """ Get the absolute path to the devilry repository root. """
    return abspath(dirname(dirname(getthisdir())))

def getscriptsdir():
    """ Get the ``scripts/`` directory. """
    thisdir = getthisdir()
    return join(dirname(thisdir), 'scripts')

def getcommands():
    """ Get a list of the filename of all available commmands.

    Available commands are all .py files in this dir (see :func:`getthisdir`)
    with filenames prefixed with ``cmd_``.
    """
    return [filename for filename in listdir(getdir(__file__)) \
            if filename.startswith('cmd_') and filename.endswith('.py')]

def getcommandnames():
    """ Get the name of all available commands.

    Retreived commands using :func:`getcommandnames`, and removes the
    command prefix (``cmd_``) and suffix (``.py``) before returning
    the list.
    """
    return [filename[4:-3] for filename in getcommands()]

def checkcommands(allcommands, *cmdnames):
    """ Check that each command in ``cmdnames`` is in ``allcommands``.

    :raise SystemExit: If any of the cmdnames is not in ``allcommands``.
    """
    for cmd in cmdnames:
        if not cmd in allcommands:
            raise SystemExit('{0} is not a valid command name.'.format(cmd))

def cmdname_to_filename(commandname):
    """ Return the ``commandname`` prefixed with ``cmd_`` and suffixed with ``.py``. """
    return 'cmd_{0}.py'.format(commandname)

def gethelp(commandname):
    """
    The second line of each command file should contain command help. as a # comment.

    This function returns the everything in the second line of the given command
    except for the first character. Additionally, the resulting string is strip()ed.
    """
    filename = cmdname_to_filename(commandname)
    filepath = join(getthisdir(), filename)
    f = open(filepath)
    f.readline()
    hlp = f.readline()[1:].strip()
    f.close()
    return hlp

def execcommand(commandname):
    """ Execute the given command. """
    commandpath = join(getthisdir(), cmdname_to_filename(commandname))
    command = [commandpath] + list(argv[2:])
    environ['DEVILRYADMIN_COMMANDNAME'] = commandname
    call(command)

def depends(*cmdnames):
    """ Execute the given commands in the given order. """
    allcommands = getcommandnames()
    checkcommands(allcommands, *cmdnames)
    for cmd in cmdnames:
        execcommand(cmd)

def require_djangoproject():
    """ Make sure the current working directory is a django project. """
    if not exists(join(getcwd(), 'manage.py')):
        raise SystemExit('This command requires CWD to be a django project (a directory containing manage.py).')
