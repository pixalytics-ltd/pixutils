import subprocess


def exec_gdl(gdl_commands: [str], working_dir: str = None) -> (int, str, str):
    """
    Creates a GDL interpreter process and then streams commands into the process before exiting.
    :param gdl_commands: a list of GDL statements to send into the GDL interpreter
    :param working_dir: the directory where files called in GDL statements exist
    :return: a tuple containing the exit code, stdout, and stderr from the GDL process
    """

    #   create a subprocess for gdl and pipe the specified commands to the subprocess.
    p = subprocess.run(['gdl'],
                       cwd=working_dir,
                       env={
                           "SHELL": "/bin/bash",
                           #"PATH": os.environ["PATH"] + os.pathsep + path,
                           #"DIR": path,
                       },
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE,
                       input="\n".join(gdl_commands) + "\n",
                       encoding='ascii')

    #   capture the return code and stdout and stderr outputs
    return p.returncode, p.stdout, p.stderr
