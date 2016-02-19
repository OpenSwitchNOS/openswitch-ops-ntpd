# NTP-Client Test Cases

- [Test initial conditions](#test-initial-conditions)
- [Test NTP authentication disable/enable](#test-ntp-authentication-disableenable)
- [Test authentication key addition (valid key)](#test-authentication-key-addition-valid-key)
- [Test authentication key addition (invalid key)](#test-authentication-key-addition-invalid-key)
- [Test authentication key addition (invalid password)](#test-authentication-key-addition-invalid-password)
- [Test addition of NTP server (with no optional parameters)](#test-addition-of-ntp-server-with-no-optional-parameters)
- [Test addition of NTP server (with "prefer" option)](#test-addition-of-ntp-server-with-prefer-option)
- [Test addition of NTP server (with "version" option)](#test-addition-of-ntp-server-with-version-option)
- [Test addition failure of NTP server (with invalid "version" option)](#test-addition-failure-of-ntp-server-with-invalid-version-option)
- [Test addition failure of server with invalid server name](#test-addition-failure-of-server-with-invalid-server-name)
- [Test addition of NTP server (with valid "key-id" option)](#test-addition-of-ntp-server-with-valid-key-id-option)
- [Test addition of NTP server (with invalid "key-id" option)](#test-addition-of-ntp-server-with-invalid-key-id-option)
- [Test addition of NTP server (with all valid options)](#test-addition-of-ntp-server-with-all-valid-options)
- [Test addition of more than 8 NTP servers](#test-addition-of-more-than-8-NTP-servers)
- [Test addition of server with valid FQDN](#test-addition-of-server-with-valid-FQDN)

## Test initial conditions
### Objective
Verify that NTP is enabled.

### Requirements
The Virtual Mininet Test Setup is required for this test.

### Setup

#### Topology diagram
[s1]
### Description
This test confirms that NTP is enabled by default by displaying the `show ntp status` output.

### Test result criteria
#### Test pass criteria
All verifications succeed.
#### Test fail criteria
One or more verifications fail.

## Test NTP authentication disable/enable
### Objective
Verify that NTP authentication can be disabled or enabled.
### Requirements
The Virtual Mininet Test Setup is required for this test.
### Setup
#### Topology diagram
[s1]
### Description
1. Disable NTP authentication and display the output of the 'show ntp status` to confirm that NTP authentication is disabled.
2. Enable NTP authentication and display the output of `show ntp status` to confirm that NTP authentication is enabled.


### Test result criteria
#### Test pass criteria
All verifications succeed.
#### Test Fail Criteria
One or more verifications fail.

## Test authentication key addition (valid key)
### Objective
Verify that the addition of an NTP authentication key succeeds with a valid range with a valid password.
### Requirements
The Virtual Mininet Test Setup is required for this test.
### Setup
#### Topology diagram
[s1]
### Description
1. Add an NTP authentication key in the range of [1-65534].
2. Add an md5 password containing between 8 to 16 alphanumeric characters.
3. Confirm the existence of the NTP authentication key with the `show ntp authentication-keys` command.

### Test result criteria
#### Test pass criteria
The NTP authentication key is displayed as part of `show ntp authentication-keys` output.
#### Test Fail Criteria
The NTP authentication key is absent from the output of the `show ntp authentication-keys` command.

## Test authentication key addition (invalid key)
### Objective
Verify that the addition of NTP Authentication Key fails if it is outside the valid range.
### Requirements
 The Virtual Mininet Test Setup is required for this test.
### Setup
#### Topology diagram
[s1]
### Description
Add the NTP authentication key and ensure that it is outside of the [1-65534] range.

### Test result criteria
#### Test pass criteria
The NTP authentication key is absent from the `show ntp authentication-keys` command output.

#### Test fail criteria
The NTP authentication key is displayed as part of `show ntp authentication-keys` command output.
## Test authentication key addition (invalid password)
### Objective
Verify that the addition of an NTP authentication key fails when the password is incorrect.
### Requirements
The Virtual Mininet Test Setup is required for this test.
### Setup
#### Topology diagram
[s1]
### Description
Add an NTP authentication key with a password that has less than eight characters.

### Test result criteria
#### Test pass criteria
The NTP authentication key is absent from the `show ntp authentication-keys` command output.
#### Test fail criteria
The NTP authentication key is displayed as part of `show ntp authentication-keys` command output.

## Test addition of NTP server (with no optional parameters)
### Objective
Verify that the addition of an NTP server succeeds with just the server IP or the server FQDN.
### Requirements
The Virtual Mininet Test Setup is required for this test.
### Setup
#### Topology diagram
[s1]
### Description
- Add NTP server using just the IPV4 address
- Add NTP server using just the FQDN

### Test result criteria
#### Test pass criteria
These two NTP servers are present in the `show ntp associations` command output.
#### Test Fail Criteria
These two NTP servers are absent from the `show ntp associations` command output.

## Test addition of NTP server (with "prefer" option)
### Objective
Verify that the addition of an NTP server succeeds with the server IP/FQDN and the "prefer" option.
### Requirements
The Virtual Mininet Test Setup is required for this test.
### Setup
#### Topology diagram
[s1]
### Description
Add an NTP server using an IPv4 address and the "prefer" option.

### Test result criteria
#### Test pass criteria
This server is present in the `show ntp associations` command output.
#### Test fail criteria
This server is absent from the `how ntp associations` command output.

## Test addition of NTP server (with "version" option)
### Objective
Verify that the addition of an NTP server succeeds with the server IP/FQDN and a valid "version".
### Requirements
The Virtual Mininet Test Setup is required for this test.
### Setup
#### Topology diagram
[s1]
### Description
Add an NTP server using the IPV4 address and the version either as 3 or 4.
### Test result criteria
#### Test pass criteria
This server is present in the `show ntp associations` command output and displays the specified version.
#### Test fail criteria
This server is absent from the `show ntp associations` command output.

## Test addition failure of NTP server (with invalid "version" option)
### Objective
Verify that the addition of an NTP server fails when using an invalid "version".
### Requirements
The Virtual Mininet Test Setup is required for this test.
### Setup
#### Topology diagram
[s1]
### Description
Add an NTP server using the IPv4 address and a version of "5"

### Test result criteria
#### Test pass criteria
This server is absent from the `show ntp associations` command output.
#### Test Fail Criteria
This server is present in the `show ntp associations` command output and displays a specified version.

## Test addition failure of NTP server with invalid server name
### Objective
Verify that the addition of an NTP server fails when using an invalid server name.
### Requirements
The Virtual Mininet Test Setup is required for this test.
### Setup
#### Topology diagram
[s1]
### Description
Add an NTP server using an ill-formatted IPv4 address.

### Test result criteria
#### Test pass criteria
This server is absent from the `show ntp associations` command output.
#### Test Fail Criteria
This server is present in the `show ntp associations` command output.

## Test addition of NTP server (with valid "key-id" option)

### Objective
Verify that the addition of an NTP server succeeds using the server IP/FQDN and the "key-id" option.
### Requirements
The Virtual Mininet Test Setup is required for this test.
### Setup
#### Topology diagram
[s1]
### Description
1. Add an authentication-key as the number 10.
2. Add an NTP server using the IPv4 address and the key-id as 10.

### Test result criteria
#### Test pass criteria
This server is present in the `show ntp associations` command output and displays the specified version.
#### Test Fail Criteria
This server is absent from the `show ntp associations` command output.

## Test addition of NTP server (with invalid "key-id" option)
### Objective
Verify that the addition of an NTP server fails when using the server IP/FQDN and an invalid "key-id" option.
### Requirements
 The Virtual Mininet Test Setup is required for this test.
### Setup
#### Topology diagram
[s1]

### Description
1. Delete the authentication-key number 10 (if present).
1. Add the NTP server using the IPV4 address and the key-id as 10.

### Test result criteria
#### Test pass criteria
This server is absent from the `show ntp associations` command output.
#### Test Fail Criteria
This server is present in the `show ntp associations` command output and displays the specified version.

## Test addition of NTP server (with all valid options)
### Objective
Verify that the addition of an NTP server succeeds with the server IP/FQDN and all the following valid options:
- key-id
- prefer
- version

### Requirements
The Virtual Mininet Test Setup is required for this test.
### Setup
#### Topology diagram
[s1]
### Description
1. Add an authentication-key as the number 10
2. Add an NTP server using the IPv4 address with the following options and parameters:
- Key-id: 10
- Version: 4
- Option: prefer

### Test result criteria
#### Test pass criteria
This server is present in the `show ntp associations` command output and displays the specified key-id and version.
#### Test fail criteria
This server is absent from the `show ntp associations` command output.

## Test addition of more than 8 NTP servers
### Objective
Verify that the user can not add more than 8 NTP servers and an appropriate error message is shown when user tries to add more than 8 NTP servers.
### Requirements
The Virtual Mininet Test Setup is required for this test.
### Setup
#### Topology diagram
[s1]
### Description
- Add more than 8 NTP servers

### Test result criteria
#### Test pass criteria
An error message saying 'Maximum number of configurable NTP server limit has been reached' whenever user tries to add a 9th NTP server.
#### Test Fail Criteria
A 9th NTP server can be added or an error message different from 'Maximum number of configurable NTP server limit has been reached' is shown whenever user tries to add a 9th NTP server.

## Test addition of server with valid FQDN
### Objective
Verify that the addition of an NTP server succeeds with the server FQDN.
### Requirements
The Virtual Mininet Test Setup is required for this test.
### Setup
#### Topology diagram
[s1]
### Description
- Add an NTP server with a FQDN

### Test result criteria
#### Test pass criteria
This server is present in the `show ntp associations` command output and displays the specified FQDN.
#### Test Fail Criteria
This server is absent from the `show ntp associations` command output.
