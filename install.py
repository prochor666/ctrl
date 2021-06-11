import os, json
from core import compat
from core.ctrl import config, colors, utils

compat.check_version()


def packages_source():
    with open('json/packages.json') as packages:
        return json.load(packages)
    return {}


def shell_output(stream):
    return stream.read()



def packages_install():
    packages =packages_source()

    for package, conf in packages.items():
        package_path = 'vendor/' + str(package)
        deploy_commamd = str(conf['cmd'])

        if deploy_commamd.startswith('git clone'):
            deploy_commamd = deploy_commamd + ' ' + str(package_path)

        print(colors.blue('::deploy command: ' + deploy_commamd))

        if not os.path.isdir(str(package_path)):

            stream = os.popen(deploy_commamd)
            print(shell_output(stream))

            print(colors.green('Done'))

            # Run  post commands in package dir
            if deploy_commamd.startswith('git clone'):
                os.chdir(str(package_path))

            if 'postCmd' in conf.keys():
                for post_command in conf['postCmd']:
                    print(colors.blue('   -post command: ' + str(post_command)))

                    stream = os.popen(post_command)
                    print(shell_output(stream))
                    print(colors.green('Done'))
            # Return to root dir
            if deploy_commamd.startswith('git clone'):
                os.chdir('../../')

        else:
            print(colors.yellow('    !WARNING: package ' + package + ' is already installed.'))

def directories_install():
    conf = config.configure()

    for directory, path in conf['filesystem'].items():

        dir_abs_path = os.path.join(utils.app_root(), path)

        if not os.path.isdir(dir_abs_path):
            try:
                os.mkdir(dir_abs_path)
                print(colors.green('Directory created') + ': ' + dir_abs_path)
            except OSError as error:
                print(error)
                print(colors.red('Directory error') + ': ' + error)
        else:
            print(colors.blue('Directory already exists') + ': ' + dir_abs_path)


def database_install():
    conf = config.configure()

    return True


def run():
    #packages_install()
    directories_install()
    #database_install()



# Here we come
run()