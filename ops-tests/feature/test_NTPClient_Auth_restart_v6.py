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


from pytest import mark
from time import sleep


TOPOLOGY = """
# +--------+
# |        |
# |  ops1  |
# |        |
# +----^---+
#      |eth0
#      |
#      |eth0
# +----+---+
# |        |
# |  hs1   |
# |        |
# +--------+

# Nodes
[type=openswitch name="OpenSwitch 1"] ops1
[type=oobmhost name="Host 1" image="openswitch/ubuntu_ntp"] hs1

# Links
[force_name=oobm] ops1:eth0
ops1:eth0 -- hs1:eth0
"""

HS1_IP_MASK = '2013:cdba:1002:1304:4001:2005:3257:1/64'
OPS1_IP_MASK = '2013:cdba:1002:1304:4001:2005:3257:2/64'
KEY_ID = "55"
MD5_PASSWORD = "secretpassword"
TOTAL_TIMEOUT = 1020
TIMEOUT = 5
packets = 5


def set_switch_mgmt_interface(ops1, ops1_ip_mask, step):
    step("Configure switch interface mgmt IP address")
    with ops1.libs.vtysh.ConfigInterfaceMgmt() as ctx:
        ctx.ip_static(ops1_ip_mask)


def set_host_config(hs1, step):
    out = hs1.libs.ip.interface('eth0', addr=HS1_IP_MASK, up=True)
    print(out)
    hs1("echo \"authenticate yes\" >> /etc/ntp.conf")
    hs1("service ntp restart")


def verify_connectivity_host(hs1, ops1, packets, step):
    step("Test ping between host and DUT")
    ping = hs1.libs.ping.ping(packets, OPS1_IP_MASK.split('/')[0])
    assert ping['received'] > 3, (
        "Total of received packets is below the expected, " +
        "Expected: {}".format(packets)
    )


def set_ntp_authentication(ops1, step):
    step("Enable NTP authentication")
    with ops1.libs.vtysh.Configure() as ctx:
        ctx.ntp_authentication_enable()


def set_ntp_authentication_keys(ops1, key_id, md5_password):
    print("Add NTP authentication key: {}".format(key_id))
    with ops1.libs.vtysh.Configure() as ctx:
        ctx.ntp_authentication_key_md5(key_id, md5_password)
        ctx.ntp_trusted_key(key_id)


def set_ntp_server_with_key(ops1, server, key_id):
    print("Add NTP server {} with authentication key {}".
          format(server, key_id))
    with ops1.libs.vtysh.Configure() as ctx:
        ctx.ntp_server_key_id(server, key_id)


def restart_ntp_daemon(ops1, step):
    step("### Verifying the NTPD restartability ###")
    ops1("systemctl restart ops-ntpd", shell='bash')
    sleep(30)
    out = ops1("ps -ef | grep ntpd", shell='bash')
    assert'ntpd -I eth0 -c' in out, "### OPS-NTPD Daemon restart failed ###\n"


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


def validate_ntp_status(ops1):
    # out = ops1("show ntp status")
    out = ops1.libs.vtysh.show_ntp_status()
    print(out)
    assert out['authentication_status'] == 'enabled', (
        "Authentication status is not the expected, Expected: enabled"
    )

    if 'server' in out:
        return True
    else:
        return False


def validate_ntp_associations(ops1):
    show_ntp_assoc_re = ops1.libs.vtysh.show_ntp_associations()
    print(show_ntp_assoc_re)
    for key in show_ntp_assoc_re.keys():
        code = show_ntp_assoc_re[key]['code']
        if code == '*':
            return True
    return False


@mark.timeout(800)
def test_authentication_enabled_with_restart(topology, step):
    """
    Connect to NTP server with authentication enabled
    """
    ops1 = topology.get('ops1')
    hs1 = topology.get('hs1')

    assert ops1 is not None
    assert hs1 is not None

    set_switch_mgmt_interface(ops1, OPS1_IP_MASK, step)

    set_host_config(hs1, step)

    verify_connectivity_host(hs1, ops1, packets, step)

    set_ntp_authentication(ops1, step)

    set_ntp_authentication_keys(ops1, KEY_ID, MD5_PASSWORD)

    set_ntp_server_with_key(ops1, HS1_IP_MASK.split('/')[0], KEY_ID)

    check_ntp_status_and_associations(ops1, TOTAL_TIMEOUT, TIMEOUT, step)

    restart_ntp_daemon(ops1, step)

    check_ntp_status_and_associations(ops1, TOTAL_TIMEOUT, TIMEOUT, step)
