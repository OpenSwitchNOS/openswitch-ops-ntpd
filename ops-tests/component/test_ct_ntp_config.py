# (c) Copyright 2016 Hewlett Packard Enterprise Development LP
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


TOPOLOGY = """
#
# +--------+
# |  ops1  |
# +--------+
#

# Nodes
[type=openswitch name="Switch 1"] ops1
"""


default_ntp_version = '3'


def ntpauthenabledisableconfig(dut, step):
    step('\n### === authentication enable disable test start === ###')
    dut("configure terminal")
    dut("ntp authentication enable")
    dut("end")
    dump = dut("show ntp status")
    lines = dump.splitlines()
    count = 0
    for line in lines:
        if "ntp authentication is enabled" in line:
            step('\n### auth has been enabled as per show cli - passed ###')
            count = count + 1

    ''' now check the running config '''
    dump = dut("show running-config")
    lines = dump.splitlines()
    for line in lines:
        if "ntp authentication enable" in line:
            step('\n### auth has been enabled as per running-config - '
                 'passed ###')
            count = count + 1

    dut("configure terminal")
    dut("no ntp authentication enable")
    dut("end")
    dump = dut("show ntp status")
    lines = dump.splitlines()
    for line in lines:
        if "ntp authentication is disabled" in line:
            step('\n### auth has been disabled as per show cli - passed ###')
            count = count + 1

    ''' now check the running config '''
    count = count + 1
    dump = dut("show running-config")
    lines = dump.splitlines()
    for line in lines:
        if "ntp authentication enable" in line:
            print('\n### auth has been enabled as per running-config - '
                  'failed ###')
            count = count - 1

    assert (count == 4,
            print('\n### authentication enable disable test failed ###'))

    step('\n### authentication enable disable test passed ###')
    step('\n### === authentication enable disable test end === ###\n')


def ntpvalidauthkeyadd(dut, step):
    step('\n### === valid auth-key addition test start === ###')
    dut("configure terminal")
    dut("ntp authentication-key 10 md5 password10")
    dut("end")
    dump = dut("show ntp authentication-keys")
    lines = dump.splitlines()
    count = 0
    for line in lines:
        if ("10" in line and "password10" in line):
            step('\n### valid auth-key present as per show cli - passed ###')
            count = count + 1

    ''' now check the running config '''
    dump = dut("show running-config")
    lines = dump.splitlines()
    for line in lines:
        if "ntp authentication-key 10 md5 password10" in line:
            step('\n### valid auth-key present in running-config - passed')
            count = count + 1

    assert (count == 2,
            print('\n### valid auth-key addition test failed ###'))

    step('\n### valid auth-key addition test passed ###')
    step('\n### === valid auth-key addition test end === ###\n')


def ntpvalidauthkeydelete(dut, step):
    step('\n### === auth-key deletion test start === ###')
    dut("configure terminal")
    dut("no ntp authentication-key 10")
    dut("end")
    dump = dut("show ntp authentication-keys")
    lines = dump.splitlines()
    count = 1
    for line in lines:
        if ("10" in line and "password10" in line):
            step('\n### deleted key still present as per show cli')
            count = count - 1

    ''' now check the running config '''
    count = count + 1
    dump = dut("show running-config")
    lines = dump.splitlines()
    for line in lines:
        if "ntp authentication-key 10 md5 password10" in line:
            step('\n### auth-key found in running-config inspite of '
                 'deleting it')
            count = count - 1

    assert (count == 2,
            print('\n### valid auth-key deletion test failed ###'))

    step('\n### valid auth-key deletion test passed ###')
    step('\n### === auth-key deletion test end === ###\n')


def ntpinvalidauthkeyadd(dut, step):
    step('\n### === invalid auth-key addition test start === ###')
    dut("configure terminal")
    dut("ntp authentication-key 0 md5 password0")
    dut("end")
    dump = dut("show ntp authentication-keys")
    lines = dump.splitlines()
    count = 0
    count = count + 1
    for line in lines:
        if ("0" in line and "password0" in line):
            print('\n### invalid auth-key present as per show cli - '
                  'failed ###')
            count = count - 1

    ''' now check the running config '''
    count = count + 1
    dump = dut("show running-config")
    lines = dump.splitlines()
    for line in lines:
        if "ntp authentication-key 0 md5 password0" in line:
            print('\n### invalid auth-key present in running-config - failed')
            count = count - 1

    assert (count == 2,
            print('\n### invalid auth-key addition test failed ###'))

    step('\n### invalid auth-key addition test passed ###')
    step('\n### === invalid auth-key addition test end === ###\n')


