import sys
import yaml
import re
import json
import logging
import threading
import time
from os import path
import kraken.cerberus.setup as cerberus
import kraken.kubernetes.client as kubecli
import kraken.invoke.command as runcommand
import kraken.pvc.pvc_scenario as pvc_scenario
import ssh.utils as utils
import ssh.log as log
import ssh.control as control


def run1(scenarios_list, config):
	namespace = "kraken"
	failed_post_scenarios = ""
	go_meter_pod = ""
	lins_blkpvc_file = scenarios_list[0][0]
	gomet_pod_file = scenarios_list[1][0]
	stor_file = scenarios_list[2][0]
	utils._init()
	logger = log.Log()
	utils.set_logger(logger)
	stor_config = utils.ConfFile(stor_file)
	kind = stor_config.get_kind()

	pvc_resoure = kubecli.create_pvc(lins_blkpvc_file)
	time.sleep(30)

	
	with open(path.join(path.dirname(__file__), gomet_pod_file)) as f:
		gomet_pod_config = yaml.safe_load(f)
		metadata_config = gomet_pod_config["metadata"]
		go_meter_pod = metadata_config.get("name", "")
		kubecli.create_pod(gomet_pod_config, namespace, 120)

	time.sleep(3)

	versa_con = control.IscsiTest(stor_config)	

	versa_con.ckeck_drbd_status_spof(pvc_resoure, False)
	#versa_con.check_drbd_crm_res(pvc_resoure, False)
		
	logging.info("Go-meter start to write")
	threading.Thread(target=gometer_write, args=(go_meter_pod, write_wait)).start()
	if kind == "node_down":
		versa_con.down_node()
	elif kind == "interface_down":
		versa_con.down_node_interface()
	elif kind == "switch_port_down":
		versa_con.down_switch_port()
	elif kind == "hand_operation":
		logging.info("Please do hand operation...")

	logging.info("Go-meter is writing, waite...")
	write_wait.wait()

	versa_con.ckeck_drbd_status_spof(pvc_resoure, True)
	#versa_con.check_drbd_crm_res(pvc_resoure, True)

	logging.info("Go-meter start to compare")
	command = "cd /go/src/app;./main compare"
	response = kubecli.exec_cmd_in_pod(command, go_meter_pod, namespace)
	logging.info("\n" + str(response))

	time.sleep(2)

	kubecli.delete_pod(go_meter_pod, namespace)
	kubecli.delete_pvc(lins_blkpvc_file)


def run(scenarios_list, config):
	namespace = "kraken"
	failed_post_scenarios = ""
	go_meter_pod = ""
	lins_blkpvc_file = scenarios_list[0][0]
	gomet_pod_file = scenarios_list[1][0]
	stor_file = scenarios_list[2][0]
	utils._init()
	logger = log.Log()
	utils.set_logger(logger)
	stor_config = utils.ConfFile(stor_file)
	kind = stor_config.get_kind()


	versa_con = control.IscsiTest(stor_config)	

	versa_con.down_switch_port()




def runc(scenarios_list, config):
	namespace = "kraken"
	failed_post_scenarios = ""
	#for app_config in scenarios_list:

	lins_blkpvc_file = scenarios_list[0][0]
	pvc_resoure = kubecli.create_pvc(lins_blkpvc_file)
	print(pvc_resoure_name)
	time.sleep(30)

	gomet_pod_file = scenarios_list[1][0]
	with open(path.join(path.dirname(__file__), gomet_pod_file)) as f:
		gomet_pod_config = yaml.safe_load(f)
		kubecli.create_pod(gomet_pod_config, namespace, 120)



def rund(scenarios_list, config):
	namespace = "kraken"
	failed_post_scenarios = ""
	#for app_config in scenarios_list:

	lins_blkpvc_file = scenarios_list[0][0]

	gomet_pod_file = scenarios_list[1][0]


	with open(path.join(path.dirname(__file__), gomet_pod_file)) as f:
		gomet_pod_config = yaml.full_load(f)
		scenario_config = gomet_pod_config["metadata"]
		pod_name = scenario_config.get("name", "")
		kubecli.delete_pod(pod_name, namespace)

	kubecli.delete_pvc(lins_blkpvc_file)

def run22(scenarios_list, config):
	namespace = "kraken"
	failed_post_scenarios = ""
	go_meter_pod = ""
	write_wait = threading.Event()
	#for app_config in scenarios_list:

	lins_blkpvc_file = scenarios_list[0][0]
	gomet_pod_file = scenarios_list[1][0]

	with open(path.join(path.dirname(__file__), gomet_pod_file)) as f:
		gomet_pod_config = yaml.full_load(f)
		scenario_config = gomet_pod_config["metadata"]
		go_meter_pod = scenario_config.get("name", "")

	logging.info("Go-meter start to write")
	threading.Thread(target=gometer_write, args=(go_meter_pod, write_wait)).start()

	write_wait.wait()
	logging.info("Go-meter start to compare")
	command = "cd /go/src/app;./main compare"
	response = kubecli.exec_cmd_in_pod(command, go_meter_pod, namespace)
	logging.info("\n" + str(response))

def run2(scenarios_list, config):
	spof_file = scenarios_list[2][0]
	with open(spof_file, "r") as f:
		config_yaml = yaml.full_load(f)
		scenario_config = config_yaml["spof_scenario"]
		down_interface_host = scenario_config["down_interface_host"]
		inf = get_host_inf(down_interface_host)
		interface = down_interface_host["interface"]
		host = utils.SSHConn(inf["ip"],inf["port"], inf["username"], inf["password"])

		host.down_interface(interface)
		host.up_interface(interface)

def ru3(scenarios_list, config):
	spof_file = scenarios_list[2][0]

	utils._init()
	logger = log.Log()
	utils.set_logger(logger)

	configfile = utils.ConfFile(spof_file)

	#inf = configfile.get_interface_inf()
	#interface = inf["interface"]
	#host = utils.SSHConn(inf["ip"],inf["port"], "root", inf["password"])
	#host.down_interface(interface)
	#host.up_interface(interface)

	versa_con = control.IscsiTest(configfile)
	versa_con.test_down()
	#versa_con.ckeck_drbd_status_spof("res_b",1)
	#versa_con.check_drbd_crm_res("res_b", False)

	#remote_node = utils.SSHConn(ip, port, user, password, timeout=100)



def gometer_write(pod_name,write_wait):

	command = "cd /go/src/app;./main write"
	response = kubecli.exec_cmd_in_pod(command, pod_name, "kraken")
	logging.info("\n" + str(response))
	write_wait.set()













