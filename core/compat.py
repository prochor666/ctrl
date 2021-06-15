import sys


def check_version():
    rv = (3, 7)
    current_version = sys.version_info
    if current_version[0] == rv[0] and current_version[1] >= rv[1]:
        pass
    else:
        sys.stderr.write("[%s] - Error: Your Python interpreter must be %d.%d or greater (within major version %d)\n" %
                         (sys.argv[0], rv[0], rv[1], rv[0]))
        sys.exit(-1)
    return 0