def ntpshortpwdadd(dut, step):
    step('\n### === invalid (short) auth-key password addition test start ==='
         ' ###')
    dut("configure terminal")
    dut("ntp authentication-key 2 md5 short")
    dut("end")
    dump = dut("show ntp authentication-keys")
    lines = dump.splitlines()
    count = 0
    count = count + 1
    for line in lines:
        if ("2" in line and "short" in line):
            print('\n### invalid (short) auth-key password present as per '
                  'show cli - failed ###')
            count = count - 1

    ''' now check the running config '''
    count = count + 1
    dump = dut("show running-config")
    lines = dump.splitlines()
    for line in lines:
        if "ntp authentication-key 2 md5 short" in line:
            print('\n### invalid (short) auth-key password present in '
                  'running-config - failed')
            count = count - 1

    assert (count == 2,
            print('\n### invalid (short) auth-key password addition test '
                  'failed ###'))

    step('\n### invalid (short) auth-key password addition test passed ###')
    step('\n### === invalid (short) auth-key password addition test end ==='
         ' ###\n')


def ntptoolongpwdadd(dut, step):
    step('\n### === invalid (too-long) auth-key password addition test start '
         '=== ###')
    dut("configure terminal")
    dut("ntp authentication-key 17 md5 longerthansixteen")
    dut("end")
    dump = dut("show ntp authentication-keys")
    lines = dump.splitlines()
    count = 0
    count = count + 1
    for line in lines:
        if ("17" in line and "longerthansixteen" in line):
            print('\n### invalid (too-long) auth-key password present as per '
                  'show cli - failed ###')
            count = count - 1

    ''' now check the running config '''
    count = count + 1
    dump = dut("show running-config")
    lines = dump.splitlines()
    for line in lines:
        if "ntp authentication-key 17 md5 longerthansixteen" in line:
            print('\n### invalid (too-long) auth-key password present in '
                  'running-config - failed')
            count = count - 1

    assert (count == 2,
            print('\n### invalid (too-long) auth-key password addition test'
                  ' failed ###'))

    step('\n### invalid (too-long) auth-key password addition test passed '
         '###')
    step('\n### === invalid (too-long) auth-key password addition test end '
         '=== ###\n')


def ntpaddservernooptions(dut, step):
    step('\n### === server (with no options) addition test start === ###')
    dut("configure terminal")
    dut("ntp server 1.1.1.1")
    dut("end")
    dump = dut("show ntp associations")
    lines = dump.splitlines()
    count = 0
    for line in lines:
        if ("1.1.1.1" in line and default_ntp_version in line):
            step('\n### server (with no options) present as per show cli - '
                 'passed ###')
            count = count + 1

    ''' now check the running config '''
    dump = dut("show running-config")
    lines = dump.splitlines()
    for line in lines:
        if ("ntp server 1.1.1.1" in line and default_ntp_version not in line):
            step('\n### server (with no options) present in running config - '
                 'passed ###')
            count = count + 1

    assert (count == 2,
            print('\n### server (with no options) addition test failed ###'))

    step('\n### server (with no options) addition test passed ###')
    step('\n### === server (with no options) addition test end === ###\n')


def ntpaddserverpreferoption(dut, step):
    step('\n### === server (with prefer option) addition test start === ###')
    dut("configure terminal")
    dut("ntp server 2.2.2.2 prefer")
    dut("end")
    dump = dut("show ntp associations")
    lines = dump.splitlines()
    count = 0
    for line in lines:
        if ("2.2.2.2" in line and default_ntp_version in line):
            step('\n### server (with no options) present as per show cli - '
                 'passed ###')
            count = count + 1

    ''' now check the running config '''
    dump = dut("show running-config")
    lines = dump.splitlines()
    for line in lines:
        if ("ntp server 2.2.2.2 prefer" in line and
           default_ntp_version not in line):
            step('\n### server (with prefer options) present in running '
                 'config - passed ###')
            count = count + 1

    assert (count == 2,
            print('\n### server (with prefer options) addition test failed '
                  '###'))

    step('\n### server (with prefer options) addition test passed ###')
    step('\n### === server (with prefer option) addition test end === ###\n')


