from core import utils
from core.ctrl import servers, remote, stat


def survey(id):

    result = {
        'status': False,
        'message': f"Server not found",
        'data': {}
    }

    monitor = compose_monitor_tasks(id)

    if type(monitor) is not dict:
        return result

    raw_result = ''.join(
        remote.init_client(monitor['server'], monitor['tasks'])['shell'])

    #print(raw_result)

    parts = parse_monitor_result(raw_result)

    result['data']['cpu'] = stat.cpu(parts['cpu'])
    result['data']['load'] = stat.cpu_load(parts['stats1'], parts['stats2'])
    result['data']['memory'] = stat.memory(parts['memory'])
    result['data']['storage'] = stat.storage(parts['storage'])
    result['data']['network'] = stat.network(parts['network1'], parts['network2'], parts['network_stats'])
    result['data']['last_update'] = parts['last_update'].strip()
    result['status'] = True
    result['message'] = f"Server {monitor['server']['name']} stat data"

    return result


def compose_monitor_tasks(id):

    server = servers.load_server({
        'id': id
    })

    # Server validation
    if type(server) is not dict:
        return False

    tasks = [
        'cat /opt/ctrl/stats/ctrl-monitor.data',
    ]

    return {
        'server': server,
        'tasks': tasks
    }


def parse_monitor_result(raw):

    cpu = utils.tag_parse('control-monitor-cpu', raw)
    memory = utils.tag_parse('control-monitor-memory', raw)
    network1 = utils.tag_parse('control-monitor-network1', raw)
    network2 = utils.tag_parse('control-monitor-network2', raw)
    network_stats = utils.tag_parse('control-monitor-network-stats', raw)
    storage = utils.tag_parse('control-monitor-storage', raw)
    stats1 = utils.tag_parse('control-monitor-stat-sample1', raw)
    stats2 = utils.tag_parse('control-monitor-stat-sample2', raw)
    last_update = utils.tag_parse('control-monitor-last-update', raw)
    return {
        'cpu': cpu,
        'memory': memory,
        'network1': network1,
        'network2': network2,
        'network_stats': network_stats,
        'storage': storage,
        'stats1': stats1,
        'stats2': stats2,
        'last_update': last_update
    }
