# Copyright (C) 2016 Hewlett Packard Enterprise Development LP
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

"""
Author: Máximo Coghi H. - maximo.coghi-hernandez@hpe.com
        Srinivasan Srivatsan - srinivasan.srivatsan@hpe.com
        Nilesh Shinde - nilesh.shinde@hpe.com

Test_Name: "NTPClient_NoAuth"
Test_Description: "Verify DUT's behavior after connecting with maximum
                    configurable NTP servers and authentication disabled
                    each NTP server"

Notes: "- Only one host will be used. Multiple vlans will be added to host in
        order to simulate a total of eight servers"
"""

from pytest import mark
from time import sleep


TOPOLOGY = """
# +--------+     +--------+
# |        |     |        |
# |  ops1  <-----+  ops2  |
# |        |     |        |
# +--------+     +---^----+
#                    |
#                +--------+
#                |        |
#                |  hs1   |
#                |        |
#                +--------+

# Nodes
[type=openswitch name="OpenSwitch 1"] ops1
[type=openswitch name="OpenSwitch 2"] ops2
[type=host name="Host 1" image="Ubuntu"] hs1

# Links
[force_name=eth0] ops1:eth0
ops1:eth0 -- ops2:if01
ops2:if02 -- hs1:eth1
"""

# Local Variables
OPS_GW = '192.168.1.1'
OPS_IP = '192.168.1.2'
MASK = '/24'

HOST_INTERFACE = 'eth1'
HS1_IP = '192.168.{}.1'

CONNECTED_SERVER = ''
DISCONNECTED_SERVERS = []

MD5_PASSWORD = 'aNewPassword00{}'
NTP_SERVERS = ["127.127.1.0"]

TOTAL_TIMEOUT = 1020
TIMEOUT = 5

MAX_NTP_SERVERS = 8
TOTAL_FAILOVERS = 0


# The function adds an IP address to management interface
def set_switch_mgmt_interface(ops1, ip_address, ip_gateway, step):
    step("Configure switch interface mgmt IP address")
    with ops1.libs.vtysh.ConfigInterfaceMgmt() as ctx:
        ctx.ip_static(ip_address)
        ctx.default_gateway(ip_gateway)


# Function that creates vlans in second switch
def set_switch_vlans(ops1, vlans, step):
    step("Configure switch vlans")

    for vlan in range(1, vlans + 1):
        with ops1.libs.vtysh.ConfigVlan(vlan) as ctx:
            ctx.no_shutdown()


# Function that configure interfaces in second switch
def set_switch_interface_vlan(ops1, vlans, step):
    step("Configure middle switch interfaces")

    with ops1.libs.vtysh.ConfigInterface('if01') as ctx:
        ctx.no_shutdown()
        ctx.no_routing()
        ctx.vlan_access(1)

    with ops1.libs.vtysh.ConfigInterface('if02') as ctx:
        ctx.no_shutdown()
        ctx.no_routing()
        for vlan in range(1, vlans + 1):
            ctx.vlan_trunk_allowed(str(vlan))


# Function that configures a vlan interface and adds an IP address
# for each simulated NTP server
def set_host_config_interfaces(hs1, vlans, host_interface, hs1_ip, mask, step):
    step("Configure host 1 vlan interfaces")

    hs1.libs.vlan.install_vlan_packet()
    hs1.libs.vlan.load_8021q_module()
    hs1.libs.vlan.enable_ip_forward()

    # Configure each vlan IP address
    for vlan_id in range(1, vlans + 1):
        hs1.libs.vlan.add_vlan(host_interface, vlan_id)
        ip_address = hs1_ip.format(vlan_id) + mask
        hs1.libs.vlan.add_ip_address_vlan(ip_address, host_interface, vlan_id)


# Function that configures the host's IP address and ntpd for authentication
def set_host_ntpd(hs1, ntp_servers, step):
    step("Configure host ntpd service")

    hs1.libs.ntpd.ntpd_stop()
    for server in ntp_servers:
        hs1.libs.ntpd.add_ntp_server(server)
    hs1.libs.ntpd.ntpd_config_files(False)
    hs1.libs.ntpd.ntpd_start()


# Function that checks connectivity between host and DUT
def verify_connectivity_host(hs1, ops1, packets, step):
    step("Test ping between host and DUT")
    ping = hs1.libs.ping.ping(packets, ops1)
    assert ping['received'] > 3, (
        "Total of received packets is below the expected, " +
        "Expected: {}".format(packets)
    )


