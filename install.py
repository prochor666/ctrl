import os, json
from core import compat
from core.ctrl import colors, utils

compat.check_version()


def packages_source():
    with open('json/packages.json') as packages:
        return json.load(packages)
    return {}


def app_config():
    with open('json/app.json') as config:
        return json.load(config)
    return {}



def shell_output(stream):
    return stream.read()



def packages_install():
    packages =packages_source()

    for package, conf in packages.items():
        packagePath = 'vendor/' + str(package)
        deploy_commamd = str(conf['cmd'])

        if deploy_commamd.startswith('git clone'):
            deploy_commamd = deploy_commamd + ' ' + str(packagePath)

        print(colors.blue('::deploy command: ' + deploy_commamd))

        if not os.path.isdir(str(packagePath)):

            stream = os.popen(deploy_commamd)
            print(shell_output(stream))

            print(colors.green('Done'))

            # Run  post commands in package dir
            if deploy_commamd.startswith('git clone'):
                os.chdir(str(packagePath))

            if 'postCmd' in conf.keys():
                for postCommand in conf['postCmd']:
                    print(colors.blue('   -post command: ' + str(postCommand)))

                    stream = os.popen(postCommand)
                    print(shell_output(stream))
                    print(colors.green('Done'))
            # Return to root dir
            if deploy_commamd.startswith('git clone'):
                os.chdir('../../')

        else:
            print(colors.yellow('    !WARNING: package ' + package + ' is already installed.'))

def directories_install():
    config = app_config()

    for directory, path in config['filesystem'].items():
        if not os.path.isdir(os.path.join(utils.app_root(), path)):
            print('Make directory: ' + os.path.join(utils.app_root(), path) )
        else:
            print('Directory exists: ' + os.path.join(utils.app_root(), path) )

def database_install():
    return True


def run():

    #packages_install()
    directories_install()
    #database_install(database)



# Here we come
run()