import asyncio, asyncssh, sys
from slugify import slugify
from core import utils
from core.ctrl import servers, recipes, sites


async def run_client(server, tasks = [], recipe = None):

    result = {
        'status': False,
        'message': f"Server {server['name']}: ",
        'shell': []
    }

    if 'ssh_key' in server.keys() and len(server['ssh_key'])>0:
        result['auth_method'] = 'Private key'

        try:
            async with asyncssh.connect(server['ipv4'], port=int(server['ssh_port']), username=server['ssh_user'], client_keys=[server['ssh_key']], known_hosts=None) as conn:

                result = await run_task(conn, tasks, recipe, result)

        except(asyncssh.Error) as exc:
            result['message'] = f"Server {server['name']}: {str(exc)}"
    else:
        result['auth_method'] = 'Password'

        try:
            async with asyncssh.connect(server['ipv4'], port=int(server['ssh_port']), username=server['ssh_user'], password=server['ssh_pwd'], known_hosts=None) as conn:

                result = await run_task(conn, tasks, recipe, result)

        except(asyncssh.Error) as exc:
            result['message'] = f"Server {server['name']}: {str(exc)}"

    return result


async def run_task(conn, tasks, recipe, result):

    if type(recipe) is dict:
        await transfer_file(recipe, conn)

    for task in tasks:
        response = await conn.run(task, check=False)
        result['shell'].append(response.stdout)

    conn.close()
    result['message'] += f"task completed"
    result['status'] = True

    return result


async def transfer_file(recipe, conn):
    cache_file = slugify(f"{utils.now()}-{recipe.name}.sh")
    utils.file_save(f"recipes/{cache_file}", recipe.content)
    r = await conn.run('mkdir -p /opt/ctrl/scripts', check=False)
    r = await conn.scp(f"recipes/{cache_file}", f"/opt/ctrl/scripts/{cache_file}")

    return r


def deploy(id):
    site = sites.load_site({
        'id': id
    })

    server = servers.load_server({
        'id': site['server_id']
    })

    recipe = recipes.load_recipe({
        'id': site['recipe_id']
    })

    # Site validation
    if type(site) is not dict:
        return {
                'status': False,
                'message': f"Invalid site",
                'shell': []
            }

    # Recipe validation
    if type(recipe) is not dict or 'content' not in recipe or recipe['safe'] == False:
        return {
                'status': False,
                'message': f"Invalid or unsafe recipe",
                'shell': []
            }

    # domain name validation
    if type(server) is not dict or 'ipv4' not in server or sites.is_domain_on_server(site['domain'], server['ipv4']) == False:
        return {
                'status': False,
                'message': f"Domain {site['domain']} is not redirected on selected server",
                'shell': []
            }

    tasks = [
        'ls -lah /opt/ctrl',
    ]

    return init_client(server, tasks, recipe)


def test_connection(server_id):

    server = servers.load_server({
        'id': server_id
    })

    tasks = [
        'printf "SSH server hostname: $(hostname)"',
        'printf "$(lsb_release -a)"',
        'mkdir -p /opt/ctrl/scripts',
        'ls -lah /opt/ctrl',
    ]

    return init_client(server, tasks)


def init_client(server, tasks, recipe = None):

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    r = asyncio.get_event_loop().run_until_complete(run_client(server, tasks, recipe))
    return r