def ntpaddservervalidversionoption(dut, step):
    step('\n### === server (with version option) addition test start === ###')
    dut("configure terminal")
    dut("ntp server 3.3.3.3 version 4")
    dut("end")
    dump = dut("show ntp associations")
    lines = dump.splitlines()
    count = 0
    for line in lines:
        if ("3.3.3.3" in line and "4" in line):
            step('\n### server (with version option) present as per show cli '
                 '- passed ###')
            count = count + 1

    ''' now check the running config '''
    dump = dut("show running-config")
    lines = dump.splitlines()
    for line in lines:
        if ("ntp server 3.3.3.3 version 4" in line):
            step('\n### server (with version option) present in running '
                 'config - passed ###')
            count = count + 1

    assert (count == 2,
            print('\n### server (with version option) addition test failed'
                  ' ###'))

    step('\n### server (with version option) addition test passed ###')
    step('\n### === server (with version option) addition test end === ###\n')


def ntpaddserverinvalidversionoption(dut, step):
    step('\n### === server (with version option) addition test start === ###')
    dut("configure terminal")
    dut("ntp server 4.4.4.4 version 5")
    dut("end")
    dump = dut("show ntp associations")
    lines = dump.splitlines()
    count = 0
    count = count + 1
    for line in lines:
        if ("4.4.4.4" in line and "5" in line):
            print('\n### server (with invalid version option) present as per '
                  'show cli - failed ###')
            count = count - 1

    ''' now check the running config '''
    count = count + 1
    dump = dut("show running-config")
    lines = dump.splitlines()
    for line in lines:
        if ("ntp server 4.4.4.4 version 5" in line):
            print('\n### server (with invalid version option) present in '
                  'running config - failed ###')
            count = count - 1

    assert (count == 2,
            print('\n### server (with invalid version option) addition test'
                  ' failed ###'))

    step('\n### server (with invalid version option) addition test passed '
         '###')
    step('\n### === server (with invalid version option) addition test end '
         '=== ###\n')


def ntpaddserverwithfqdn(dut, step):
    step('\n### === server (with fqdn) addition test start === ###')
    dut("configure terminal")
    dut("ntp server abc.789.com")
    dut("end")
    dump = dut("show ntp associations")
    lines = dump.splitlines()
    count = 0
    for line in lines:
        if ("abc.789.com" in line and default_ntp_version in line):
            step('\n### server (with fqdn) present as per show cli - passed '
                 '###')
            count = count + 1

    ''' now check the running config '''
    dump = dut("show running-config")
    lines = dump.splitlines()
    for line in lines:
        if ("ntp server abc.789.com" in line and
           default_ntp_version not in line):
            step('\n### server (with fqdn) present in running config - passed'
                 ' ###')
            count = count + 1

    assert (count == 2,
            print('\n### server (with fqdn) addition test failed ###'))

    step('\n### server (with fqdn) addition test passed ###')
    step('\n### === server (with fqdn) addition test end === ###\n')


def ntpaddserverwithinvalidservername(dut, step):
    step('\n### === server (with invalid server name) addition test start '
         '=== ###')
    dut("configure terminal")

    ''' ill-formatted ip addreses '''
    dut("ntp server 4.4")
    dut("ntp server 4.5.6.")
    dut("ntp server 5.5.275.5")

    ''' loopback, multicast,broadcast and experimental ip addresses '''
    dut("ntp server 127.25.25.25")
    dut("ntp server 230.25.25.25")
    dut("ntp server 250.25.25.25")

    ''' ip addresses starting with 0 '''
    dut("ntp server 0.1.1.1")

    dut("end")
    dump = dut("show ntp associations")
    lines = dump.splitlines()
    count = 0
    count = count + 1
    for line in lines:
        if (
            "4.4" in line or "4.5.6." in line or "5.5.275.5" in line or
            "127.25.25.25" in line or "230.25.25.25" in line or
            "250.25.25.25" in line or "0.1.1.1" in line
        ):
            print('\n### server (with ill-formatted ) present as per show '
                  'cli - failed ###')
            count = count - 1

    ''' now check the running config '''
    count = count + 1
    dump = dut("show running-config")
    lines = dump.splitlines()
    for line in lines:
        if (
            "ntp server 4.4" in line or "ntp server 4.5.6." in line or
            "ntp server 5.5.275.5" in line or
            "ntp server 127.25.25.25" in line or
            "ntp server 230.25.25.25" in line or
            "ntp server 250.25.25.25" in line or "0.1.1.1" in line
        ):
            print('\n### server (with ill-formatted) present in running '
                  'config - failed ###')
            count = count - 1

    assert (count == 2,
            print('\n### server (with invalid server name) addition test '
                  'failed ###'))

    step('\n### server (with invalid server name) addition test passed ###')
    step('\n### === server (with invalid server name) addition test end ==='
         ' ###\n')


