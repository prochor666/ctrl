import os, json
from core import compat, config, utils, colors

compat.check_version()


def packages_source():
    with open('json/packages.json') as packages:
        return json.load(packages)
    return {}


def shell_output(stream):
    return stream.read()


def packages_install():
    packages = packages_source()

    for package_name, package_config in packages.items():
        package_path = 'vendor/' + str(package_name)
        deploy_commamd = str(package_config['command'])

        if deploy_commamd.startswith('git clone'):
            deploy_commamd = deploy_commamd + ' ' + str(package_path)

        print(colors.blue('INFO') + ': deploy package ' + package_name + ' [' + deploy_commamd + ']')

        if not os.path.isdir(str(package_path)):

            stream = os.popen(deploy_commamd)
            print(shell_output(stream))

            print(colors.green('DONE'))

            # Run  post commands in package dir
            if deploy_commamd.startswith('git clone'):
                os.chdir(str(package_path))

            if 'post_command' in package_config.keys():
                for post_command in package_config['post_command']:
                    print(colors.blue('INFO') +  ': post command ' + str(post_command))

                    stream = os.popen(post_command)
                    print(shell_output(stream))
                    print(colors.green('Done'))
            # Return to root dir
            if deploy_commamd.startswith('git clone'):
                os.chdir('../../')

        else:
            print(colors.blue('INFO') + ': package ' + package_name + ' is already installed from gihub repository.')


def directories_install():
    for directory, path in config['filesystem'].items():
        dir_abs_path = os.path.join(utils.app_root(), path)

        if not os.path.isdir(dir_abs_path):
            try:
                os.makedirs(dir_abs_path)
                print(colors.green('DONE') + ': directory ' + path +' created')
            except OSError as error:
                print(colors.red('ERROR') + ': ' + path  + str(error))
        else:
            print(colors.blue('INFO') + ': directory ' + path + ' already exists')


def run():
    print("\n")
    print(colors.blue(config['full_name'] + ' v'+ config['version'] +' installer'))

    print("\n")
    print(colors.magenta('SECTION') + ': packages')
    packages_install()

    print("\n")
    print(colors.magenta('SECTION') + ': directories')
    directories_install()


# Here we come
run()
