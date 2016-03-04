#!/usr/bin/python

# Copyright (C) 2015 Hewlett Packard Enterprise Development LP
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import pytest
import re
from opstestfw import *
from opstestfw.switch.CLI import *
from opstestfw.switch import *
from opsvsi.docker import *
from opsvsi.opsvsitest import *

# The purpose of this test is to test that ntp config
# works as per the design and we receive the output as provided

DEFAULT_NTP_VERSION = '3'

class myTopo(Topo):
    def build(self, hsts=0, sws=1, **_opts):
        '''Function to build the topology of \
        one host and one switch'''
        self.hsts = hsts
        self.sws = sws
        # Add list of switches
        for s in irange(1, sws):
            switch = self.addSwitch('s%s' % s)

class ntpConfigTest(OpsVsiTest):
        def setupNet(self):
            self.net = Mininet(topo=myTopo(hsts=0, sws=1,
                                       hopts=self.getHostOpts(),
                                       sopts=self.getSwitchOpts()),
                                       switch=VsiOpenSwitch,
                                       host=Host,
                                       link=OpsVsiLink, controller=None,
                                       build=True)

        def testNtpAuthEnableDisableConfig(self):
            info('\n### === Authentication enable disable test START === ###')
            s1 = self.net.switches[0]
            s1.cmdCLI("configure terminal")
            s1.cmdCLI("ntp authentication enable")
            s1.cmdCLI("exit")
            dump = s1.cmdCLI("show ntp status")
            lines = dump.split('\n')
            count = 0
            for line in lines:
               if "NTP authentication is enabled" in line:
                  info('\n### Auth has been enabled as per show CLI - PASSED ###')
                  count = count + 1

            ''' Now check the running config '''
            dump = s1.cmdCLI("show running-config")
            lines = dump.split('\n')
            for line in lines:
               if "ntp authentication enable" in line:
                  info('\n### Auth has been enabled as per running-config - PASSED ###')
                  count = count + 1

            s1.cmdCLI("configure terminal")
            s1.cmdCLI("no ntp authentication enable")
            s1.cmdCLI("exit")
            dump = s1.cmdCLI("show ntp status")
            lines = dump.split('\n')
            for line in lines:
               if "NTP authentication is disabled" in line:
                  info('\n### Auth has been disabled as per show CLI - PASSED ###')
                  count = count + 1

            ''' Now check the running config '''
            count = count + 1
            dump = s1.cmdCLI("show running-config")
            lines = dump.split('\n')
            for line in lines:
               if "ntp authentication enable" in line:
                  error('\n### Auth has been enabled as per running-config - FAILED ###')
                  count = count - 1

            assert count == 4, \
                   error('\n### Authentication enable disable test FAILED ###')

            info('\n### Authentication enable disable test PASSED ###')
            info('\n### === Authentication enable disable test END === ###\n')

        def testNtpValidAuthKeyAdd(self):
            info('\n### === Valid Auth-Key addition test START === ###')
            s1 = self.net.switches[0]
            s1.cmdCLI("configure terminal")
            s1.cmdCLI("ntp authentication-key 10 md5 password10")
            s1.cmdCLI("exit")
            dump = s1.cmdCLI("show ntp authentication-keys")
            lines = dump.split('\n')
            count = 0
            for line in lines:
               if ("10" in line and "password10" in line):
                  info('\n### Valid auth-key present as per show CLI - PASSED ###')
                  count = count + 1

            ''' Now check the running config '''
            dump = s1.cmdCLI("show running-config")
            lines = dump.split('\n')
            for line in lines:
               if "ntp authentication-key 10 md5 password10" in line:
                  info('\n### Valid auth-key present in running-config - PASSED')
                  count = count + 1

            assert count == 2, \
                   error('\n### Valid auth-key addition test FAILED ###')

            info('\n### Valid auth-key addition test PASSED ###')
            info('\n### === Valid Auth-Key addition test END === ###\n')

        def testNtpValidAuthKeyDelete(self):
            info('\n### === Auth-Key deletion test START === ###')
            s1 = self.net.switches[0]
            s1.cmdCLI("configure terminal")
            s1.cmdCLI("no ntp authentication-key 10")
            s1.cmdCLI("exit")
            dump = s1.cmdCLI("show ntp authentication-keys")
            lines = dump.split('\n')
            count = 1
            for line in lines:
               if ("10" in line and "password10" in line):
                  info('\n### Deleted key still present as per show CLI')
                  count = count - 1

            ''' Now check the running config '''
            count = count + 1
            dump = s1.cmdCLI("show running-config")
            lines = dump.split('\n')
            for line in lines:
               if "ntp authentication-key 10 md5 password10" in line:
                  info('\n### auth-key found in running-config inspite of deleting it')
                  count = count - 1

            assert count == 2, \
                   error('\n### Valid auth-key deletion test FAILED ###')

            info('\n### Valid auth-key deletion test PASSED ###')
            info('\n### === Auth-Key deletion test END === ###\n')

        def testNtpInvalidAuthKeyAdd(self):
            info('\n### === Invalid Auth-Key addition test START === ###')
            s1 = self.net.switches[0]
            s1.cmdCLI("configure terminal")
            s1.cmdCLI("ntp authentication-key 0 md5 password0")
            s1.cmdCLI("exit")
            dump = s1.cmdCLI("show ntp authentication-keys")
            lines = dump.split('\n')
            count = 0
            count = count + 1
            for line in lines:
               if ("0" in line and "password0" in line):
                  error('\n### Invalid auth-key present as per show CLI - FAILED ###')
                  count = count - 1

            ''' Now check the running config '''
            count = count + 1
            dump = s1.cmdCLI("show running-config")
            lines = dump.split('\n')
            for line in lines:
               if "ntp authentication-key 0 md5 password0" in line:
                  error('\n### Invalid auth-key present in running-config - FAILED')
                  count = count - 1

            assert count == 2, \
                   error('\n### Invalid auth-key addition test FAILED ###')

            info('\n### Invalid auth-key addition test PASSED ###')
            info('\n### === Invalid Auth-Key addition test END === ###\n')

        def testNtpShortPwdAdd(self):
            info('\n### === Invalid (short) Auth-Key password addition test START === ###')
            s1 = self.net.switches[0]
            s1.cmdCLI("configure terminal")
            s1.cmdCLI("ntp authentication-key 2 md5 short")
            s1.cmdCLI("exit")
            dump = s1.cmdCLI("show ntp authentication-keys")
            lines = dump.split('\n')
            count = 0
            count = count + 1
            for line in lines:
               if ("2" in line and "short" in line):
                  error('\n### Invalid (short) auth-key password present as per show CLI - FAILED ###')
                  count = count - 1

            ''' Now check the running config '''
            count = count + 1
            dump = s1.cmdCLI("show running-config")
            lines = dump.split('\n')
            for line in lines:
               if "ntp authentication-key 2 md5 short" in line:
                  error('\n### Invalid (short) auth-key password present in running-config - FAILED')
                  count = count - 1

            assert count == 2, \
                   error('\n### Invalid (short) auth-key password addition test FAILED ###')

            info('\n### Invalid (short) auth-key password addition test PASSED ###')
            info('\n### === Invalid (short) Auth-Key password addition test END === ###\n')

        def testNtpTooLongPwdAdd(self):
            info('\n### === Invalid (too-long) Auth-Key password addition test START === ###')
            s1 = self.net.switches[0]
            s1.cmdCLI("configure terminal")
            s1.cmdCLI("ntp authentication-key 17 md5 longerthansixteen")
            s1.cmdCLI("exit")
            dump = s1.cmdCLI("show ntp authentication-keys")
            lines = dump.split('\n')
            count = 0
            count = count + 1
            for line in lines:
               if ("17" in line and "longerthansixteen" in line):
                  error('\n### Invalid (too-long) auth-key password present as per show CLI - FAILED ###')
                  count = count - 1

            ''' Now check the running config '''
            count = count + 1
            dump = s1.cmdCLI("show running-config")
            lines = dump.split('\n')
            for line in lines:
               if "ntp authentication-key 17 md5 longerthansixteen" in line:
                  error('\n### Invalid (too-long) auth-key password present in running-config - FAILED')
                  count = count - 1

            assert count == 2, \
                   error('\n### Invalid (too-long) auth-key password addition test FAILED ###')

            info('\n### Invalid (too-long) auth-key password addition test PASSED ###')
            info('\n### === Invalid (too-long) Auth-Key password addition test END === ###\n')

        def testNtpAddServerNoOptions(self):
            info('\n### === Server (with no options) addition test START === ###')
            s1 = self.net.switches[0]
            s1.cmdCLI("configure terminal")
            s1.cmdCLI("ntp server 1.1.1.1")
            s1.cmdCLI("exit")
            dump = s1.cmdCLI("show ntp associations")
            lines = dump.split('\n')
            count = 0
            for line in lines:
               if ("1.1.1.1" in line and DEFAULT_NTP_VERSION in line):
                  info('\n### Server (with no options) present as per show CLI - PASSED ###')
                  count = count + 1

            ''' Now check the running config '''
            dump = s1.cmdCLI("show running-config")
            lines = dump.split('\n')
            for line in lines:
               if ("ntp server 1.1.1.1" in line and DEFAULT_NTP_VERSION not in line):
                  info('\n### Server (with no options) present in running config - PASSED ###')
                  count = count + 1

            assert count == 2, \
                   error('\n### Server (with no options) addition test FAILED ###')

            info('\n### Server (with no options) addition test PASSED ###')
            info('\n### === Server (with no options) addition test END === ###\n')

        def testNtpAddServerPreferOption(self):
            info('\n### === Server (with prefer option) addition test START === ###')
            s1 = self.net.switches[0]
            s1.cmdCLI("configure terminal")
            s1.cmdCLI("ntp server 2.2.2.2 prefer")
            s1.cmdCLI("exit")
            dump = s1.cmdCLI("show ntp associations")
            lines = dump.split('\n')
            count = 0
            for line in lines:
               if ("2.2.2.2" in line and DEFAULT_NTP_VERSION in line):
                  info('\n### Server (with no options) present as per show CLI - PASSED ###')
                  count = count + 1

            ''' Now check the running config '''
            dump = s1.cmdCLI("show running-config")
            lines = dump.split('\n')
            for line in lines:
               if ("ntp server 2.2.2.2 prefer" in line and DEFAULT_NTP_VERSION not in line):
                  info('\n### Server (with prefer options) present in running config - PASSED ###')
                  count = count + 1

            assert count == 2, \
                   error('\n### Server (with prefer options) addition test FAILED ###')

            info('\n### Server (with prefer options) addition test PASSED ###')
            info('\n### === Server (with prefer option) addition test END === ###\n')

        def testNtpAddServerValidVersionOption(self):
            info('\n### === Server (with version option) addition test START === ###')
            s1 = self.net.switches[0]
            s1.cmdCLI("configure terminal")
            s1.cmdCLI("ntp server 3.3.3.3 version 4")
            s1.cmdCLI("exit")
            dump = s1.cmdCLI("show ntp associations")
            lines = dump.split('\n')
            count = 0
            for line in lines:
               if ("3.3.3.3" in line and "4" in line):
                  info('\n### Server (with version option) present as per show CLI - PASSED ###')
                  count = count + 1

            ''' Now check the running config '''
            dump = s1.cmdCLI("show running-config")
            lines = dump.split('\n')
            for line in lines:
               if ("ntp server 3.3.3.3 version 4" in line):
                  info('\n### Server (with version option) present in running config - PASSED ###')
                  count = count + 1

            assert count == 2, \
                   error('\n### Server (with version option) addition test FAILED ###')

            info('\n### Server (with version option) addition test PASSED ###')
            info('\n### === Server (with version option) addition test END === ###\n')

        def testNtpAddServerInvalidVersionOption(self):
            info('\n### === Server (with version option) addition test START === ###')
            s1 = self.net.switches[0]
            s1.cmdCLI("configure terminal")
            s1.cmdCLI("ntp server 4.4.4.4 version 5")
            s1.cmdCLI("exit")
            dump = s1.cmdCLI("show ntp associations")
            lines = dump.split('\n')
            count = 0
            count = count + 1
            for line in lines:
               if ("4.4.4.4" in line and "5" in line):
                  error('\n### Server (with invalid version option) present as per show CLI - FAILED ###')
                  count = count - 1

            ''' Now check the running config '''
            count = count + 1
            dump = s1.cmdCLI("show running-config")
            lines = dump.split('\n')
            for line in lines:
               if ("ntp server 4.4.4.4 version 5" in line):
                  error('\n### Server (with invalid version option) present in running config - FAILED ###')
                  count = count - 1

            assert count == 2, \
                   error('\n### Server (with invalid version option) addition test FAILED ###')

            info('\n### Server (with invalid version option) addition test PASSED ###')
            info('\n### === Server (with invalid version option) addition test END === ###\n')

        def testNtpAddServerWithFQDN(self):
            info('\n### === Server (with FQDN) addition test START === ###')
            s1 = self.net.switches[0]
            s1.cmdCLI("configure terminal")
            s1.cmdCLI("ntp server abc.789.com")
            s1.cmdCLI("exit")
            dump = s1.cmdCLI("show ntp associations")
            lines = dump.split('\n')
            count = 0
            for line in lines:
               if ("abc.789.com" in line and DEFAULT_NTP_VERSION in line):
                  info('\n### Server (with FQDN) present as per show CLI - PASSED ###')
                  count = count + 1

            ''' Now check the running config '''
            dump = s1.cmdCLI("show running-config")
            lines = dump.split('\n')
            for line in lines:
               if ("ntp server abc.789.com" in line and DEFAULT_NTP_VERSION not in line):
                  info('\n### Server (with FQDN) present in running config - PASSED ###')
                  count = count + 1

            assert count == 2, \
                   error('\n### Server (with FQDN) addition test FAILED ###')

            info('\n### Server (with FQDN) addition test PASSED ###')
            info('\n### === Server (with FQDN) addition test END === ###\n')

        def testNtpAddServerWithInvalidServerName(self):
            info('\n### === Server (with invalid server name) addition test START === ###')
            s1 = self.net.switches[0]
            s1.cmdCLI("configure terminal")

            ''' Ill-formatted IP addreses '''
            s1.cmdCLI("ntp server 4.4")
            s1.cmdCLI("ntp server 4.5.6.")
            s1.cmdCLI("ntp server 5.5.275.5")

            ''' Loopback, multicast,broadcast and experimental IP addresses '''
            s1.cmdCLI("ntp server 127.25.25.25")
            s1.cmdCLI("ntp server 230.25.25.25")
            s1.cmdCLI("ntp server 250.25.25.25")

            ''' IP addresses starting with 0 '''
            s1.cmdCLI("ntp server 0.1.1.1")

            s1.cmdCLI("exit")
            dump = s1.cmdCLI("show ntp associations")
            lines = dump.split('\n')
            count = 0
            count = count + 1
            for line in lines:
               if ("4.4" in line or "4.5.6." in line or "5.5.275.5" in line or "127.25.25.25" in line
                    or "230.25.25.25" in line or "250.25.25.25" in line or "0.1.1.1" in line):
                  error('\n### Server (with ill-formatted ) present as per show CLI - FAILED ###')
                  count = count - 1

            ''' Now check the running config '''
            count = count + 1
            dump = s1.cmdCLI("show running-config")
            lines = dump.split('\n')
            for line in lines:
               if ("ntp server 4.4" in line or "ntp server 4.5.6." in line or "ntp server 5.5.275.5" in line
                    or "ntp server 127.25.25.25" in line or "ntp server 230.25.25.25" in line
                    or "ntp server 250.25.25.25" in line or "0.1.1.1" in line):
                  error('\n### Server (with ill-formatted) present in running config - FAILED ###')
                  count = count - 1


            assert count == 2, \
                   error('\n### Server (with invalid server name) addition test FAILED ###')

            info('\n### Server (with invalid server name) addition test PASSED ###')
            info('\n### === Server (with invalid server name) addition test END === ###\n')

        def testNtpAddServerKeyidOption(self):
            info('\n### === Server (with key-id option) addition test START === ###')
            s1 = self.net.switches[0]
            s1.cmdCLI("configure terminal")
            s1.cmdCLI("ntp authentication-key 10 md5 password10")
            s1.cmdCLI("ntp server 4.4.4.4 key-id 10")
            s1.cmdCLI("exit")
            dump = s1.cmdCLI("show ntp associations")
            lines = dump.split('\n')
            count = 0
            for line in lines:
               if ("4.4.4.4" in line and "10" in line):
                  info('\n### Server (with key-id option) present as per show CLI - PASSED ###')
                  count = count + 1

            ''' Now check the running config '''
            dump = s1.cmdCLI("show running-config")
            lines = dump.split('\n')
            for line in lines:
               if ("ntp server 4.4.4.4 key-id 10" in line):
                  info('\n### Server (with key-id option) present in running config - PASSED ###')
                  count = count + 1

            assert count == 2, \
                   error('\n### Server (with key-id option) addition test FAILED ###')

            info('\n### Server (with key-id option) addition test PASSED ###')
            info('\n### === Server (with key-id option) addition test END === ###\n')

        def testNtpAddServerAllOptions(self):
            info('\n### === Server (with all options) addition test START === ###')
            s1 = self.net.switches[0]
            s1.cmdCLI("configure terminal")
            s1.cmdCLI("ntp authentication-key 11 md5 password11")
            s1.cmdCLI("ntp server 5.5.5.5 key-id 11 version 4 prefer")
            s1.cmdCLI("exit")
            dump = s1.cmdCLI("show ntp associations")
            lines = dump.split('\n')
            count = 0
            for line in lines:
               if ("5.5.5.5" in line and "11" in line and "4" in line):
                  info('\n### Server (with all options) present as per show CLI - PASSED ###')
                  count = count + 1

            ''' Now check the running config '''
            dump = s1.cmdCLI("show running-config")
            lines = dump.split('\n')
            for line in lines:
               if ("ntp server 5.5.5.5 key-id 11 version 4 prefer" in line):
                  info('\n### Server (with all options) present in running config - PASSED ###')
                  count = count + 1

            assert count == 2, \
                   error('\n### Server (with all options) addition test FAILED ###')

            info('\n### Server (with all options) addition test PASSED ###')
            info('\n### === Server (with all options) addition test END === ###\n')

        def testNtpAddMoreThan8Servers(self):
            info('\n### === Addition of more than 8 servers test START === ###')
            moreThan8ServersError = "Maximum number of configurable NTP server limit has been reached";
            s1 = self.net.switches[0]
            s1.cmdCLI("configure terminal")
            s1.cmdCLI("ntp server 6.6.6.6")
            s1.cmdCLI("ntp server 7.7.7.7")
            s1.cmdCLI("ntp server 8.8.8.8")

            dump = s1.cmdCLI("ntp server 9.9.9.9")
            assert moreThan8ServersError in dump, \
                   error ('\n### More than 8 server addition test FAILED ###')

            s1.cmdCLI("exit")

            dump = s1.cmdCLI("show ntp associations")
            lines = dump.split('\n')
            count = 0
            for line in lines:
               if ("6.6.6.6" in line or "7.7.7.7" in line or "8.8.8.8" in line):
                  count = count + 1
               if ("9.9.9.9" in line):
                  count = count - 1

            ''' Now check the running config '''
            dump = s1.cmdCLI("show running-config")
            lines = dump.split('\n')
            for line in lines:
               if ("ntp server 6.6.6.6" in line or "ntp server 7.7.7.7" in line or "ntp server 8.8.8.8" in line):
                  count = count + 1
               if ("ntp server 9.9.9.9" in line):
                  count = count - 1

            assert count == 6, \
                   error('\n### === Addition of more than 8 servers test FAILED === ###')

            info('\n### === Addition of more than 8 servers test PASSED === ###')
            info('\n### === Addition of more than 8 servers test END === ###')

        def testNtpDelServer(self):
            info('\n### === Server deletion test START === ###')
            s1 = self.net.switches[0]
            s1.cmdCLI("configure terminal")
            s1.cmdCLI("no ntp server 8.8.8.8")
            s1.cmdCLI("exit")
            dump = s1.cmdCLI("show ntp associations")
            lines = dump.split('\n')
            count = 0
            count = count + 1
            for line in lines:
               if ("8.8.8.8" in line):
                  error('\n### Server still present as per show CLI - FAILED ###')
                  count = count - 1

            ''' Now check the running config '''
            count = count + 1
            dump = s1.cmdCLI("show running-config")
            lines = dump.split('\n')
            for line in lines:
               if ("ntp server 8.8.8.8" in line):
                  error('\n### Server still present in running config - FAILED ###')
                  count = count - 1

            assert count == 2, \
                   error('\n### Server deletion test FAILED ###')

            info('\n### Server deletion test PASSED ###')
            info('\n### === Server deletion test END === ###\n')

        def testNtpAddServerWithLongServerName(self):
            info('\n### === Server (with long server name) addition test START === ###')
            s1 = self.net.switches[0]
            s1.cmdCLI("configure terminal")

            ''' Long server name '''
            s1.cmdCLI("ntp server 1.cr.pool.ntp.org version 4 prefer")
            s1.cmdCLI("ntp server abcdefghijklmnopqrstuvwxyz")
            s1.cmdCLI("ntp server 5.5.275.5")

            ''' Short server name '''
            s1.cmdCLI("ntp server ab")

            s1.cmdCLI("exit")
            dump = s1.cmdCLI("show ntp associations")
            lines = dump.split('\n')
            max_len = len(lines[1])
            count = 0
            for line in lines:
                if (len(line) > max_len):
                    count = count + 1

            assert count == 0, \
                   error('\n###  Server (with long server name) addition test FAILED ###')

            info('\n### Server (with long server name) addition test PASSED ###')
            info('\n### === Server (with long server name) addition test END === ###\n')

