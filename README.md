OPS-NTPD
========

What is ops-ntpd?
-----------------
The `ops-ntpd` Python module handles the Network Time Protocol (NTP) component in OpenSwitch. This component serves the following functions:
- It is an interaction layer between the NTP Daemon and the Open vSwitch Database (OVSDB).
- It reads the configuration from the OVSDB and sends it to the NTP daemon.
- It reads the NTP daemon status and populates the OVSDB.
- If a configuration change in OVSDB warrants a daemon restart, it restarts the NTP daemon.

What daemon are you using for NTP?
-----------------------------------
We are using the [NTPsec](https://www.ntpsec.org) repository to run the NTP daemon.

What is the structure of the repository?
----------------------------------------
- `ops-ntpd` The Python source files are under this subdirectory.
- `./tests/` - This directory contains the component tests of `ops-ntpd` based on the ops Mininet framework.

What is the license?
--------------------
Apache 2.0 license. For more details refer to [COPYING](https://git.openswitch.net/cgit/openswitch/ops-openvswitch/tree/COPYING)

What other documents are available?
----------------------------------
For the high level design of `ops-ntpd`, refer to [DESIGN.md](DESIGN.md)

More Info
----------
- [OpenSwitch](http://www.openswitch.net)
- [NTPsec](https://www.ntpsec.org)
