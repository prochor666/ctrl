import asyncio
import asyncssh
import json
import re
from slugify import slugify
from core import app, utils, data
from core.ctrl import servers, recipes, sites, mailer, services, notifications


async def run_client(server, tasks=[], recipe=None, service_installer=False):

    result = {
        'status': False,
        'message': f"Server {server['name']}: ",
        'shell': []
    }

    if 'ssh_key' in server.keys() and len(server['ssh_key']) > 0:
        result['auth_method'] = 'Private key'

        try:
            async with asyncssh.connect(server['ipv4'], port=int(server['ssh_port']), username=server['ssh_user'], client_keys=[server['ssh_key']], known_hosts=None) as conn:

                result = await run_task(conn, tasks, recipe, service_installer, result)

        except(asyncssh.Error) as exc:
            result['message'] = f"Server {server['name']}: {str(exc)}"
    else:
        result['auth_method'] = 'Password'

        try:
            async with asyncssh.connect(server['ipv4'], port=int(server['ssh_port']), username=server['ssh_user'], password=server['ssh_pwd'], known_hosts=None) as conn:
                #print(recipe)

                result = await run_task(conn, tasks, recipe, service_installer, result)

        except(asyncssh.Error) as exc:
            result['message'] = f"Server {server['name']}: {str(exc)}"

    return result


async def run_task(conn, tasks, recipe, service_installer, result):

    if type(recipe) is dict:
        result = await process_recipe_file(conn, recipe, result)

    if service_installer == True:
        result = await process_service_files(conn, result)

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
    response = await conn.run(as_root('mkdir -p /opt/ctrl/scripts'), check=False)
    result['shell'].append(response.stdout)
    response = await conn.run(as_root('chown $(ls - ld ~ | awk \'{print $3}\') /opt/ctrl/scripts'), check=False)
    result['shell'].append(response.stdout)

    # Cache recipe file localy
    utils.file_save(f"{cache_dir}/{cache_file}",
                    utils.dos2unix(recipe['content']))

    # Transfer recipe file
    # Returns None type, so we can't log
    await asyncssh.scp(f"{cache_dir}/{cache_file}", (conn, f"/opt/ctrl/scripts/{cache_file}"))

    # Make recipe file executable
    response = await conn.run(as_root(f"chmod +x /opt/ctrl/scripts/{cache_file}"), check=False)
    result['shell'].append(response.stdout)

    # Run script in remote dir
    recipe['arguments'] = domain_unique(recipe['arguments'])
    response = await conn.run(as_root(f"/opt/ctrl/scripts/{cache_file} {compose_script_call_args(recipe['arguments'])}"), check=False)
    result['shell'].append(response.stdout)

    return result