# Function that enable or disable NTP authentication on switch
def set_ntp_authentication(ops1, step, auth_enabled=True):
    if auth_enabled:
        step("Enable NTP authentication")
        with ops1.libs.vtysh.Configure() as ctx:
            ctx.ntp_authentication_enable()
    else:
        step("Disable NTP authentication")
        with ops1.libs.vtysh.Configure() as ctx:
            ctx.no_ntp_authentication_enable()


# Function to set NTP server profile
def set_ntp_server_without_key(ops1, server):
    print("Add NTP server {}".
          format(server))
    with ops1.libs.vtysh.Configure() as ctx:
        ctx.ntp_server(server)


# Function to add the NTP server to DUT's configuration
def set_ntp_servers(ops1, hs1_ip, total_servers, step):
    step("Configure max NTP servers")
    for counter in range(1, total_servers + 1):
        set_ntp_server_without_key(ops1, hs1_ip.format(counter))


# Function that changes the preferred NTP server
def set_ntp_server_prefer(ops1, ip_address):
    with ops1.libs.vtysh.Configure() as ctx:
        ctx.ntp_server_prefer(ip_address)


# Function that validates if switch is synchronized with NTP server
def validate_ntp_status(ops1):
    global CONNECTED_SERVER
    show_ntp_status_re = ops1.libs.vtysh.show_ntp_status()

    auth_status_value = show_ntp_status_re['authentication_status']
    assert auth_status_value == 'disabled', (
        "Authentication status is not the expected, Expected: disabled"
    )

    if 'server' in show_ntp_status_re:
        CONNECTED_SERVER = show_ntp_status_re['server']
        return True
    else:
        return False


# Function that validates if an NTP association is properly added
def validate_ntp_associations(ops1):
    show_ntp_assoc_re = ops1.libs.vtysh.show_ntp_associations()

    for key in show_ntp_assoc_re.keys():
        code = show_ntp_assoc_re[key]['code']
        if code == '*':
            return True
    return False


# Function that checks if switch synchronized with NTP server or not
def check_ntp_status_and_associations(ops1, total_timeout, timeout, step):
    step("Check NTP status and NTP associations")

    check_status = False
    check_associations = False
    for t in range(0, total_timeout, timeout):
        # Timeout check for each iteration
        sleep(timeout)
        if check_status is False:
            check_status = validate_ntp_status(ops1)
        if check_associations is False:
            check_associations = validate_ntp_associations(ops1)
        if check_status is True and check_associations is True:
            return True

    assert check_status is True and check_associations is True, (
        "Timeout occurred. DUT didn't synch with NTP server"
    )


# Function to check that synchronized server gets updated
def check_ntp_server_update(ops1, step):
    global CONNECTED_SERVER

    check_update = False
    increase_timeout = 0
    ops1._telnet.disconnect()
    while check_update is False:
        show_ntp_status_re = ops1.libs.vtysh.show_ntp_status()
        if show_ntp_status_re['server'] != CONNECTED_SERVER:
            CONNECTED_SERVER = show_ntp_status_re['server']
            check_update = True
            print(
                'Server updated after {} seconds'.
                format(increase_timeout)
            )
        increase_timeout = increase_timeout + TIMEOUT
        sleep(TIMEOUT)


@mark.timeout(3600)
@mark.platform_incompatible(['docker'])
def test_authentication_disabled(topology, step):
    """
    Connect max. NTP servers with authentication enabled and keys
    """
    ops1 = topology.get('ops1')
    ops2 = topology.get('ops2')
    hs1 = topology.get('hs1')

    assert ops1 is not None
    assert ops2 is not None
    assert hs1 is not None

    # Configure DUT's management interface IP address
    set_switch_mgmt_interface(ops1, (OPS_IP + MASK), OPS_GW, step)

    # Configure middle switch vlans
    set_switch_vlans(ops2, MAX_NTP_SERVERS, step)

    # Configure middle switch interface vlans
    set_switch_interface_vlan(ops2, MAX_NTP_SERVERS, step)

    # Configure host IP addresses
    set_host_config_interfaces(hs1, MAX_NTP_SERVERS, HOST_INTERFACE,
                               HS1_IP, MASK, step)

    # Configure host ntpd process
    set_host_ntpd(hs1, NTP_SERVERS, step)

    # Connectivity test
    verify_connectivity_host(hs1, OPS_IP, 5, step)

    # Disable authentication
    set_ntp_authentication(ops1, step, False)

    # Configure NTP server profile
    set_ntp_servers(ops1, HS1_IP, MAX_NTP_SERVERS, step)

    # Set last NTP server as preferred
    set_ntp_server_prefer(ops1, HS1_IP.format(MAX_NTP_SERVERS))

    # Check show commands
    check_ntp_status_and_associations(ops1, TOTAL_TIMEOUT, TIMEOUT, step)
