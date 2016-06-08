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

Test_Name: "NTPClient_AuthEnabled"
Test_Description: "Verify synchronization of NTP server with OPS and
                  see if NTP client on OPS connects to atleast
                  one NTP server using authentication"

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

MD5_PASSWORD = 'aNewPassword00{}'
NTP_SERVERS = ["127.127.1.0"]

TOTAL_TIMEOUT = 1020
TIMEOUT = 5

MAX_NTP_SERVERS = 8


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
def set_host_ntpd(hs1, ntp_servers, md5_password, total_passwords, step):
    step("Configure host ntpd service")

    hs1.libs.ntpd.ntpd_stop()
    for server in ntp_servers:
        hs1.libs.ntpd.add_ntp_server(server)

    for key_id in range(1, total_passwords + 1):
        hs1.libs.ntpd.add_trustedkey(key_id)
        hs1.libs.ntpd.add_trustedkey_password(key_id,
                                              md5_password.format(key_id))
        hs1.libs.ntpd.ntpd_config_files(True, key_id)

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


# Function to set the NTP authentication-keys on switch
def set_ntp_authentication_keys(ops1, key_id, md5_password):
    print("Add NTP authentication key: {}".format(key_id))
    with ops1.libs.vtysh.Configure() as ctx:
        ctx.ntp_authentication_key_md5(str(key_id), md5_password)
        ctx.ntp_trusted_key(str(key_id))


# Function to set a key-id in NTP server profile
def set_ntp_server_with_key(ops1, server, key_id):
    print("Add NTP server {} with authentication key {}".
          format(server, key_id))
    with ops1.libs.vtysh.Configure() as ctx:
        ctx.ntp_server_key_id(server, str(key_id))


# Function to add the NTP server to DUT's configuration
def set_ntp_servers(ops1, hs1_ip, total_servers, md5_password,
                    key_password, step):
    step("Configure max NTP servers")
    for counter in range(1, total_servers + 1):
        password = md5_password.format(counter)
        set_ntp_authentication_keys(ops1, counter, password)
        set_ntp_server_with_key(ops1, hs1_ip.format(counter), counter)

        key_password[counter] = password


# Function that changes the preferred NTP server
def set_ntp_server_prefer(ops1, ip_address):
    with ops1.libs.vtysh.Configure() as ctx:
        ctx.ntp_server_prefer(ip_address)


# Function that checks if NTP authentication-keys are set correctly
def check_ntp_authentication_keys(ops1, key_password, step):
    step("Check NTP authentication keys")
    show_ntp_auth_keys_re = ops1.libs.vtysh.show_ntp_authentication_key()

    for key_id, md5_password in key_password.items():
        assert str(key_id) in show_ntp_auth_keys_re, (
            "KEY_ID not included in show ntp authentication-keys command, " +
            "Expected: {}".format(key_id)
        )

        md5_password_value = show_ntp_auth_keys_re[str(key_id)]['md5_password']
        assert md5_password_value == md5_password, (
            "MD5 password value is not the expected, " +
            "Expected: {}".format(md5_password)
        )


# Function that checks if NTP trusted keys are set correctly
def check_ntp_trusted_keys(ops1, key_password, step):
    step("Check NTP trusted keys")
    show_ntp_trusted_keys_re = ops1.libs.vtysh.show_ntp_trusted_keys()

    for key_id in key_password:
        assert str(key_id) in show_ntp_trusted_keys_re, (
            "KEY_ID not included in show NTP trusted-keys command, " +
            "Expected: {}".format(key_id)
        )


# Function that validates if switch is synchronized with NTP server
def validate_ntp_status(ops1):
    show_ntp_status_re = ops1.libs.vtysh.show_ntp_status()

    auth_status_value = show_ntp_status_re['authentication_status']
    assert auth_status_value == 'enabled', (
        "Authentication status is not the expected, Expected: enabled"
    )

    if 'server' in show_ntp_status_re:
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


@mark.timeout(800)
@mark.platform_incompatible(['docker'])
def test_authentication_enabled_keys(topology, step):
    """
    Connect max. NTP servers with authentication enabled and keys
    """
    ops1 = topology.get('ops1')
    ops2 = topology.get('ops2')
    hs1 = topology.get('hs1')

    assert ops1 is not None
    assert ops2 is not None
    assert hs1 is not None

    keys_passwords = {}

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
    set_host_ntpd(hs1, NTP_SERVERS, MD5_PASSWORD, MAX_NTP_SERVERS, step)

    # Connectivity test
    verify_connectivity_host(hs1, OPS_IP, 5, step)

    # Enable authentication
    set_ntp_authentication(ops1, step)

    # Configure NTP server profile with authentication-key
    set_ntp_servers(ops1, HS1_IP, MAX_NTP_SERVERS, MD5_PASSWORD,
                    keys_passwords, step)

    # Set last NTP server as preferred
    set_ntp_server_prefer(ops1, HS1_IP.format(MAX_NTP_SERVERS))

    # Check show NTP authentication-keys command
    check_ntp_authentication_keys(ops1, keys_passwords, step)

    # Check show NTP authentication-keys command
    check_ntp_trusted_keys(ops1, keys_passwords, step)

    # Check show commands with authentication enabled
    check_ntp_status_and_associations(ops1, TOTAL_TIMEOUT, TIMEOUT, step)
