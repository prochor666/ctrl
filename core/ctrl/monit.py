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

    parts = parse_monitor_result(raw_result)

    result['data']['cpu'] = stat.cpu(parts['cpu'])
    result['data']['load'] = stat.cpu_load(parts['stats1'], parts['stats2'])
    result['data']['memory'] = stat.memory(parts['memory'])
    result['data']['storage'] = stat.storage(parts['storage'])
    result['data']['network'] = stat.network(parts['network'], parts['network_stats'])
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
        'echo "SSH server hostname: $(hostname)"',
        'echo "<control-monitor-cpu>"',
        'echo "$(cat /proc/cpuinfo)"',
        'echo "</control-monitor-cpu>"',
        'echo "<control-monitor-stat-sample1>"',
        'echo "$(cat /proc/stat)"',
        'echo "</control-monitor-stat-sample1>"',
        'sleep 2',
        'echo "<control-monitor-stat-sample2>"',
        'echo "$(cat /proc/stat)"',
        'echo "</control-monitor-stat-sample2>"',
        'echo "<control-monitor-memory>"',
        'echo "$(cat /proc/meminfo)"',
        'echo "</control-monitor-memory>"',
        'echo "<control-monitor-storage>"',
        'echo "$(df -P /var/www)"',
        'echo "</control-monitor-storage>"',
        'echo "<control-monitor-network>"',
        'echo "$(cat /proc/net/dev)"',
        'echo "</control-monitor-network>"',
        'echo "<control-monitor-network-stats>"',
        'echo "TO-DO: create stat service https://gist.github.com/prochor666/f5dc193a1fe01b9bef2c1e2cdbfa4e70"',
        'echo "</control-monitor-network-stats>"',
    ]

    return {
        'server': server,
        'tasks': tasks
    }


def parse_monitor_result(raw):

    print(raw)

    cpu = utils.tag_parse('control-monitor-cpu', raw)
    memory = utils.tag_parse('control-monitor-memory', raw)
    network = utils.tag_parse('control-monitor-network', raw)
    network_stats = utils.tag_parse('control-monitor-network-stats', raw)
    storage = utils.tag_parse('control-monitor-storage', raw)
    stats1 = utils.tag_parse('control-monitor-stat-sample1', raw)
    stats2 = utils.tag_parse('control-monitor-stat-sample2', raw)

    return {
        'cpu': cpu,
        'memory': memory,
        'network': network,
        'network_stats': network_stats,
        'storage': storage,
        'stats1': stats1,
        'stats2': stats2,
    }
