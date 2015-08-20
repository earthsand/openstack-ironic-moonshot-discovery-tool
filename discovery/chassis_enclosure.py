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

import ConfigParser
import chassis_discovery_utils


class ChassisEnclosure(object):

    def __init__(self, host=None, username=None, password=None,
                 ironic_driver=None, discovery_driver=None,
                 chassis_uuid=None):

        self.host = host
        self.username = username
        self.password = password
        self.ironic_driver = ironic_driver
        self.discovery_driver = discovery_driver
        self.chassis_uuid = chassis_uuid

    def create_chassis(self):

        # TODO: Exception Handling when driver not found
        # Discovery driver object
        discovery_driver = self.discovery_driver.driver
        # Connect to Chassis
        discovery_driver.chassis_connect()
        # Trigger Discovery process
        chassis_details = discovery_driver.gather_chassis_details()

        # If successful, create chassis, nodes and ports in Ironic database
        # Create chassis
        new_chassis = chassis_discovery_utils.create_chassis(self.hostname,
                           self.username, self.password, self.ironic_driver,
                           self.discovery_driver)
        # For each node in chassis details, gather
        # node_details, switch_details and port_details
        for node in chassis_details:
            node_details = discovery_driver.get_node_details(node)
            switch_details = discovery_driver.get_switch_details(node)
            driver_details = discovery_driver.get_driver_details(node)
            # Create Ironic Node
            new_node = chassis_discovery_utils.create_node(new_chassis.uuid,
                            node_details, switch_details,
                            self.ironic_driver, driver_details)
            # Create Ironic Port
            port_details = discovery_driver.get_port_details(node)
            chassis_discovery_utils.create_port(new_node.uuid, port_details)

    def delete_chassis(self):

        chassis_discovery_utils.delete_chassis(self.chassis_uuid)

    def update_chassis(self):

        config = ConfigParser.ConfigParser()
        config.read('node_update_path.ini')

        if self.host:
            chassis_update_path = '/extra/host'
            node_update_path = config.get('node_parameters_path', 'host')
            chassis_discovery_utils.update_chassis(self.chassis_uuid,
                                    chassis_update_path, node_update_path,
                                    self.host)

        if self.username:
            chassis_update_path = '/extra/username'
            node_update_path = config.get('node_parameters_path', 'username')
            chassis_discovery_utils.update_chassis(self.chassis_uuid,
                                    chassis_update_path, node_update_path,
                                    self.username)

        if self.password:
            chassis_update_path = '/extra/password'
            node_update_path = config.get('node_parameters_path', 'password')
            chassis_discovery_utils.update_chassis(self.chassis_uuid,
                                    chassis_update_path, node_update_path,
                                    self.password)

        if self.ironic_driver:
            chassis_update_path = '/extra/ironic_driver'
            node_update_path = "/driver"
            chassis_discovery_utils.update_chassis(self.chassis_uuid,
                                    chassis_update_path, node_update_path,
                                    self.ironic_driver)

        if self.discovery_driver:
            chassis_update_path = '/extra/discovery_driver'
            node_update_path = None
            chassis_discovery_utils.update_chassis(self.chassis_uuid,
                                    chassis_update_path, node_update_path,
                                    self.discovery_driver)
