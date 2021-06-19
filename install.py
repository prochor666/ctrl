import os
import json
from shutil import copyfile
from core import compat, config as conf, colors

compat.check_version()
config = conf.configure()


def packages_source():
    with open('json/packages.json') as packages:
        return json.load(packages)
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

        print(f"{colors.yellow('PACKAGE')}: {package_name} [{deploy_commamd}]")

        if not os.path.isdir(str(package_path)):

            stream = os.popen(deploy_commamd)
            print(shell_output(stream))
            print(colors.green('DONE'))
            print("\n")

            # Run  post commands in package dir
            if deploy_commamd.startswith('git clone'):
                os.chdir(str(package_path))

            if 'post_command' in package_config.keys():
                for post_command in package_config['post_command']:
                    print(f"{colors.blue('INFO')}: post command {str(post_command)}")

                    stream = os.popen(post_command)
                    print(shell_output(stream))
                    print(colors.green("Done"))

            # Return to root dir
            if deploy_commamd.startswith('git clone'):
                os.chdir('../../')

        else:
            print(f"{colors.blue('INFO')}: package {package_name} is already installed from gihub repository")


def directories_install():
    for directory, path in config['filesystem'].items():
        dir_abs_path = os.path.join(os.path.abspath(__file__), path)

        if not os.path.isdir(dir_abs_path):
            try:
                os.makedirs(dir_abs_path)
                print(f"{colors.green('DONE')}: directory {path} created")
            except OSError as error:
                print(f"{colors.red('ERROR')}: {path} {str(error)}")
        else:
            print(f"{colors.blue('INFO')}: directory {path} already exists")


def run():
    print("\n")
    print(f"{colors.blue(config['full_name'])} v{config['version']} installer")

    print("\n")
    print(f"{colors.magenta('SECTION')}: packages")
    packages_install()

    print("\n")
    print(f"{colors.magenta('SECTION')} directories")
    directories_install()

    print("\n")
    print(f"{colors.magenta('SECTION')} config")
    sample_config = os.path.join(os.path.abspath(__file__), 'json/sample.app.json')
    production_config = os.path.join(os.path.abspath(__file__), 'json/app.json')
    if not os.path.isfile(production_config):
        copyfile(sample_config, production_config)


# Here we come
run()
