#!/usr/bin/python

# Copyright 2013 Hewlett-Packard Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.


from chassis_enclosure import ChassisEnclosure
from ironic.common import exception
from optparse import OptionParser
from stevedore import driver


parser = OptionParser()
parser.add_option("-a", "--action", help="create|update|refresh|delete")
parser.add_option("-i", "--host", help="hostname of the chassis")
parser.add_option("-u", "--username", help="UserName of the chassis")
parser.add_option("-p", "--password", help="Password of the chassis")
parser.add_option("-d", "--ironic_driver",
                            help="Ironic Driver for Baremetal Nodes")
parser.add_option("-s", "--discovery_driver",
                            help="Discovery Driver for Chassis Discovery")
parser.add_option("-c", "--chassis_uuid",
                            help="chassis_uuid for update|refresh|delete")

(options, args) = parser.parse_args()

# Load the Discovery Driver
try:
    if options.discovery_driver:
        discovery_driver = driver.DriverManager(
                                namespace='ironic.tools.discovery',
                                name=options.discovery_driver,
                                invoke_on_load=True,
                                invoke_args=(options.username,
                                             options.password,
                                             options.host),
                            )
except KeyError:
    raise exception.DriverNotFound(driver_name=options.discovery_driver)

if options.action == "create":
    chassis = ChassisEnclosure(options.host, options.username,
                               options.password, options.ironic_driver,
                               discovery_driver, None)
    chassis.create_chassis()
elif options.action == "update":
    chassis = ChassisEnclosure(options.host, options.username,
                               options.password, options.ironic_driver,
                               None, options.chassis_uuid)
    chassis.update_chassis()
elif options.action == "delete":
    chassis = ChassisEnclosure(None, None, None, None, None,
                               options.chassis_uuid)
    chassis.delete_chassis()
