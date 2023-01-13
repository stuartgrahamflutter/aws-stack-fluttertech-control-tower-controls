import subprocess
import control_config
from pprint import pprint

ORG_ID = 'o-c6co4u7u9s'
MANAGEMENT_ACCOUNT = '293146768702'
REGION = 'eu-west-1'

AWS_ORG_OU_IDS = [
    {'name': 'Infrastructure', 'id': 'ou-cthw-adl1zi8t'},
    {'name': 'Sandbox', 'id': 'ou-cthw-korcoo3r'},
    {'name': 'Security', 'id': 'ou-cthw-voezy2wp'},
    {'name': 'Workloads', 'id': 'ou-cthw-73b802zi'},
    {'name': 'Production', 'id': 'ou-cthw-w5cdagce'},
    {'name': 'Development', 'id': 'ou-cthw-w5cdagce'}
]

CONTROLS = control_config.CONTROLS


# Future use to run command directly
def run_aws_cli(command):
    command = command.split(' ')
    print(f'Running subprocess.run({command})')
    subprocess.run(command)


def write_command_list_file(command_list):
    with open('controls.sh','w') as f:
        for command in command_list:
            f.writelines(command+'\n')


def lookup_ou_id(ou_name):
    for ou in AWS_ORG_OU_IDS:
        if ou_name.lower() == ou['name'].lower():
            return ou['id']
    return ''


def build_command(control_id, ou_id):
    return (
        f'aws controltower enable-control '
        f'--control-identifier arn:aws:controltower:{REGION}::control/{control_id} '
        f'--target-identifier arn:aws:organizations::{MANAGEMENT_ACCOUNT}:ou/{ORG_ID}/{ou_id}'
    )

def build_command_list(control):
    # example control
    # {'id': 'AWS-GR_NO_UNRESTRICTED_ROUTE_TO_IGW', 'include': 'ALL', 'exclude': ['Sandbox, Infrastructure']}
    command_list = []

    if isinstance(control['include'], list):
        if control['include'][0].lower() == 'all':
            for ou in AWS_ORG_OU_IDS:
                command_list.append(build_command(control['id'], ou['id']))
        
        else:
            for ou in control['include']:
                ou_id = lookup_ou_id(ou)
                if bool(ou_id):
                    print('in here')
                    command_list.append(build_command(control['id'], ou_id))


    if isinstance(control['exclude'], list):
        for ou in control['exclude']:
            ou_id = lookup_ou_id(ou)
            if bool(ou_id):
                for i in command_list:
                    if ou_id in i:
                        command_list.remove(i)

    return command_list



def main():
    command_list = []
    for control in CONTROLS:
        command_list.extend(build_command_list(control))
    write_command_list_file(command_list)


main()



