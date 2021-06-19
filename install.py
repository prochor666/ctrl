import os
import json
import sys
import subprocess
from shutil import copyfile

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

check_version()

print("\n")
print("SECTION config")
sample_config = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'json/sample.app.json').replace('/', os.path.sep)
production_config = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'json/app.json').replace('/', os.path.sep)
if not os.path.isfile(production_config):
    copyfile(sample_config, production_config)
    print("Config created")
else:
    print("Config exists")


def packages_source():
    with open('json/packages.json') as packages:
        return json.load(packages)
    return {}

def config_source():
    with open('json/app.json') as conf:
        config = json.load(conf)
        for key, value in config['filesystem'].items():
            config['filesystem'][key] = value.replace('/', os.path.sep)

        return config
    return {}

def shell_output(stream):
    return stream.read()


def packages_install():
    packages = packages_source()

    for package_name, package_config in packages.items():
        package_path = f"vendor/{str(package_name)}"
        deploy_commamd = str(package_config['command'])

        if deploy_commamd.startswith('git clone'):
            deploy_commamd = f"{deploy_commamd} {str(package_path)}"

        print(f"PACKAGE: {package_name} [{deploy_commamd}]")

        if not os.path.isdir(str(package_path)):

            stream = os.popen(deploy_commamd)
            print(shell_output(stream))
            print('DONE')
            print("\n")

            # Run  post commands in package dir
            #if deploy_commamd.startswith('git clone'):
            #    os.chdir(str(package_path))

            if 'post_command' in package_config.keys():
                for post_command in package_config['post_command']:
                    print(f"INFO: post command {str(post_command)}")

                    stream = os.popen(post_command)
                    print(shell_output(stream))
                    print("Done")

            # Return to root dir
            #if deploy_commamd.startswith('git clone'):
            #    os.chdir('../../')

        else:
            print(f"INFO: package {package_name} is already installed from gihub repository")


def directories_install():

    config = config_source()

    for directory, path in config['filesystem'].items():
        dir_abs_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), path)

        if not os.path.isdir(dir_abs_path):
            try:
                os.makedirs(dir_abs_path)
                print(f"DONE: directory {path} created")
            except OSError as error:
                print(f"ERROR: {path} {str(error)}")
        else:
            print(f"INFO: directory {path} already exists")


def run():
    print("\n")
    print("SECTION: packages")
    packages_install()

    print("\n")
    print("SECTION: directories")
    directories_install()


# Here we come
run()
