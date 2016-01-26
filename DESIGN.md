#NTP client component design

##Contents
- [High level design](#high-level-design)
  - [Configuration workflow](#configuration-workflow)
  - [Show information workflow](#show-info-workflow)
- [OVSDB-Design](#ovsdb-design)
  - [OVSDB Representation](#ovsdb-representation)
  - [NTP global configuration](#ntp-configuration)
  - [NTP global statistics](#ntp-statistics)
  - [NTP Association table](#ntp-associations-table)
  - [NTP Key table](#ntp-keys-table)
- [Design choices](#design-choices)
  - [Open source repository](#design-choice-open-source-repository)
- [References](#references)

##High level design of NTP

```
            +----+             +----------------+
    +-----> |NTPD|             |                |
    |       +-+--+             |  CLI and REST  |
    |         |                |                |
    |       +-+--+             +-------+--------+
    |       |NTPQ|                     |
    |       +-+--+                     |
    |         |                        |
    |   +-----+--------+       +-------+---------+
    |   |              |       |                 |
    +---+   OPS-NTPD   +-------+      OVSDB      |
        |              |       |                 |
        +--------------+       +-----------------+

```
The NTP client feature provides the Network Time Protocol client functionality which synchronize information from NTP servers. OpenSwitch uses open source classic `ntpd` for NTP functionality. Classic `ntpd` provides both server and client functionality. But we are using it only in NTP client mode.

`ops-ntpd` python daemon manages `ntpd` and sends configuration information using `ntpq`. Periodically the `ops-ntpd` python daemon would poll and update status information for the associations with the OVSDB. This is the association status information used for **show NTP Association".

By enabling NTP Authentication, the `ntpd` daemon would start using the trusted keyid information configured with the association to do authenticate the server and use only those servers for synchronizing time.

###Configuration workflow
* When using NTP client, the operator would be configuring NTP Association(servers) to be used by the NTP client to synchronize time information. This configuration specific to NTP client is maintained in OVSDB. The user configuration for NTP client are updated in OVSDB through CLI and REST daemons.
* The NTP client python daemon monitors the OVSDB for any configuration changes specific to NTP client and if there are any configuration changes, the `ops-ntpd` python daemon communicates the updates to `ntpd` using `ntpq`.

###Show information workflow
* `ops-ntpd` daemon periodically updates the status information with `ntpd` (using `ntpq`) about the NTP Association into OVSDB. This information is used to display when a call to `show NTP Association` is made.
* `ops-ntpd` daemon also updates the system info and statistics information about `ntpd` daemon which can be used for debugging purposes.
* `ntpd` updates a log file whose output is displayed by issuing the `show ntp logging`.

##OVSDB-Design
The OVSDB is the central database used in OpenSwitch. All the communication between different modules are facilitated through this database. The following tables and columns are used in the OVSDB for NTP client functionality:
##OVSDB-Representation
```
  +---------------------------------------------------------+
  |                       OVSDB                             |
  |   +--------------------+                                |
  |   |                    |           +----------+         |
  |   |      SYSTEM        |           |          |         |
  |   |                    +----------->   VRF    |         |
  |   |  global config     |           |          |         |
  |   |  global statistics |           +----^-----+         |
  |   |                    |                |               |
  |   +--------------------+                |               |
  |                                         |               |
  |                                         |               |
  |                                         |               |
  |   +--------------------+        +-------+----------+    |
  |   |     NTP Key       |        |      NTP         |    |
  |   |                    <--------+   ASSOCIATIONS   |    |
  |   |   key id           |        |                  |    |
  |   |   key trust conf   |        | configuration    |    |
  |   |   md5 password     |        | status info      |    |
  |   |                    |        |                  |    |
  |   +--------------------+        +------------------+    |
  |                                                         |
  +---------------------------------------------------------+
```

###NTP global configuration
The following key=value pair mappings are used in NTP config column of System table for global NTP configuration:

* The key **authentication_enable** would have the value **true** if NTP Authentication is enabled and **false** if NTP Authentication is disabled.

###NTP global statistics

The following key=value pair mappings are used in NTP statistics column of System table for global NTP statistics:

* The key **uptime** would keep information about the time in hours since the system was last rebooted.
* The key **ntp\_pkts\_received** would keep statistics about the Total number of packets received.
* The key **ntp\_pkts\_with\_current\_version** would keep statistics about the number of packets matching the current NTP version.
* The key **ntp\_pkts\_with\_older\_version** would keep statistics about the number of packets matching the previous NTP version.
* The key **ntp\_pkts\_with\_bad\_length\_or\_format** would keep statistics about the number of packets with invalid length, format or port number.
* The key **ntp\_pkts\_with\_auth\_failed** would keep statistics about the number of packets not verified as authentic.
* The key **ntp\_pkts\_declined** would keep statistics about the number of packets denied access for any reason.
* The key **ntp\_pkts\_restricted** would keep statistics about the number of packets restricted for any reason.
* The key **ntp\_pkts\_rate\_limited** would keep statistics about the number of packets discarded due to rate limitation.
* The key **ntp\_pkts\_kod\_responses** would keep statistics about the number of KoD packets from the server.

###NTP Association table
The NTP Association table has the following columns:

```
Name
Key
Vrf
Association Attributes
Association Status
```
- **address**: FQDN or ip address for the association..
- **key_id**: This column has a reference to the NTP Key table.
- **vrf**: This column has a weak reference to the VRF table.
- **association_attributes**: This column has key=value pairs mapping of association status information. The following key=value pair mappings are used:
  * The key **ref\_clock_id** stores the refclock driver ID, if available a refclock driver ID like "127.127.1.0" for non uni/multi/broadcast associations
  * The key **prefer** stores the preference flag to suggest for this association. Set this to <code>true</code> to enable preference
for this association.
  * The key **ntp_version** stores the NTP version to use for when communicating with this association.

- **association_status**: This column has key=value pairs mapping of association status information. The following key=value pair mappings are used:
      
      <column name="association_status" key="reference_time">
        Provides the time (in "day, month date year hh:mm" format)
        when the server clock of refid was last adjusted.
        Eg format Wed, Jan 13 2016  7:56:26.126
      </column>
      <column name="association_status" key="peer_status_word"
        type='{"type": "string", "enum": ["set", ["reject",
        "falsetick", "excess", "outlier", "pps_peer",
        "candidate", "backup", "system_peer"]]}'>
        Provides information about the peer status.
        Refer to link for more info
        <code>https://www.eecis.udel.edu/~mills/ntp/html/decode.html#peer</code>
      </column>
      <column name="association_status" key="associd">
        Provides the Association ID mapped for this association.
        This is an Internal ID.
      </column>
  * The key **remote\_peer_address** stores the remote peer's ip address being synced to. If FQDN is used as "address" during config, then this would be the ip address.
  * The key **remote\_peer\_ref\_id** stores the reference id used by the remote peer. This can be either another server or stratum 1 devices like .GPS. .USNO. etc.
  * The key **stratum** stores remote peer or server Stratum
  * The key **peer_type** stores the type (u: unicast or manycast client,
    b: broadcast or multicast client, l: local reference clock, s: symmetric peer,
    A: manycast server, B: broadcast server, M: multicast server
  * The key **last\_polled** stores when last polled (seconds ago, 'h' hours ago, or 'd' days ago). Example 6h, 5d, 5 (this refers to seconds).
  * The key **polling_interval** stores the polling frequency (in seconds) used for this peer.
  * The key **reachability_register** stores status about the last consequetive polls for this peer. (1 bit per poll)
  * The key **network_delay** stores the round trip communication delay to the remote peer or server
  (milliseconds)
  * The key **time_offset** stores the Root Mean Square time (in milliseconds) between this local host and the remote peer or server.
  * The key **jitter** stores jitter (in milliseconds) in the time reported for that remote peer or server.
  * The key **reference_time** stores the time (in "day, month date year hh:mm" format) when the server clock of refid was last adjusted. Eg format Wed, Jan 13 2016  7:56:26.126
  * The key **root_dispersion** stores maximum error relative time (in seconds) to primary reference clock.
  * The key **peer_status_word** stores information about the peer status. It can be either a candidate or a system selected peer. It can take on other states like 'reject', 'falsetick', 'excess', 'outlier', 'pps_peer'.
  * The key **associd** stores the Association ID for the peer. This is an Internal ID.

###NTP Key table
The NTP Key table has the following columns:

```
Key Id
Password
Trust enable
```
- **key_id** specifies a key_id which is used for NTP authentication.
- **key_password** specifies a key_password which is used for NTP authentication.
- **trust_enable** enables trust settings for this key_id. By default it is false.


##Design choices

###Open source repository
There are multiple open source choices available for the NTP. The open source from [ntp.org](http://www.ntp.org/) was chosen based on the following considerations:

* It is standard NTP reference implementation and is widely used.
* It can be cross compiled without issues.
* It support NTP authentication and advanced security measures for time synchronization.
* The NTP Project conducts Research and Development in NTP and produces the Official Reference Implementation of NTP.
* The NTP Project also drives standards and formalies RFCs for newer implementations, also provides maintainance releases for common zero day issues.

##References
* [NTP references](http://doc.ntp.org/)
* [NTPQ references](http://doc.ntp.org/4.2.6p5/debug.html)
