import sys
import yaml
import re
import json
import logging
import time
import kraken.cerberus.setup as cerberus
import kraken.kubernetes.client as kubecli
import kraken.invoke.command as runcommand
import kraken.pvc.pvc_scenario as pvc_scenario




def run(scenarios_list, config):
	print("start creat_pvc")
	failed_post_scenarios = ""
	#for app_config in scenarios_list:
	pvc_config = scenarios_list[0][0]
	kubecli.create_pvc(pvc_config)
	time.sleep(30)

	dep_config = scenarios_list[1][0]
	kubecli.create_dep(dep_config)
	time.sleep(55)

	t_config = scenarios_list[2][0]
	pvc_scenario.run(t_config, config)
	time.sleep(5)

	kubecli.delete_dep(dep_config)
	time.sleep(23)
	kubecli.delete_pvc(pvc_config)


