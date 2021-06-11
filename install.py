import os, json
from core.ctrl import colors

def packagesSrc():
    with open('json/install.json') as install:
        return json.load(install)

    return {}


def cmdOutput(stream):
    return stream.read()


def run():

    packages = packagesSrc()

    for package, conf in packages.items():
        packagePath = 'vendor/' + str(package)
        deployCommand = str(conf['cmd'])

        if deployCommand.startswith('git clone'):
            deployCommand = deployCommand + ' ' + str(packagePath)

        print(colors.blue('::deploy command: ' + deployCommand))

        if not os.path.isdir(str(packagePath)):

            stream = os.popen(deployCommand)
            print(cmdOutput(stream))

            print(colors.green('Done'))

            # Run  post commands in package dir
            if deployCommand.startswith('git clone'):
                os.chdir(str(packagePath))

            if 'postCmd' in conf.keys():
                for postCommand in conf['postCmd']:
                    print(colors.blue('   -post command: ' + str(postCommand)))

                    stream = os.popen(postCommand)
                    print(cmdOutput(stream))
                    print(colors.green('Done'))
            # Return to root dir
            if deployCommand.startswith('git clone'):
                os.chdir('../../')

        else:
            print(colors.yellow('    !WARNING: package ' + package + ' is already installed.'))

# Here we come
run()