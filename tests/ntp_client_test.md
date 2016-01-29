# NTP-Client Test Cases

[TOC]

## Test Initial Conditions
### Objective
Verify that NTP has been enabled
### Requirements
 - Virtual Mininet Test Setup
### Setup
#### Topology Diagram
```
[s1]
```
### Description ###
1. For this (Dill) release NTP is enabled by default.
2. Check the output of "show ntp status" to confirm
### Test Result Criteria
#### Test Pass Criteria
All verifications succeed.
#### Test Fail Criteria
One or more verifications fail.

## Test NTP authentication disable/enable
### Objective
Verify that NTP Authentication gets disabled/enabled
### Requirements
 - Virtual Mininet Test Setup
### Setup
#### Topology Diagram
```
[s1]
```
### Description ###
1. Disable NTP authentication
2. Check the output of "show ntp status" to confirm
3. Check it is not present in the output for "show running config"
4. Enable NTP authentication
5. Check the output of "show ntp status" to confirm
6. Confirm thst it is present in the output for "show running config"
### Test Result Criteria
#### Test Pass Criteria
All verifications succeed.
#### Test Fail Criteria
One or more verifications fail.

## Test authentication key addition (valid key)
### Objective
Verify addition of NTP Authentication Key in the valid range with a valid password succeeds
### Requirements
 - Virtual Mininet Test Setup
### Setup
#### Topology Diagram
```
[s1]
```
### Description ###
1. Add NTP Authentication key in the range of [1-65534]
2. Add md5 password containing 8-16 alphanumeric chars
### Test Result Criteria
#### Test Pass Criteria
NTP authentication key gets displayed as part of "show ntp authentication-keys"
#### Test Fail Criteria
NTP authentication key is absent from the output of "show ntp authentication-keys"

## Test authentication key deletion (valid key)
### Objective
Verify deletion of a previously added NTP Authentication Key
### Requirements
 - Virtual Mininet Test Setup
### Setup
#### Topology Diagram
```
[s1]
```
### Description ###
Delete the authentication key added using the earlier test
### Test Result Criteria
#### Test Pass Criteria
NTP authentication key is not displayed as part of "show ntp authentication-keys"
#### Test Fail Criteria
NTP authentication key is present in the output of "show ntp authentication-keys"

## Test authentication key addition (invalid key)
### Objective
Verify addition of NTP Authentication Key outside the valid range fails
### Requirements
 - Virtual Mininet Test Setup
### Setup
#### Topology Diagram
```
[s1]
```
### Description ###
1. Add NTP Authentication key outside the range of [1-65534]
### Test Result Criteria
#### Test Pass Criteria
NTP authentication key is absent from the output of "show ntp authentication-keys"
#### Test Fail Criteria
NTP authentication key gets displayed as part of "show ntp authentication-keys"

## Test authentication key addition (invalid password)
### Objective
Verify addition of NTP Authentication Key with an incorrect password fails
### Requirements
 - Virtual Mininet Test Setup
### Setup
#### Topology Diagram
```
[s1]
```
### Description ###
1. Add NTP Authentication key with a password lesser than 8 characters
### Test Result Criteria
#### Test Pass Criteria
NTP authentication key is absent from the output of "show ntp authentication-keys"
#### Test Fail Criteria
NTP authentication key gets displayed as part of "show ntp authentication-keys"

## Test addition of NTP server (with no optional parameters)
### Objective
Verify addition of NTP server with just the server IP/FQDN succeeds
### Requirements
 - Virtual Mininet Test Setup
### Setup
#### Topology Diagram
```
[s1]
```
### Description ###
1. Add NTP server using just the IPV4 address
1. Add NTP server using just the FQDN
### Test Result Criteria
#### Test Pass Criteria
These 2 NTP servers are present in the output of "show ntp associations"
#### Test Fail Criteria
These 2 NTP servers are absent from the output of "show ntp associations"

## Test addition of NTP server (with "prefer" option)
### Objective
Verify addition of NTP server with the server IP/FQDN and the "prefer" option succeeds
### Requirements
 - Virtual Mininet Test Setup
### Setup
#### Topology Diagram
```
[s1]
```
### Description ###
1. Add NTP server using the IPV4 address and the "prefer" option
### Test Result Criteria
#### Test Pass Criteria
This server is present in the output of "show ntp associations"
#### Test Fail Criteria
This server is absent from the output of "show ntp associations"

## Test addition of NTP server (with "version" option)
### Objective
Verify addition of NTP server with the server IP/FQDN and the valid "version" passes
### Requirements
 - Virtual Mininet Test Setup
### Setup
#### Topology Diagram
```
[s1]
```
### Description ###
1. Add NTP server using the IPV4 address and version as 3 or 4
### Test Result Criteria
#### Test Pass Criteria
This server is present in the output of "show ntp associations" & shows specified version
#### Test Fail Criteria
This server is absent from the output of "show ntp associations"

## Test addition failure of NTP server (with invalid "version" option)
### Objective
Verify addition of NTP server with an invalid "version" fails
### Requirements
 - Virtual Mininet Test Setup
### Setup
#### Topology Diagram
```
[s1]
```
### Description ###
1. Add NTP server using the IPV4 address and version as 5
### Test Result Criteria
#### Test Pass Criteria
This server is absent from the output of "show ntp associations"
#### Test Fail Criteria
This server is present in the output of "show ntp associations" & shows specified version

## Test addition of NTP server (with valid "key-id" option)
### Objective
Verify addition of NTP server with the server IP/FQDN and the "key-id" option succeeds
### Requirements
 - Virtual Mininet Test Setup
### Setup
#### Topology Diagram
```
[s1]
```
### Description ###
1. Add authentication-key as 10
2. Add NTP server using the IPV4 address and key-id as 10
### Test Result Criteria
#### Test Pass Criteria
This server is present in the output of "show ntp associations" & shows specified version
#### Test Fail Criteria
This server is absent from the output of "show ntp associations"

## Test addition of NTP server (with invalid "key-id" option)
### Objective
Verify addition of NTP server with the server IP/FQDN and invalid "key-id" option fails
### Requirements
 - Virtual Mininet Test Setup
### Setup
#### Topology Diagram
```
[s1]
```
### Description ###
1. Delete authentication-key 10 (if present)
1. Add NTP server using the IPV4 address and key-id as 10
### Test Result Criteria
#### Test Pass Criteria
This server is absent from the output of "show ntp associations"
#### Test Fail Criteria
This server is present in the output of "show ntp associations" & shows specified version

## Test addition of NTP server (with all valid options)
### Objective
Verify addition of NTP server with the server IP/FQDN and valid "key-id", "prefer" & "version" options succeeds
### Requirements
 - Virtual Mininet Test Setup
### Setup
#### Topology Diagram
```
[s1]
```
### Description ###
1. Add authentication-key as 10
2. Add NTP server using the IPV4 address and key-id as 10, version as 4 and the prefer option
### Test Result Criteria
#### Test Pass Criteria
This server is present in the output of "show ntp associations" & shows specified key-id & version
#### Test Fail Criteria
This server is absent from the output of "show ntp associations"
