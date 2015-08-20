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


import os
from ironicclient import client as irclient


def get_client_handle():

    kwargs = {'os_username': os.environ['OS_USERNAME'],
              'os_password': os.environ['OS_PASSWORD'],
              'os_auth_url': os.environ['OS_AUTH_URL'],
              'os_tenant_name': os.environ['OS_TENANT_NAME']}

    ironic = irclient.get_client(1, **kwargs)
    return ironic


def create_chassis(hostname, username, password, ironic_driver,
                   discovery_driver):

    ironic = get_client_handle()
    chassis_create_kwargs = {'description': "discovery mode",
                             'extra': {'host': hostname,
                                       'username': username,
                                       'password': password,
                                       'ironic_driver': ironic_driver,
                                       'discovery_driver':
                                                  str(discovery_driver)}
                             }
    chassis = ironic.chassis.create(**chassis_create_kwargs)
    return chassis


def create_node(chassis_uuid, node_details, switch_details,
                ironic_driver, driver_details):

    ironic = get_client_handle()
    node_create_kwargs = {'properties': node_details,
                          'driver': ironic_driver,
                          'driver_info': driver_details,
                          'chassis_uuid': chassis_uuid,
                          'extra': switch_details}
    new_node = ironic.node.create(**node_create_kwargs)
    return new_node


def create_port(node_uuid, port_details):

    ironic = get_client_handle()
    port_create_kwargs = {'node_uuid': node_uuid,
                          'address': port_details['address']}
    ironic.port.create(**port_create_kwargs)


def delete_chassis(chassis_uuid):

    ironic = get_client_handle()
    nodes = ironic.chassis.list_nodes(chassis_uuid)

    for node in nodes:
        ironic.node.delete(node.uuid)

    ironic.chassis.delete(chassis_uuid)


def update_nodes(chassis_uuid, patch):

    ironic = get_client_handle()

    nodes = ironic.chassis.list_nodes(chassis_uuid)
    for node in nodes:
        ironic.node.update(node.uuid, patch)


def update_chassis(chassis_uuid, chassis_update_path, node_update_path, value):

    ironic = get_client_handle()

    patch = [
                {'op': 'replace', 'path': chassis_update_path, 'value': value},
            ]
    ironic.chassis.update(chassis_uuid, patch)
    if node_update_path:

        patch = [
                {'op': 'replace', 'path': node_update_path, 'value': value},
                ]

        update_nodes(chassis_uuid, patch)
