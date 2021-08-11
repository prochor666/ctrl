import asyncio
import asyncssh
import sys
import json
from flask import render_template
from slugify import slugify
from core import app, utils, data
from core.ctrl import servers, recipes, sites, mailer


async def run_client(server, tasks=[], recipe=None):

    result = {
        'status': False,
        'message': f"Server {server['name']}: ",
        'shell': []
    }

    if 'ssh_key' in server.keys() and len(server['ssh_key']) > 0:
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
                #print(recipe)

                result = await run_task(conn, tasks, recipe, result)

        except(asyncssh.Error) as exc:
            result['message'] = f"Server {server['name']}: {str(exc)}"

    return result


async def run_task(conn, tasks, recipe, result):

    if type(recipe) is dict:
        result = await process_recipe_file(conn, recipe, result)

    for task in tasks:
        response = await conn.run(task, check=False)
        result['shell'].append(response.stdout)

    conn.close()
    result['message'] += f"Task completed"
    result['status'] = True

    return result


async def process_recipe_file(conn, recipe, result):
    cache_dir = app.config['filesystem']['recipes']
    cache_file = slugify(f"{utils.now()}-{recipe['name']}") + ".sh"

    # Check remote dir for scripts
    response = await conn.run('xnope="$(mkdir -p /opt/ctrl/scripts 2>&1)"', check=False)
    result['shell'].append(response.stdout)

    # Cache recipe file localy
    utils.file_save(f"{cache_dir}/{cache_file}", recipe['content'])

    # Transfer recipe file
    # Returns None type, so we can't log
    await asyncssh.scp(f"{cache_dir}/{cache_file}", (conn, f"/opt/ctrl/scripts/{cache_file}"))

    # Make recipe file executable
    response = await conn.run(f"chmod +x /opt/ctrl/scripts/{cache_file}", check=False)
    result['shell'].append(response.stdout)

    # Run script in remote dir
    response = await conn.run(f"/opt/ctrl/scripts/{cache_file} {compose_script_call_args(recipe['arguments'])}", check=False)
    result['shell'].append(response.stdout)

    return result


def deploy(id):
    site = sites.load_site({
        'id': id
    })

    # Site validation
    if type(site) is not dict:
        return {
            'status': False,
            'message': f"Invalid site",
            'shell': []
        }

    server = servers.load_server({
        'id': site['server_id']
    })

    recipe = recipes.load_recipe({
        'id': site['recipe_id']
    })

    # Recipe validation
    if type(recipe) is not dict or 'content' not in recipe or recipe['safe'] == False:
        return {
            'status': False,
            'message': f"Invalid or unsafe recipe",
            'shell': []
        }

    # Domain name validation
    if type(server) is not dict or 'ipv4' not in server:
        return {
            'status': False,
            'message': f"Domain {site['domain']} is not redirected on selected server",
            'shell': []
        }

    tasks = []

    recipe['arguments'] = {
        'home_dir': site['home_dir'],
        'domain': '',
        'dev_domain': '',
        'alias_domains': []
    }

    valid_domains = []

    # Validate domain DNS entries
    if sites.is_domain_on_server(site['domain'], server['ipv4']) == True:
        valid_domains.append(site['domain'])
        recipe['arguments']['domain'] = site['domain']


    # Validate dev_domain DNS entries
    if 'dev_domain' in site.keys() and type(site['dev_domain']) is str and len(site['dev_domain']) > 3 and sites.is_domain_on_server(site['dev_domain'], server['ipv4']) == True:
        valid_domains.append(site['dev_domain'])
        recipe['arguments']['dev_domain'] = site['dev_domain']

    # Validate alias domains DNS entries
    if 'alias_domains' in site.keys() and type(site['alias_domains']) is list and len(site['alias_domains']) > 0:

        for alias_domain in site['alias_domains']:

            if sites.is_domain_on_server(alias_domain, server['ipv4']) == True:
                valid_domains.append(alias_domain)
                recipe['arguments']['alias_domains'].append(alias_domain)

    if len(valid_domains) == 0:
        return {
            'status': False,
            'message': f"None of the specified domains are redirected to the selected server",
            'shell': []
        }

    recipe['valid_domains'] = valid_domains

    result = init_client(server, tasks, recipe)
    # TO-DO: notify

    return result


def notify_deploy_result(result, site):

    valid_users = data.ex({
        'collection': 'users',
        'filter': {
            'settings': {
                'notificatios': {
                    'sites': True
                }
            }
        },
        'exclude': {'secret': 0, 'pwd': 0, 'salt': 0}
    })

    html_message_data = {
        'app_full_name': app.config['full_name'],
    }

    try:
        json_object = json.loads(result)
        html_message_data['data'] = json_object
        template = 'deploy-json'

    except ValueError as e:
        html_message_data['data'] = result
        template = 'deploy-text'

    #html_message = mailer.email_template(template).format(**html_message_data)

    for user in valid_users:

        html_message_data['user'] = user
        html_message = render_template(
            f"email/{template}.html", data=html_message_data)
        es = mailer.send(
            user['email'], f"{app.config['name']} site deployed", html_message)



def test_connection(server_id):

    server = servers.load_server({
        'id': server_id
    })

    tasks = [
        'echo "SSH server hostname: $(hostname)"',
        'echo "$(lsb_release -a)"',
        'xnope="$(mkdir -p /opt/ctrl/scripts 2>&1)" | echo $xnope',
        'echo "$(ls -lah /opt/ctrl)"',
    ]

    return init_client(server, tasks)


def compose_script_call_args(recipe_arguments):
    cmd = f""

    if len(recipe_arguments['home_dir']) > 0:
        cmd += f" --home_dir {recipe_arguments['home_dir']}"

    if len(recipe_arguments['domain']) > 0:
        cmd += f" --domain {recipe_arguments['domain']}"

    if len(recipe_arguments['dev_domain']) > 0:
        cmd += f" --dev_domain {recipe_arguments['dev_domain']}"

    if type(recipe_arguments['alias_domains']) is list and len(recipe_arguments['alias_domains']) > 0:
        cmd += f" --alias_domains {':'.join(recipe_arguments['alias_domains'])}"

    return cmd


def validate_dns_entry(domain, server_ipv4):
    if not sites.is_domain_on_server(domain, server_ipv4):
        return False
    return True


def init_client(server, tasks, recipe=None):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    r = asyncio.get_event_loop().run_until_complete(
        run_client(server, tasks, recipe))
    return r