def ntpaddserverkeyidoption(dut, step):
    step('\n### === server (with key-id option) addition test start === ###')
    dut("configure terminal")
    dut("ntp authentication-key 10 md5 password10")
    dut("ntp server 4.4.4.4 key-id 10")
    dut("end")
    dump = dut("show ntp associations")
    lines = dump.splitlines()
    count = 0
    for line in lines:
        if ("4.4.4.4" in line and "10" in line):
            step('\n### server (with key-id option) present as per show cli -'
                 ' passed ###')
            count = count + 1

    ''' now check the running config '''
    dump = dut("show running-config")
    lines = dump.splitlines()
    for line in lines:
        if ("ntp server 4.4.4.4 key-id 10" in line):
            step('\n### server (with key-id option) present in running config'
                 ' - passed ###')
            count = count + 1

    assert (count == 2,
            print('\n### server (with key-id option) addition test failed '
                  '###'))

    step('\n### server (with key-id option) addition test passed ###')
    step('\n### === server (with key-id option) addition test end === ###\n')


def ntpaddserveralloptions(dut, step):
    step('\n### === server (with all options) addition test start === ###')
    dut("configure terminal")
    dut("ntp authentication-key 11 md5 password11")
    dut("ntp server 5.5.5.5 key-id 11 version 4 prefer")
    dut("end")
    dump = dut("show ntp associations")
    lines = dump.splitlines()
    count = 0
    for line in lines:
        if ("5.5.5.5" in line and "11" in line and "4" in line):
            step('\n### server (with all options) present as per show cli - '
                 'passed ###')
            count = count + 1

    ''' now check the running config '''
    dump = dut("show running-config")
    lines = dump.splitlines()
    for line in lines:
        if ("ntp server 5.5.5.5 key-id 11 version 4 prefer" in line):
            step('\n### server (with all options) present in running config -'
                 ' passed ###')
            count = count + 1

    assert (count == 2,
            print('\n### server (with all options) addition test failed ###'))

    step('\n### server (with all options) addition test passed ###')
    step('\n### === server (with all options) addition test end === ###\n')


def ntpaddmorethan8servers(dut, step):
    step('\n### === addition of more than 8 servers test start === ###')
    morethan8serverserror = "maximum number of configurable ntp server limit "
    "has been reached"
    dut("configure terminal")
    dut("ntp server 6.6.6.6")
    dut("ntp server 7.7.7.7")
    dut("ntp server 8.8.8.8")

    dump = dut("ntp server 9.9.9.9")
    assert (morethan8serverserror in dump,
            print('\n### more than 8 server addition test failed ###'))

    dut("end")

    dump = dut("show ntp associations")
    lines = dump.splitlines()
    count = 0
    for line in lines:
        if ("6.6.6.6" in line or "7.7.7.7" in line or "8.8.8.8" in line):
            count = count + 1
        if ("9.9.9.9" in line):
            count = count - 1

    ''' now check the running config '''
    dump = dut("show running-config")
    lines = dump.splitlines()
    for line in lines:
        if ("ntp server 6.6.6.6" in line or "ntp server 7.7.7.7" in line or
           "ntp server 8.8.8.8" in line):
            count = count + 1
        if ("ntp server 9.9.9.9" in line):
            count = count - 1

    assert (count == 6,
            print('\n### === addition of more than 8 servers test failed ==='
                  ' ###'))

    step('\n### === addition of more than 8 servers test passed === ###')
    step('\n### === addition of more than 8 servers test end === ###')