def deploy(site_id):
    site = sites.load_site({
        'id': site_id
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

    # Notify and parse shell response
    parsed = parse_shell_result("\n".join(result['shell']))
    notifications.email('settings.notifications.sites',
                        parsed['template'], f"{app.config['name']} - site deployed", parsed['html_message_data'], parsed['result'])
    notifications.db(
        'site', site_id, f"Site {site['name']} deployed.", parsed['nice'])

    result['shell'] = [parsed['nice']]

    return result


def parse_shell_result(result):
    tag_result = result

    custom_tag = utils.tag_parse('control-result', result)

    if len(custom_tag) > 0:
        tag_result = custom_tag

    html_message_data = {
        'app_full_name': app.config['full_name'],
    }
    try:
        json_object = json.loads(tag_result)
        html_message_data['data'] = json.dumps(json_object, indent=4)
        template = 'deploy-json'

    except ValueError as e:
        html_message_data['data'] = tag_result
        template = 'deploy-text'

    return {
        'result': result,
        'nice': html_message_data['data'],
        'template': template,
        'html_message_data': html_message_data
    }


def test_connection(server_id):
    server = servers.load_server({
        'id': server_id
    })

    if type(server) is not dict or 'ipv4' not in server:
        return {
            'status': False,
            'message': f"Server {server_id} not found",
            'shell': []
        }

    tasks = [
        'echo "SSH server hostname: $(hostname)"',
        'echo "$(uname -a)"',
        'echo "$(cat /etc/os-release)"',
        as_root('mkdir -p /opt/ctrl/scripts'),
        'echo "Monitoring service is $(systemctl is-active ctrl-monitor-collector.service)"',
    ]

    return init_client(server, tasks)


async def process_service_files(conn, result):
    cache_dir = app.config['filesystem']['recipes']
    config_cache_file = "ctrl-monitor-install.sh"
    script_cache_file = "ctrl-monitor.sh"

    # Check remote dir for scripts
    response = await conn.run(as_root('mkdir -p /opt/ctrl/scripts'), check=False)
    result['shell'].append(response.stdout)
    response = await conn.run(as_root('mkdir -p /opt/ctrl/monitor'), check=False)
    result['shell'].append(response.stdout)

    response = await conn.run(as_root('chown $(ls -ld ~ | awk \'{print $3}\') /opt/ctrl/scripts'), check=False)
    result['shell'].append(response.stdout)
    response = await conn.run(as_root('chown $(ls -ld ~ | awk \'{print $3}\') /opt/ctrl/monitor'), check=False)
    result['shell'].append(response.stdout)

    # Cache files localy
    utils.file_save(f"{cache_dir}/{config_cache_file}",
                    utils.dos2unix(services.monitor_service_config()))
    utils.file_save(f"{cache_dir}/{script_cache_file}",
                    utils.dos2unix(services.monitor_service_script()))

    # Transfer script filess
    # Returns None type, so we can't log
    await asyncssh.scp(f"{cache_dir}/{config_cache_file}", (conn, f"/opt/ctrl/scripts/{config_cache_file}"))
    await asyncssh.scp(f"{cache_dir}/{script_cache_file}", (conn, f"/opt/ctrl/monitor/{script_cache_file}"))

    response = await conn.run(as_root(f"dos2unix /opt/ctrl/scripts/{config_cache_file}"), check=False)
    result['shell'].append(response.stdout)
    response = await conn.run(as_root(f"dos2unix /opt/ctrl/monitor/{script_cache_file}"), check = False)
    result['shell'].append(response.stdout)

    # Make recipe file executable
    response = await conn.run(as_root(f"chmod +x /opt/ctrl/scripts/{config_cache_file}"), check=False)
    result['shell'].append(response.stdout)
    response = await conn.run(as_root(f"chmod +x /opt/ctrl/monitor/{script_cache_file}"), check = False)
    result['shell'].append(response.stdout)

    # Run install script in remote dir
    response = await conn.run(as_root(f"/opt/ctrl/scripts/{config_cache_file}"), check=False)
    result['shell'].append(response.stdout)

    return result


def domain_unique(recipe_arguments):
    new_aliases = []
    if len(recipe_arguments['dev_domain']) > 0 and recipe_arguments['domain'] == recipe_arguments['dev_domain']:
       recipe_arguments['dev_domain'] = ''

    if type(recipe_arguments['alias_domains']) is list and len(recipe_arguments['alias_domains']) > 0:

        for alias_domain in recipe_arguments['alias_domains']:
            if alias_domain != recipe_arguments['domain'] and alias_domain != recipe_arguments['dev_domain'] and alias_domain not in new_aliases:

                new_aliases.append(alias_domain)

    recipe_arguments['alias_domains'] = new_aliases
    return recipe_arguments


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


def install_monitoring_service(server_id):
    server = servers.load_server({
        'id': server_id
    })

    tasks = [
        'echo "SSH server hostname: $(hostname)"',
        'echo "Monitoring service is $(systemctl is-active ctrl-monitor-collector.service)"'
    ]

    return init_client(server=server, tasks=tasks, recipe=None, service_installer=True)


def validate_dns_entry(domain, server_ipv4):
    if not sites.is_domain_on_server(domain, server_ipv4):
        return False
    return True


def detect_root(server_id):
    server = servers.load_server({
        'id': server_id
    })

    if type(server) is not dict or 'ipv4' not in server:
        return {
            'status': False,
            'message': f"Server {server_id} not found",
            'shell': []
        }

    tasks = [
        f"if [[ $EUID == 0 ]];then AR=\"root\"; elif [[ $(which sudo) ]] && [[ $EUID != 0 ]];then AR=\"sudo\"; else AR=\"none\"; fi; echo -n $AR",
    ]

    return init_client(server, tasks)


def as_root(command):
    pattern = f"if [[ $EUID == 0 ]];then {command}; elif [[ $(which sudo) ]] && [[ $EUID != 0 ]];then sudo {command}; else echo \"No root condition, can't run on this machine\"; fi;"
    return pattern


def init_client(server, tasks, recipe=None, service_installer=False):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    r = asyncio.get_event_loop().run_until_complete(
        run_client(server, tasks, recipe, service_installer))
    return r
