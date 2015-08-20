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

import abc
import six


@six.add_metaclass(abc.ABCMeta)
class BaseDiscovery(object):

    """Base class for Chassis Discovery

    A driver for chassis discovery
    must implement this class and include specific details

    """

    # auth token for chassis connection
    token = None

    def __init__(self, username, password, host):

        self.username = username
        self.password = password
        self.host = host

    @abc.abstractmethod
    def chassis_connect(self):

        """
        Log in to the chassis and establish session
        Set the auth token class variable for further access
        """

    @abc.abstractmethod
    def call_protocol(self, inner_url_member, chassis_ilo_ip):

        """
        Contact chassis with specific protocol.
        Different hardware vendors will have
        different ways to connect to the chassis -
        ssh, http, cli, netcat, ris are examples.

        :return: details
        """

    @abc.abstractmethod
    def gather_chassis_details(self):

        """
        Contact chassis interface using call_protocol method
        and query for chassis details

        :return: chassis_details: a list with each element being
                 a dictionary of properties.
        """

    # The following four methods work for a single node. The Discovery
    # tool calls these methods with a single element (node) from gathered
    # chassis_details.
    @abc.abstractmethod
    def get_node_details(self, node):

        """
        Extract properties
                 cpu_arch
                 no_of_cores
                 local_disk_size
                 memory_size
        for a single node

        :param node: a single element from chassis_details
        :return: node_properties_details for a specific node
        """

    @abc.abstractmethod
    def get_port_details(self, node):

        """
        Set port details such as mac_address
        for ports in a node.

        :param node: a single element from chassis_details
        :return: port_details for a specific node
        """

    @abc.abstractmethod
    def get_switch_details(self, node):

        """
        Gather mac_address, switch_port_id and other related
        switch details

        :param node: a single element from chassis_details
        :return: switch_details for a specific node
        """

    @abc.abstractmethod
    def get_driver_details(self, node):

        """
        Set driver details such as address, username, password
        for the specific Ironic power/deploy driver.

        :param node: a single element from chassis_details
        :return: driver_details for a specific node
        """
