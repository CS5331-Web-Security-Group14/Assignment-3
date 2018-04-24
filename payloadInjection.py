import requests
import urlparse
import sys
import json
import logging

#defining constants

SQL_INJECTION = "SQL Injection"
SERVER_SIDE_CODE_INJECTION = "Server Side Code Injection"
DIRECTORY_TRAVERSAL = "Directory Traversal"
OPEN_REDIRECT = "Open Redirect"
CSRF = "Cross Site Request Forgery"
SHELL_CMD_INJECTION = "Shell Command Injection"

def is_attack_successful(attack_type, response, endpoint):
    success = False
    if attack_type == OPEN_REDIRECT:
        if '<title>GitHub System Status</title>' in response['result']:
            success = True
    elif attack_type == SHELL_CMD_INJECTION:
        if 'Linux' in response['result']:
            success = True
    elif attack_type == DIRECTORY_TRAVERSAL:
        if 'root' in response['result']:
            success = True
    elif attack_type == SQL_INJECTION:
            success = False
    else:
        success = False

    if success == True:
        logging.info('\n')
        logging.info('!! Potential {0} attack found at {1} !!\n'.format(attack_type, endpoint))

    return success

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
    logging.info('Starting Phase 2: Payload Generation for {0} attack'.format(attack_type))
    payload_file = get_payload_file(attack_type)
    logging.info('Retrieving payloads from {0} file'.format(payload_file))
    logging.info('Completed Phase 2: Payload Generation for {0} attack\n\n---------------------\n'.format(attack_type))
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
    logging.info('Starting Phase 3: Payload Injection for {0} attack\n'.format(attack_type))
    obj = {"class" : attack_type, "results" : {}}
    end_points = json.load(open('scrapeTarget_phase1.json'))
    
    for url in end_points:
        injection_points = end_points[url]
        parsed = urlparse.urlparse(url)
        if url not in obj["results"]:
	    obj["results"][url] = []
        response = {}
        
        for injection_point in injection_points:
            if injection_point['method'] == 'POST':
                for payload in payloads:
                    response = post_request(url, injection_point, payload)
            elif injection_point['method'] == 'GET':
                for payload in payloads:
                    response = get_request(attack_type, url, injection_point, payload)
            
            success = is_attack_successful(attack_type, response, urlparse.urljoin(url, injection_point['endpoint']))
            response['success'] = success
            obj["results"][url].append(response)
    
    op_file = attack_type.replace(" ","")+".json"
    logging.info('Generating Phase 3 output file for {0} attack\n'.format(attack_type))
    with open("response/"+op_file, 'w') as fp:
        json.dump(obj, fp, sort_keys=True, indent=4)

def main():
    logging.basicConfig(filename='scanner_logs.log', format='%(asctime)s %(message)s', level=logging.DEBUG)
    attack_type = sys.argv[1]
    launch_attack(attack_type)
    logging.info('Completed Phase 3: Payload Injection for {0}\n\n---------------------\n'.format(attack_type))

if __name__ == "__main__":
    main()
