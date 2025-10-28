# parsers/__init__.py
from .nginx import parse_nginx_log
from .apache import parse_apache_log
from .generic import parse_generic_log
import re

def detect_log_type(sample_lines):
    nginx_pattern = re.compile(r'\d+\.\d+\.\d+\.\d+ - - \[')
    apache_pattern = re.compile(r'\d+\.\d+\.\d+\.\d+ - - \[')
    json_pattern = re.compile(r'^\s*\{.*\}\s*$')

    for line in sample_lines:
        if nginx_pattern.search(line):
            return 'nginx'
        if apache_pattern.search(line):
            return 'apache'
        if json_pattern.match(line):
            return 'json'
    return 'generic'

def parse_log_file(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()[:10000]  # ограничение на 10k строк

    sample = lines[:10]
    log_type = detect_log_type(sample)

    if log_type == 'nginx':
        return [parse_nginx_log(line) for line in lines if line.strip()]
    elif log_type == 'apache':
        return [parse_apache_log(line) for line in lines if line.strip()]
    elif log_type == 'json':
        import json
        logs = []
        for line in lines:
            try:
                data = json.loads(line.strip())
                data['raw'] = line.strip()
                data['level'] = data.get('level', 'INFO').upper()
                logs.append(data)
            except:
                continue
        return logs
    else:
        return [parse_generic_log(line) for line in lines if line.strip()]