def ntpmodify8thntpserver(dut, step):
    step('\n### === modifying version for the 8th ntp association test start '
         '=== ###')
    dut("configure terminal")
    dut("ntp server 8.8.8.8 version 4")
    dut("end")
    dump = dut("show ntp associations")
    lines = dump.splitlines()
    count = 0
    for line in lines:
        if ("8.8.8.8" in line):
            server_version = line.split()[3]
            if server_version != "4":
                print('\n### server configuration is not latest failed === '
                      '###')
                count = count - 1
            else:
                count = count + 1

    ''' check the running config '''
    dump = dut("show running-config")
    lines = dump.splitlines()
    for line in lines:
        if ("ntp server 8.8.8.8 version 4" in line):
            count = count + 1

    assert (count == 2,
            print('\n### === modifying version for the 8th ntp association '
                  'test failed === ###'))

    step('\n### === modifying version for the 8th ntp association test passed'
         ' === ###')
    step('\n### === modifying version for the 8th ntp association test end '
         '=== ###')


def ntpdelserver(dut, step):
    step('\n### === server deletion test start === ###')
    dut("configure terminal")
    dut("no ntp server 8.8.8.8")
    dut("end")
    dump = dut("show ntp associations")
    lines = dump.splitlines()
    count = 0
    count = count + 1
    for line in lines:
        if ("8.8.8.8" in line):
            print('\n### server still present as per show cli - failed ###')
            count = count - 1

    ''' now check the running config '''
    count = count + 1
    dump = dut("show running-config")
    lines = dump.splitlines()
    for line in lines:
        if ("ntp server 8.8.8.8" in line):
            print('\n### server still present in running config - failed ###')
            count = count - 1

    assert (count == 2,
            print('\n### server deletion test failed ###'))

    step('\n### server deletion test passed ###')
    step('\n### === server deletion test end === ###\n')


def ntpaddserverwithlongservername(dut, step):
    step('\n### === server (with long server name) addition test start === '
         '###')
    dut("configure terminal")

    ''' long server name '''
    dut("ntp server 1.cr.pool.ntp.org version 4 prefer")
    dut("ntp server abcdefghijklmnopqrstuvwxyz")
    dut("ntp server 192.168.101.125")

    ''' short server name '''
    dut("ntp server ab")

    dut("end")
    dump = dut("show ntp associations")
    lines = dump.splitlines()
    max_len = len(lines[1])
    count = 0
    for line in lines:
        if (len(line) > max_len):
            count = count + 1
        if (" 1.cr.pool.ntp.o " in line):
            count = count + 1
        if (" abcdefghijklmno " in line):
            count = count + 1
        if (" 192.168.101.125 " in line):
            count = count + 1
        if (" ab " in line):
            count = count + 1

    ''' clean up '''
    dut("configure terminal")
    dut("no ntp server 1.cr.pool.ntp.org")
    dut("no ntp server abcdefghijklmnopqrstuvwxyz")
    dut("no ntp server 192.168.101.125")
    dut("no ntp server ab")
    dut("exit")

    assert (count == 4,
            print('\n###  server (with long server name) addition test failed'
                  ' ###'))

    step('\n### server (with long server name) addition test passed ###')
    step('\n### === server (with long server name) addition test end === ###'
         '\n')


def test_ct_ntp_config(topology, step):
    ops1 = topology.get("ops1")
    assert ops1 is not None

    ntpauthenabledisableconfig(ops1, step)

    ntpvalidauthkeyadd(ops1, step)

    ntpinvalidauthkeyadd(ops1, step)

    ntpshortpwdadd(ops1, step)

    ntptoolongpwdadd(ops1, step)

    ntpaddservernooptions(ops1, step)

    ntpaddserverpreferoption(ops1, step)

    ntpaddservervalidversionoption(ops1, step)

    ntpaddserverinvalidversionoption(ops1, step)

    ntpaddserverwithlongservername(ops1, step)

    ntpaddserverwithinvalidservername(ops1, step)

    ntpaddserverkeyidoption(ops1, step)

    ntpaddserveralloptions(ops1, step)

    ntpaddmorethan8servers(ops1, step)

    ntpmodify8thntpserver(ops1, step)

    ntpdelserver(ops1, step)

    ntpaddserverwithfqdn(ops1, step)
