OPS-NTPD
========

What is ops-ntpd?
-----------------
ops-ntpd in OpenSwitch, is a python module to handle Network Time Protocol component in OpenSwitch. This component serves the following functions:
- It is an interaction layer between the NTP Daemon and the Openvswitch Database.
- Reads configuration from OVSDB and sends it to the NTP daemon.
- Reads NTP daemon status and populates with OVSDB.
- If configuration change in OVSDB warrants a daemon restart then it restarts the NTP daemon.

What daemon are you using for NTP?
-----------------------------------
We are using NTPsec repo to run NTP daemon.

What is the structure of the repository?
----------------------------------------
- ops-ntpd python source files are under this subdirectory.
- ./tests/ - contains all of the component tests of ops-ntpd based on the ops mininet framework.

What is the license?
--------------------
Apache 2.0 license. For more details refer to [COPYING](https://git.openswitch.net/cgit/openswitch/ops-openvswitch/tree/COPYING)

What other documents are available?
----------------------------------
For the high level design of ops-ntpd, refer to [DESIGN.md](DESIGN.md)

More Info
----------
Refer to [OpenSwitch] (http://www.openswitch.net)
Refer to [NTPsec] (https://www.ntpsec.org)
