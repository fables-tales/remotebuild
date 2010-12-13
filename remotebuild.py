import ConfigParser, os
import sys
import subprocess

def read_config(config_file):

    config = ConfigParser.ConfigParser()
    assert os.path.exists(config_file)
    config.readfp(open(config_file))
    return config.items("remotebuild")

if __name__ == "__main__":
    things = read_config(".remotebuildrc")

    remote_host = None
    compile_command = None
    copy_to = None

    for k,v in things:
        if k == "remote_path":
            copy_to = v
        elif k == "compile_command":
            compile_command = v
        elif k == "ssh_login":
            remote_host = v

    if compile_command is None:
        sys.stderr.write("no compile command configured\n")
        sys.exit(2)
    if copy_to is None:
        sys.stderr.write("no remote directory configured\n")
        sys.exit(4)
    if remote_host is None:
        sys.stderr.write("no remote host configured\n")
        sys.exit(8)

    #do an rsync
    subprocess.check_call(["rsync", "-r", "-t", "./", remote_host + ":" + copy_to])

    #execute the compile command in the remote directory
    subprocess.check_call(["ssh", remote_host, "cd %s && %s" % (copy_to, compile_command)])

    #rsync back
    subprocess.check_call(["rsync", "-r", "-t", remote_host + ":" + copy_to + "/*", "./"])