class TestNtpConfig:

        def setup(self):
            pass

        def teardown(self):
            pass

        def setup_class(cls):
            TestNtpConfig.ntpConfigTest = ntpConfigTest()

        def teardown_class(cls):
            # Stop the Docker containers, and mininet topology
            TestNtpConfig.ntpConfigTest.net.stop()

        def __del__(self):
            del self.ntpConfigTest

        def testNtpAuthEnableDisable(self):
            self.ntpConfigTest.testNtpAuthEnableDisableConfig()

        def testNtpValidAuthKeyAdd(self):
            self.ntpConfigTest.testNtpValidAuthKeyAdd()

        def testNtpInvalidAuthKeyAdd(self):
            self.ntpConfigTest.testNtpInvalidAuthKeyAdd()

        def testNtpShortPwdAdd(self):
            self.ntpConfigTest.testNtpShortPwdAdd()

        def testNtpTooLongPwdAdd(self):
            self.ntpConfigTest.testNtpTooLongPwdAdd()

        def testNtpAddServerNoOptions(self):
            self.ntpConfigTest.testNtpAddServerNoOptions()

        def testNtpAddServerPreferOption(self):
            self.ntpConfigTest.testNtpAddServerPreferOption()

        def testNtpAddServerValidVersionOption(self):
            self.ntpConfigTest.testNtpAddServerValidVersionOption()

        def testNtpAddServerInvalidVersionOption(self):
            self.ntpConfigTest.testNtpAddServerInvalidVersionOption()

        def testNtpAddServerWithInvalidServerName(self):
            self.ntpConfigTest.testNtpAddServerWithInvalidServerName()

        def testNtpAddServerKeyidOption(self):
            self.ntpConfigTest.testNtpAddServerKeyidOption()

        def testNtpAddServerAllOptions(self):
            self.ntpConfigTest.testNtpAddServerAllOptions()

        def testNtpAddMoreThan8Servers(self):
            self.ntpConfigTest.testNtpAddMoreThan8Servers()

        def testNtpDelServer(self):
            self.ntpConfigTest.testNtpDelServer()

        def testNtpAddServerWithFQDN(self):
            self.ntpConfigTest.testNtpAddServerWithFQDN()

        def testNtpAddServerWithLongServerName(self):
            self.ntpConfigTest.testNtpAddServerWithLongServerName()
