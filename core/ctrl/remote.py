import asyncio, asyncssh, sys

async def run_client(server, tasks = []):
    async with asyncssh.connect(server['ipv4'], username=server['ssh_user'], client_keys=[server['ssh_key']]) as conn:

        result = ""

        for task in tasks:
            response = await conn.run(task, check=False)
            result += response.stdout

        return result


def task():

    server = {
        'ipv4': '159.89.29.171',
        'ssh_user': 'root',
        'ssh_key': '~/.ssh/id_ed25519_ctrl_server'
    }

    tasks = [
        'printf \'%s✖ %s%s\n\' "$(tput setaf 1)" "Okay" "$(tput sgr0)"',
        'ls -la ~/testing-dir',
        'echo $(cat ~/testing-dir/a.txt)'
    ]

    try:
        r = asyncio.get_event_loop().run_until_complete(run_client(server, tasks))
        print(r, end='')
    except (OSError, asyncssh.Error) as exc:
        sys.exit('SSH connection failed: ' + str(exc))

task()
