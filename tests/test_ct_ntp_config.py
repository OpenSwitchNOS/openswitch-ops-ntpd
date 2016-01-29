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

SERVER1 = "1.1.1.1"
SERVER2 = "2.2.2.2"
SERVER3 = "3.3.3.3"
SERVER4 = "4.4.4.4"
keyid = '12'
VER = '3'

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

	def ntpConfig(self):
            info('\n### NTP CTs started ###\n')
            info('\n### Configure different ntp associations ###\n')
	    s1 = self.net.switches[0]
            s1.cmdCLI("configure terminal")
            s1.cmdCLI("ntp server %s" % SERVER1)
            s1.cmdCLI("ntp server %s" % SERVER2)
            s1.cmdCLI("ntp server %s prefer" % SERVER3)
            s1.cmdCLI("ntp server %s version 3" % SERVER4)
            s1.cmdCLI("exit")

        def testNtpAuthEnableDisableConfig(self):
            info('\n### Authentication enable disable test START ###\n')
            s1 = self.net.switches[0]
            s1.cmdCLI("configure terminal")
            s1.cmdCLI("ntp authentication enable")
            s1.cmdCLI("exit")
            dump = s1.cmdCLI("show ntp status")
            lines = dump.split('\n')
            count = 0
            for line in lines:
               if "NTP Authentication has been enabled" in line:
                  info('\n### authentication has been enabled as per "show ntp status" ###\n')
                  count = count + 1

            ''' Now check the running config '''
            dump = s1.cmdCLI("show running-config")
            lines = dump.split('\n')
            for line in lines:
               if "ntp authentication enable" in line:
                  info('\n### NTP authentication has been enabled as per "show running-config" ###\n')
                  count = count + 1

            s1.cmdCLI("configure terminal")
            s1.cmdCLI("no ntp authentication enable")
            s1.cmdCLI("exit")
            dump = s1.cmdCLI("show ntp status")
            lines = dump.split('\n')
            for line in lines:
               if "NTP Authentication has been disabled" in line:
                  info('\n### authentication has been disabled as per "show ntp status" ###\n')
                  count = count + 1

            ''' Now check the running config '''
            sleep(2)
            count = count + 1
            dump = s1.cmdCLI("show running-config")
            lines = dump.split('\n')
            for line in lines:
               info("%s" % line)
               if "ntp authentication enable" in line:
                  info('\n### enable authentication test failed in show running-config verification\n')
                  count = count - 1

            assert count == 4, \
                   info('\n### Authentication config: Tests failed!!###\n')

        def testNtpValidAuthKeyAdd(self):
            info('\n### Valid Auth-Key addition test ###\n')
            s1 = self.net.switches[0]
            s1.cmdCLI("configure terminal")
            s1.cmdCLI("ntp authentication-key 10 md5 password10")
            s1.cmdCLI("exit")
            dump = s1.cmdCLI("show ntp authentication-keys")
            lines = dump.split('\n')
            count = 0
            for line in lines:
               info("%s\n" % line)
               if ("10" in line and "password10" in line):
                  info('\n### Valid auth-key found in output of the show CLI\n')
                  count = count + 1

            ''' Now check the running config '''
            dump = s1.cmdCLI("show running-config")
            lines = dump.split('\n')
            for line in lines:
               if "ntp authentication-key 10 md5 password10" in line:
                  info('\n### Valid auth-key found in running-config\n')
                  count = count + 1

            assert count == 2, \
                   info('\n### Valid auth-key addition test FAILED!! ###\n')

            info('\n### Valid auth-key addition test PASSED!! ###\n')

        def testNtpValidAuthKeyDelete(self):
            info('\n### Auth-Key deletion test ###\n')
            s1 = self.net.switches[0]
            s1.cmdCLI("configure terminal")
            s1.cmdCLI("no ntp authentication-key 10")
            s1.cmdCLI("exit")
            dump = s1.cmdCLI("show ntp authentication-keys")
            lines = dump.split('\n')
            count = 1
            for line in lines:
               info("%s\n" % line)
               if ("10" in line and "password10" in line):
                  info('\n### Deleted key still found in OVSDB\n')
                  count = count - 1

            ''' Now check the running config '''
            count = count + 1
            dump = s1.cmdCLI("show running-config")
            lines = dump.split('\n')
            for line in lines:
               if "ntp authentication-key 10 md5 password10" in line:
                  info('\n### auth-key found in running-config inspite of deleting it\n')
                  count = count - 1

            assert count == 2, \
                   info('\n### Valid auth-key deletion test FAILED!!###\n')

            info('\n### Valid auth-key deletion test PASSED!!###\n')

        def testNtpAssociationsConfig(self):
            info('\n### Verify ntp associations table ###\n')
            s1 = self.net.switches[0]
            #parse the ntp associations command
            dump = s1.cmdCLI("show ntp associations")
            lines = dump.split('\n')
            count = 0
            for line in lines:
               if SERVER1 in line:
                  info("###found %s in db###\n"% SERVER1)
                  count = count + 1

               if SERVER2 in line:
                  info('###found %s in db###\n'% SERVER2)
                  count = count + 1

               if SERVER3 in line:
                  info('###found %s in db###\n'% SERVER3)
                  count = count + 1

               if (SERVER4 in line and VER in line):
                  info('###found %s and appropriate version in db###\n'% SERVER4)
                  count = count + 1

            assert count == 4, \
                   info('tests are not successful\n')

            info('\n### testNtpAssociationsConfig: Test Passed ###\n')

        def testUnconfigureNtpServers(self):
            info('\n### checking unconfigure commands ###\n')
            s1 = self.net.switches[0]
            s1.cmdCLI("configure terminal")
            s1.cmdCLI("no ntp server %s" % SERVER1)
            s1.cmdCLI("exit")
            dump = s1.cmdCLI("show ntp associations")
            count = 0
            lines = dump.split('\n')
            for line in lines:
               if SERVER1 in line:
                  info('\n### no ntp server tests unsuccessful \n')
                  conut = count + 1

            assert count == 0, \
                  info('\n### no ntp server tests unsuccessful : Test failed### \n')

            info('\n### no ntp server tests unsuccessful : Test passed### \n')


class TestNtpConfig:

	def setup(self):
            pass

        def teardown(self):
            pass

        def setup_class(cls):
            TestNtpConfig.ntpConfigTest = ntpConfigTest()

        def teardown_class(cls):
            # Stop the Docker containers, and
            # mininet topology
            TestNtpConfig.ntpConfigTest.net.stop()

        def __del__(self):
            del self.ntpConfigTest

        def testNtpFull(self):
            info('\n########## Test NTP configuration ##########\n')
            self.ntpConfigTest.ntpConfig()
            self.ntpConfigTest.testNtpAuthEnableDisableConfig()
            self.ntpConfigTest.testNtpValidAuthKeyAdd()
            self.ntpConfigTest.testNtpAssociationsConfig()
            self.ntpConfigTest.testUnconfigureNtpServers()
            info('\n########## End of test NTP configuration configuration ##########\n')
