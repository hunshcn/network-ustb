import logging
import socket
from time import sleep

import psutil
import requests

params = dict(
    login_token="123456,your api token",
    domain="hunsh.net",  # doamin
    sub_domain="sub domain here",  # example: "a"
    format="json",
    record_type='A',
    record_line='默认',
)
params_modify = dict(
    record_id=0,
    value=""
)


def connect_test():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    ip = '202.204.48.66'
    try:
        sock.connect((ip, 80))
        sock.close()
        return True
    except Exception as e:
        sock.close()
    return False


# 获取网卡名称和其ip地址，不包括回环
def get_ip():
    info = psutil.net_if_addrs()
    for k, v in info.items():
        for item in v:
            if item[0] == 2 and item[1].startswith('10.'):
                connect_test()
                return item[1]


def get_record():
    global current_ip
    url = 'https://dnsapi.cn/Record.List'
    try:
        r = requests.post(url, data=params)
        r.raise_for_status()
    except:
        logger.warning("\033[1;31m[Error]\033[0m Please check network connectivity.")
        return
    r = r.json()
    code = r['status']['code']
    record_id = r['records'][0]['id'] if code == '1' else 0
    current_ip = r['records'][0]['value'] if code == '1' else ""
    if code == '1':
        params_modify['record_id'] = record_id
    else:
        logger.critical(f"\033[1;31m[critical]\033[0m 获取{params['sub_domain']}.{params['domain']}解析出错，code：{code}，message：{r['status']['message']}")
        exit(2)


def update_record(new_value):
    url = 'https://dnsapi.cn/Record.Modify'
    p = params.copy()
    p.update(params_modify)
    p['value'] = new_value
    try:
        r = requests.post(url, data=p)
        r.raise_for_status()
    except:
        logger.warning("\033[1;31m[Error]\033[0m Please check network connectivity.")
        return
    logger.info("[info] update ip: " + new_value)

    r = r.json()
    code = r['status']['code']
    if code != '1':
        logger.critical(f"\033[1;31m[critical]\033[0m 获取{params['sub_domain']}.{params['domain']}解析出错，code：{code}，message：{r['status']['message']}")
        exit(2)
    return True


if __name__ == '__main__':
    current_ip = ''
    logging.basicConfig(format='%(message)s', level=logging.INFO)
    logger = logging.getLogger("DDNS")
    get_record()
    logger.info("[info] Start.")
    try:
        while 1:
            ip = get_ip()
            if current_ip != ip:
                update_record(ip)
                sleep(5)
                get_record()
            sleep(60)
    except KeyboardInterrupt:
        logger.warning("\033[1;33m[Error]\033[0m Accept the exit signal.")
        sleep(1)
