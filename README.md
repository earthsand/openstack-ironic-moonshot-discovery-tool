# openstack-ironic-moonshot-discovery-tool
Openstack Ironic Chassis Discovery Tool for Moonshot hardware

A new tool to query nodes and their hardware properties
at chassis level and register the node information in the Ironic
database.
This tool targets chassis management of micro-servers or similar enlosures
where the chassis has an active interface to query the details of large
number of baremetal nodes. Scaling the number of nodes is also managed with
a view that querying individual nodes to inspect their properties will consume
significant time.

This tool will reside in the ironic/tools folder.


The chassis discovery driver is loaded when the tool is invoked

Pre requisite to load the driver is to give entry points in
setup.py and run install. stevedore library is used to load
the driver
The tool is invoked with the following commands -
To Discovery and Create:
  "python chassis_discovery_tool.py -a create -i <hostname>
             -u <username> -p <password> -d <driver> -s <discovery_driver>"
Sample cmd to update hostname:
  "python chassis_discovery_tool.py -a update -i <hostname> -c <chassis_uuid>"
Sample cmd to delete chassis:
  "python chassis_discovery_tool.py -a delete -c <chassis_uuid>"
