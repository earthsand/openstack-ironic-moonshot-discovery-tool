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

import json
import requests
from basediscovery import BaseDiscovery
from ironic.common import exception


class MoonshotDiscovery(BaseDiscovery):

    CARTRIDGE_IPMB_START_ADR = 130
    NODE_IPMB_START_ADDR = 114
    MOONSHOT_CPU_ARCH = "x86_64"
    MOONSHOT_LOCAL_DISK_SPACE = 400

    IPMI_TERMINAL_PORT = 9091
    IPMI_TARGET_CHANNEL = 7
    IPMI_TRANSIT_CHANNEL = 0
    IPMI_LOCAL_ADDRESS = "0x20"
    IPMI_BRIDGING_TYPE = "dual"

    def __init__(self, username, password, host):

        super(MoonshotDiscovery, self).__init__(username, password, host)

    def chassis_connect(self):

        """
            HP Moonshot is a micro-server that has an active
            RIS interface in the Chassis to query for node
            properties and details.

            The connection protocol here is REST based querying
            :return: token for further access
        """
        url_member = "/rest/v1/Sessions"
        url = "https://" + self.host + url_member
        payload = {"UserName": self.username, "Password": self.password}
        headers = {'content-type': 'application/json'}
        response = requests.post(url, data=json.dumps(payload),
                                 headers=headers, verify=False)
        details = response.headers
        try:
            self.auth_token = details['x-auth-token']
        except KeyError as e:
            raise exception.Invalid(e)

    def call_protocol(self, inner_url_member, chassis_ilo_ip):
        url = "https://" + chassis_ilo_ip + inner_url_member
        headers = {'content-type': 'application/json',
                   'x-auth-token': self.auth_token}
        response = requests.get(url, headers=headers, verify=False)
        details = response.json()
        return details

    # Following three methods are utility methods
    # specific to HP Moonshot
    @staticmethod
    def convertGBtoMB(value):

        return value * 1024

    @staticmethod
    def getTransitAddress(cartridgeSlot):

        return MoonshotDiscovery.CARTRIDGE_IPMB_START_ADR + 2 * (cartridgeSlot)

    @staticmethod
    def getTargetAddress(nodeSlot):

        return MoonshotDiscovery.NODE_IPMB_START_ADDR + 2 * (nodeSlot)

    def gather_chassis_details(self):

        chassis_details = []
        url_member = "/rest/v1/Chassis"
        details = self.call_protocol(url_member, self.host)
        try:
            chassis_list = details['links']['Member']
            for member in chassis_list:
                url_member = member['href']
                chassis_link_details = self.call_protocol(
                                       url_member, self.host)

            # Step 1 - Get the cartridges access layer
            cartridges_url_member = (chassis_link_details['links']
                                    ['Cartridges']['href'])
            cartridge_details = self.call_protocol(
                                cartridges_url_member, self.host)
            cartridge_members = cartridge_details['links']['Member']
            # Step 2 - Get individual cartridge details
            for cart_member in cartridge_members:
                cartridge_url_member = cart_member['href']
                node_details = self.call_protocol(
                               cartridge_url_member, self.host)
                # Step 3 - Get into the Node access layer for that Cartridge
                if 'ComputerSystems' in node_details['links']:
                    node_members = node_details['links']['ComputerSystems']
                    for node_member in node_members:
                        node_url_member = node_member['href']
                        node_inner_details = self.call_protocol(
                                             node_url_member, self.host)
                        # Step 4 - Collect cores, memory and arch for each node
                        single_node = dict()
                        single_node['cartridge_slot'] = (cartridge_members.
                                                         index(cart_member))
                        single_node['node_slot'] = (node_members.
                                                    index(node_member))
                        single_node['cpus'] = (details['Processors']
                                              ['NumberOfCores'])
                        single_node['memory_mb'] = (MoonshotDiscovery.
                                    convertGBtoMB(node_inner_details['Memory']
                                    ['TotalSystemMemoryGB']))
                        single_node['cpu_arch'] = (MoonshotDiscovery.
                                                  MOONSHOT_CPU_ARCH)
                        single_node['mac_addr'] = (node_inner_details
                                    ['HostCorrelation']['HostMACAddress'][0])
                        single_node['mac_addr2'] = (node_inner_details
                                    ['HostCorrelation']['HostMACAddress'][1])
                    chassis_details.append(single_node)
        except KeyError as e:
            raise exception.Invalid(e)

        return chassis_details

    def get_node_details(self, node):

        node_details = dict()
        node_details['memory_mb'] = node['memory_mb']
        node_details['cpu_arch'] = node['cpu_arch']
        node_details['local_gb'] = MoonshotDiscovery.MOONSHOT_LOCAL_DISK_SPACE
        node_details['cpus'] = node['cpus']
        node_details['mac_addr'] = node['mac_addr']

        return node_details

    def get_port_details(self, node):

        port_details = dict()
        port_details['address'] = node['mac_addr']

        return port_details

    def get_switch_details(self, node):

        switch_details = dict()
        switch_details['hardware/interfaces/0/switch_chassis_descr'] = "sa"
        switch_details['hardware/interfaces/0/switch_port_id'] = "1/0/" + str(
                                                    node['cartridge_slot'] + 1)
        switch_details['hardware/interfaces/0/mac_address'] = node['mac_addr']
        switch_details['hardware/interfaces/0/switch_port_des'] = "port" + str(
                                                    node['cartridge_slot'] + 1)
        switch_details['hardware/interfaces/0/name'] = "eth0"
        switch_details['hardware/interfaces/0/switch_chassis_id'] = "SwitchA"

        switch_details['hardware/interfaces/1/switch_chassis_descr'] = "sb"
        switch_details['hardware/interfaces/1/switch_port_id'] = "1/0/" + str(
                                                    node['cartridge_slot'] + 1)
        switch_details['hardware/interfaces/1/mac_address'] = node['mac_addr2']
        switch_details['hardware/interfaces/1/switch_port_des'] = "port" + str(
                                                    node['cartridge_slot'] + 1)
        switch_details['hardware/interfaces/1/name'] = "eth1"
        switch_details['hardware/interfaces/1/switch_chassis_id'] = "SwitchB"

        return switch_details

    def get_driver_details(self, node):

        driver_details = dict()
        driver_details['ipmi_transit_address'] = (hex(
            MoonshotDiscovery.getTransitAddress(node['cartridge_slot'])))
        driver_details['ipmi_terminal_port'] = (MoonshotDiscovery.
                                               IPMI_TERMINAL_PORT)
        driver_details['ipmi_target_channel'] = (MoonshotDiscovery.
                                                IPMI_TARGET_CHANNEL)
        driver_details['ipmi_transit_channel'] = (MoonshotDiscovery.
                                                 IPMI_TRANSIT_CHANNEL)
        driver_details['ipmi_local_address'] = (MoonshotDiscovery.
                                               IPMI_LOCAL_ADDRESS)
        driver_details['ipmi_username'] = self.username
        driver_details['ipmi_address'] = self.host
        driver_details['ipmi_target_address'] = (hex(
            MoonshotDiscovery.getTargetAddress(node['node_slot'])))
        driver_details['ipmi_password'] = self.password
        driver_details['ipmi_bridging'] = MoonshotDiscovery.IPMI_BRIDGING_TYPE

        return driver_details
