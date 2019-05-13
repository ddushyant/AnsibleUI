import argparse
import subprocess
import os
from pprint import PrettyPrinter
import json

pp = PrettyPrinter(indent=4)

parser = argparse.ArgumentParser()
parser.add_argument("-g", "--group", help="list", required=True)
parser.add_argument("-c", "--commands", help="path", required=True)
parser.add_argument("-n", "--cNames", help="command name", required=True)
parser.add_argument("-r", "--root", help="root", required=True)
args = parser.parse_args()

host = args.group
commands = args.commands
cNames = args.cNames
root = args.root
dir_path = os.path.dirname(os.path.realpath(__file__))

def ansibleGen(fName,host, commands, cNames,root):
	ansible="---\n- name: Data Retriver Tool\n  hosts: "+host+"\n  tasks:"
	ansible+='\n    - name: make an output file\n      command: touch /tmp/output-AnsibleUI.json\n      become: yes\n      args:\n       creates: "/tmp/output-AnsibleUI.json"\n       warn: no'
	ansible+="\n    - debug:\n        var: imported_var"
	jsonCreate=""
	for count in range(len(cNames)):
		if root[count] == 1:
			root[count] = "\n      become: yes"
		else:
			root[count] = ""
		ansible+="\n    - name: return "+cNames[count]+"\n      shell: echo $("+commands[count].strip('\"')+")\n      register: "+cNames[count]+root[count]
		jsonCreate += "| combine({ '"+cNames[count]+"': "+cNames[count]+".stdout_lines })"
	ansible+='\n    - name: append data to var\n      set_fact:\n        imported_var: "{{ imported_var | default([]) '+jsonCreate+' }}"'
	ansible+='\n    - debug:\n        var: imported_var'
	ansible+='\n    - name: write var to output file\n      copy:\n        content: "{{ imported_var | to_nice_json }}"\n        dest: /tmp/output-AnsibleUI.json\n      become: yes'
	ansible+='\n    - name: get host name\n      command: hostname\n      register: host'
	ansible+='\n    - name: copy the file to local\n      command: cat /tmp/output-AnsibleUI.json\n      register: data'
	ansible+='\n    - local_action: copy content={{ data.stdout }} dest={{playbook_dir}}/out/{{host.stdout}}.json'
	f = open(fName, 'w')
	f.write(ansible)

def htmlGen(directory):
	html = '''<!DOCTYPE html>
	<html>
	<head>
	<style>
	table {
	  font-family: arial, sans-serif;
	  border-collapse: collapse;
	  width: 100%;
	}

	td, th {
	  border: 1px solid #dddddd;
	  text-align: left;
	  padding: 8px;
	}

	tr:nth-child(even) {
	  background-color: #dddddd;
	}
	</style>
	</head>
	<body>

	<table>
	<tr>
    <th>Servers</th>
    <th>Uptime</th>
    <th>Cat</th>
    </tr>
	'''
	for filename in os.listdir(directory):
		with open(directory+filename) as json_file:
			data = json.load(json_file)
			html += "<tr><td>"+filename+"</td><td>"+str(data['uptime'][0])+"</td><td>"+str(data['cat'][0])+"</td></tr>"
	html += "</table></body></html>"
	f = open("index.html", 'w')
	f.write(html)

ansibleGen("dataServer.yml", host, map(str, commands.strip('[]').split(',')), map(str, cNames.strip('[]'). split(',')), map(int, root.strip('[]').split(',')))
os.system("rm -r "+dir_path+"/out/*")
ansibleCmd = 'ansible-playbook -i host.txt -u ciuser dataServer.yml --key-file="/root/.ssh/id_rsa_ciuser"'
output,error = subprocess.Popen(ansibleCmd, shell=True, executable="/bin/bash", stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
print error
htmlGen(dir_path+"/out/")





