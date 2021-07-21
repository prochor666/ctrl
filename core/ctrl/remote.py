import asyncio, asyncssh, sys
from core.ctrl import servers

async def run_client(server, tasks = []):

    result = {
        'status': False,
        'message': 'Try client run',
        'shell': []
    }

    if 'ssh_key' in server.keys() and len(server['ssh_key'])>0:

        try:
            async with asyncssh.connect(server['ipv4'], port=int(server['ssh_port']), username=server['ssh_user'], client_keys=[server['ssh_key']], known_hosts=None) as conn:

                result = await run_task(conn, tasks, result)

        except(asyncssh.Error) as exc:
            result['message'] = exc
    else:

        try:
            async with asyncssh.connect(server['ipv4'], port=int(server['ssh_port']), username=server['ssh_user'], password=server['ssh_pwd'], known_hosts=None) as conn:

                result = await run_task(conn, tasks, result)

        except(asyncssh.Error) as exc:
            result['message'] = exc

    return result


async def run_task(conn, tasks, result):

    for task in tasks:
        response = await conn.run(task, check=False)
        result['shell'].append(response.stdout)

    conn.close()
    result['message'] = 'Task completed'
    result['status'] = True

    return result



def test_connection(server_id):

    server = servers.load_server({
        'id': server_id
    })

    tasks = [
        'printf "SSH server hostname: $(hostname)"',
        'printf "$(lsb_release -a)"',
    ]

    return task_init(server, tasks)


def task_init(server, tasks):

    r = asyncio.get_event_loop().run_until_complete(run_client(server, tasks))
    return r

