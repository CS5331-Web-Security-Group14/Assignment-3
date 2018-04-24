import requests
import urlparse
import sys
import json

#defining constants

SQL_INJECTION = "SQL Injection"
SERVER_SIDE_CODE_INJECTION = "Server Side Code Injection"
DIRECTORY_TRAVERSAL = "Directory Traversal"
OPEN_REDIRECT = "Open Redirect"
CSRF = "Cross Site Request Forgery"
SHELL_CMD_INJECTION = "Shell Command Injection"

def is_attack_successful(attack_type, response):
    if attack_type == OPEN_REDIRECT:
        if '<title>GitHub System Status</title>' in response['result']:
            return True
        else:
            return False
    elif attack_type == SHELL_CMD_INJECTION:
        if 'Linux' in response['result']:
            return True
        else:
            return False
    elif attack_type == DIRECTORY_TRAVERSAL:
        if 'root' in response['result']:
            return True
        else:
            return False
    elif attack_type == SQL_INJECTION:
        return True
    else:
        return True

#return payload file for specified attack
def get_payload_file(attack_type):
    return {
        SQL_INJECTION : "SQLInjection.txt",
        SERVER_SIDE_CODE_INJECTION : "ServerSideCodeInjection.txt",
        DIRECTORY_TRAVERSAL : "DirectoryTraversal.txt",
        OPEN_REDIRECT : "OpenRedirect.txt",
        CSRF : "CrossSiteRequestForgery.txt",
        SHELL_CMD_INJECTION : "ShellCommandInjection.txt"
    }.get(attack_type, '')

#return list of payloads for specified attack
def get_payload(attack_type):
    payload_file = get_payload_file(attack_type)
    if payload_file == '':
        return None
    with open('payload/'+payload_file) as f:
        return f.read().splitlines()

def post_request(url, injection_point, payload):
    response = {'endpoint': injection_point['endpoint'], 'params': {}, 'method': 'POST'}
    #construct data
    for param in injection_point['params']:
        if param['type'] == 'submit':
            continue
        elif param['type'] == 'text':
            response['params'][param['name']] = payload
    r = requests.post(urlparse.urljoin(url, injection_point['endpoint']), data=response['params'])
    response['result'] = r.text
    return response
            
def get_request(attack_type, url,injection_point, payload):
    paramStr = '?'
    response = {'endpoint': injection_point['endpoint'], 'params': {}, 'method': 'GET'}
    for param in injection_point['params']:
        response['params'][param['name']] = payload
        paramStr = paramStr + param['name'] + '=' + payload
    r = requests.get(urlparse.urljoin(url, injection_point['endpoint']+paramStr))
    response['result'] = r.text
    return response
            
def launch_attack(attack_type):
    payloads = get_payload(attack_type)
    obj = {"class" : attack_type, "results" : {}}
    end_points = json.load(open('scrapeTarget_phase1.json'))
    for url in end_points:
        injection_points = end_points[url]
        parsed = urlparse.urlparse(url)
        obj["results"] = []
        for injection_point in injection_points:
            if injection_point['method'] == 'POST':
                for payload in payloads:
                    response = post_request(url, injection_point, payload)
                    success = is_attack_successful(attack_type, response)
                    response['success'] = success
                    obj["results"].append(response)
            elif injection_point['method'] == 'GET':
                for payload in payloads:
                    response = get_request(attack_type, url, injection_point, payload)
                    success = is_attack_successful(attack_type, response)
                    response['success'] = success
                    obj["results"].append(response)
    op_file = attack_type.replace(" ","")+".json"
    with open(op_file, 'w') as fp:
        json.dump(obj, fp, sort_keys=True, indent=4)

def main():
    attack_type = sys.argv[1]
    launch_attack(attack_type)

if __name__ == "__main__":
    main()
