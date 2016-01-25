#!/usr/bin/env python
# (C) Copyright 2015-2016 Hewlett Packard Enterprise Development LP
# All Rights Reserved.
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
#    under the License..

'''
NOTES:
 OPS-NTPD python daemon.
 - This is a helper daemon to retrieve the NTP configs from OVSDB
   during bootup and starts the NTPD dameon.
 - Any updates from OVSDB is synced to NTPD using NTPQ and NTPDC
 - Periodic updates from NTPD is synced to OVSDB using
   ops_ntpd_sync_to_ovsdb script.
'''

import os, sys, time, signal, shutil, copy
import argparse, subprocess, json, pprint
import ovs.dirs
from ovs.db import error
from ovs.db import types
import ovs.daemon
import ovs.db.idl
import ovs.unixctl
import ovs.unixctl.server

# OVSDB information
idl = None
def_db = 'unix:/var/run/openvswitch/db.sock'
ovs_schema = '/usr/share/openvswitch/vswitch.ovsschema'

# vlog setup
vlog = ovs.vlog.Vlog("ops-ntpd")

# Globals
exiting = False
seqno = 0
ntpd_process = None
ntpq_process = None
ntpd_started = False
ntpd_command = None
ntpd_info    = None
ntpq_info    = None
g_ntpa_map   = {}
g_ntpk_db    = {}
controlkey   = 65535
cmdline_str  = ""
default_assoc_info = {
    "remote_peer_address" : "-",
    "remote_peer_ref_id" : "-",
    "stratum" : "-",
    "peer_type" : "-",
    "last_polled" : "-",
    "polling_interval" : "-",
    "reachability_register" : "-",
    "network_delay" : "-",
    "time_offset" : "-",
    "jitter" : "-",
    "root_dispersion" : "-",
    "peer_status_word" : "-",
    "associd" : "-",
}

translate_peer_status_word = {
  "sel_reject" : "reject",
  "sel_falsetick" : "falsetick",
  "sel_excess" : "excess",
  "sel_outlyer" : "outlier",
  "sel_candidate" : "candidate",
  "sel_backup" : "backup",
  "sel_sys.peer" : "system_peer",
  "sel_pps.peer" : "pps_peer"
}
translate_peer_type = {
  "u" : "unicast",
  "b" : "bcast_or_mcast_",
  "l" : "local_ref_clock",
  "m" : "mcast_server"
}

# Defaults
DEFAULT_NTP_KEY_ID        = 0
DEFAULT_NTP_PREF          = False
DEFAULT_NTP_VERSION       = 3
DEFAULT_NTP_REF_CLOCK_ID  = ".LOCL."
DEFAULT_NTP_TRUST_ENABLE  = False

# Tables definitions
NTP_ASSOCIATION_TABLE   = 'NTP_Association'
NTP_KEY_TABLE           = 'NTP_Key'
SYSTEM_TABLE            = 'System'
# Columns definitions
SYSTEM_CUR_CFG          = 'cur_cfg'
SYSTEM_NTP_CONFIG       = 'ntp_config'
NTP_ASSOCIATION_VRF     = 'vrf'
NTP_ASSOCIATION_ADDRESS = 'address'
NTP_ASSOCIATION_KEY_ID  = 'key_id'
NTP_ASSOCIATION_ATTR    = 'association_attributes'
NTP_KEY_ID              = 'key_id'
NTP_KEY_PASSWORD        = 'key_password'
NTP_KEY_TRUST_ENABLE    = 'trust_enable'

# String keys
NTPQ_REMOTE  = "remote"
NTPQ_ASSOCID = "assid"
NTPQ_REFID = "refid"
NTPQ_ST = "st"
NTPQ_T = "t"
NTPQ_WHEN = "when"
NTPQ_POLL = "poll"
NTPQ_REACH = "reach"
NTPQ_DELAY = "delay"
NTPQ_OFFSET = "offset"
NTPQ_JITTER = "jitter"

NTPQ_REMOTE_PEER_ADDRESS = "remote_peer_address"
NTPQ_REMOTE_PEER_REF_ID = "remote_peer_ref_id"
NTPQ_ROOT_DISPERSION = "root_dispersion"
NTPQ_STRATUM = "stratum"
NTPQ_PEER_TYPE = "peer_type"
NTPQ_LAST_POLLED = "last_polled"
NTPQ_POLLING_INTERVAL = "polling_interval"
NTPQ_REACHABILITY_REGISTER = "reachability_register"
NTPQ_NETWORK_DELAY = "network_delay"
NTPQ_TIME_OFFSET = "time_offset"
NTPQ_JITTER = "jitter"
NTPQ_REFERENCE_TIME = "reference_time"
NTPQ_PEER_STATUS_WORD = "peer_status_word"
NTPQ_ASSOCID = "associd"

NTPQ_UPTIME = "uptime"
NTPQ_SYSSTATS_RESET = "sysstats reset"
NTPQ_PACKETS_RECEIVED = "packets received"
NTPQ_CURRENT_VERSION = "current version"
NTPQ_OLDER_VERSION = "older version"
NTPQ_BAD_LENGTH_OR_FORMAT = "bad length or format"
NTPQ_AUTHENTICATION_FAILED = "authentication failed"
NTPQ_DECLINED = "declined"
NTPQ_RESTRICTED = "restricted"
NTPQ_RATE_LIMITED = "rate limited"
NTPQ_KOD_RESPONSES = "KoD responses"
NTPQ_PROCESSED_FOR_TIME = "processed for time"

# NTP global info keys/columns
NTP_UPTIME = "uptime"
NTP_STAT_NTP_PKTS_RECEIVED = "ntp_pkts_received"
NTP_STAT_NTP_PKTS_WITH_CURRENT_VERSION = "ntp_pkts_with_current_version"
NTP_STAT_NTP_PKTS_WITH_OLDER_VERSION = "ntp_pkts_with_older_version"
NTP_STAT_NTP_PKTS_WITH_BAD_LENGTH_OR_FORMAT = "ntp_pkts_with_bad_length_or_format"
NTP_STAT_NTP_PKTS_WITH_AUTH_FAILED = "ntp_pkts_with_auth_failed"
NTP_STAT_NTP_PKTS_DECLINED = "ntp_pkts_declined"
NTP_STAT_NTP_PKTS_RESTRICTED = "ntp_pkts_restricted"
NTP_STAT_NTP_PKTS_RATE_LIMITED = "ntp_pkts_rate_limited"
NTP_STAT_NTP_PKTS_KOD_RESPONSES = "ntp_pkts_kod_responses"

def ops_ntpd_create_working_dir(ntp_working_dir_path):
    try:
        ops_ntpd_cleanup_working_dir(ntp_working_dir_path)
    finally:
        os.system("mkdir %s"%ntp_working_dir_path)

def ops_ntpd_cleanup_working_dir(ntp_working_dir_path):
    os.system("rm -rf %s;" %(ntp_working_dir_path))

def ops_ntpd_update_content_buffer(file_buffer, line):
    return file_buffer + [line+"\n"]

def ops_ntpd_get_file_contents(filename):
    fh = open(filename, 'r')
    contents = fh.readlines()
    fh.close()
    return contents

def ops_ntpd_set_file_contents(filename, contents):
    with open(filename, "w+") as f:
        f.writelines(contents)

def ops_ntpd_setup_ntpq_integration(ntp_working_dir_path):
    global ntpq_info, cmdline_str
    os.system("cd %s;ntp-keygen -M"%ntp_working_dir_path)
    filepath = ntp_working_dir_path + "ntp.keys"
    for line in ops_ntpd_get_file_contents(filepath):
        if line.endswith("# MD5 key\n"):
            controlkey_answer = line.strip().split()[2]
            break
    os.system("rm -rf %s/*;"%ntp_working_dir_path)
    ntpq_info = (controlkey, controlkey_answer)
    #Build a commandline string to execute
    cmdline_str = "ntpq -c \"keyid %d\" -c \"passwd %s\""%\
            (controlkey, controlkey_answer)
    return (controlkey, controlkey_answer)

def ops_ntpd_setup_ntpd_default_config_file(ntp_working_dir_path):
    global ntpq_info
    os.system("cd %s;"%ntp_working_dir_path)
    conf = []
    conf = ops_ntpd_update_content_buffer(conf,
        "#This is generated from ops-ntpd")
    conf = ops_ntpd_update_content_buffer(conf,
        "trustedkey %s"%(ntpq_info[0]))
    conf = ops_ntpd_update_content_buffer(conf,
        "requestkey %s"%(ntpq_info[0]))
    conf = ops_ntpd_update_content_buffer(conf,
        "controlkey %s"%(ntpq_info[0]))
    conf = ops_ntpd_update_content_buffer(conf,
        "enable mode7")
    conf_file = ntp_working_dir_path + "ops_ntp.conf"
    ops_ntpd_set_file_contents(conf_file, conf)
    return conf_file

def ops_ntpd_get_ntpd_default_keys_file_content():
    global ntpq_info
    keys_content = "#This is generated from ops-ntpd\n"
    keys_content += " %s MD5 %s\n"%(ntpq_info[0], ntpq_info[1])
    return keys_content

def ops_ntpd_setup_ntpd_default_keys_file(ntp_working_dir_path):
    global ntpq_info
    os.system("cd %s;"%ntp_working_dir_path)
    keys_info = []
    keys_info = ops_ntpd_update_content_buffer(keys_info,
        ops_ntpd_get_ntpd_default_keys_file_content())
    keys_file = ntp_working_dir_path + "ops_ntp.keys"
    ops_ntpd_set_file_contents(keys_file, keys_info)
    return keys_file

def ops_ntpd_setup_ntpd_default_log_file(ntp_working_dir_path):
    return ntp_working_dir_path + "ops_ntp.log"

def ops_ntpd_run_command(command):
    process = subprocess.Popen(args=command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    shell=True)
    error = process.stderr.read()
    output = process.communicate()[0]
    return error, output

def ops_ntpd_setup_ntp_key_map(ntpk_db, key_id, key_pass, trust_flag):
    ntpk_db[key_id] = (key_pass, trust_flag)

def ops_ntpd_setup_ntp_config_map(ntpa_map, vrf, address, associd, key_id, ref_clock_id, prefer, ntp_version):
    ntpa_map[(vrf,address)] = associd
    ntpa_map[(vrf,address)] = (address, vrf, key_id, ref_clock_id, prefer, ntp_version)

def ops_ntpd_sync_updates_to_ntpd(server_configs, key_configs, keys_file_content):
    global cmdline_str
    global ntpd_info
    command = copy.copy(cmdline_str)
    for config in server_configs+key_configs:
       command += " -c \"%s\""%(config)
    vlog.dbg("ops_ntpd_run_command is %s"%command)

    ops_ntpd_set_file_contents(ntpd_info[1], keys_file_content)
    process = subprocess.Popen(args="ntpq -c \"authinfo\"",
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    shell=True)
    output = process.communicate()
    ops_ntpd_run_command("ntpdc -c \"readkeys\"")
    process = subprocess.Popen(args="ntpq -c \"authinfo\"",
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    shell=True)
    output = process.communicate()
    ops_ntpd_run_command(command)
    vlog.info("Sync OVSDB -> NTPD : done")

def ops_ntpd_get_ntpd_associations_info(ntpd_updates):
    a_table = {}
    assoc_db = {}
    associations_info_table = {}
    process = subprocess.Popen(args="ntpq -n -c \"apeers\"",
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    shell=True)
    cmd_output = process.communicate()
    n_out = cmd_output[0].strip().split('\n')[2:]
    for n in n_out:
        n = n.strip().split()
        a_entry = {}
        a_entry[NTPQ_REMOTE] = n[0]
        a_entry[NTPQ_REFID] = n[1]
        a_entry[NTPQ_ASSOCID] = n[2]
        a_entry[NTPQ_ST] = n[3]
        a_entry[NTPQ_T] = n[4]
        a_entry[NTPQ_WHEN] = n[5]
        a_entry[NTPQ_POLL] = n[6]
        a_entry[NTPQ_REACH] = n[7]
        a_entry[NTPQ_DELAY] = n[8]
        a_entry[NTPQ_OFFSET] = n[9]
        a_entry[NTPQ_JITTER] = n[10]
        a_table[a_entry[NTPQ_ASSOCID]] = a_entry
        assoc_db[a_entry[NTPQ_ASSOCID]] = a_entry

    for assoc_id in assoc_db.keys():
        process = subprocess.Popen(args="ntpq -c \"rv %s\""%assoc_id,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        shell=True)
        cmd_output = process.communicate()
        n_out = " ".join(cmd_output[0].split("\n"))
        n = n_out.split(",")
        associd = n[0].split()[0].strip().split("=")[1]
        peer_status_word = [x.strip() for x in n if "sel_" in x][0]
        root_dispersion = [x.strip() for x in n if "rootdisp" in x][0].strip().split("=")[1]
        remote_peer_address = [x.strip() for x in n if "srcadr" in x][0].strip().split("=")[1]
        reference_time = " ".join([n[i]+n[i+1] for i in range(len(n)) if "reftime" in n[i]][0].strip().split("=")[1].split()[1:])
        a_table[assoc_id][NTPQ_REMOTE] = remote_peer_address
        a_table[assoc_id][NTPQ_ROOT_DISPERSION] = root_dispersion
        a_table[assoc_id][NTPQ_REFERENCE_TIME] = reference_time
        a_table[assoc_id][NTPQ_PEER_STATUS_WORD] = peer_status_word
        associations_info_table[remote_peer_address] = a_table[assoc_id]

    for address in associations_info_table.keys():
        assoc_info = copy.copy(default_assoc_info)
        vlog.dbg("Gathering information about address %s"%address)
        assoc_info["remote_peer_address"] = associations_info_table[address][NTPQ_REMOTE]
        assoc_info["remote_peer_ref_id"] = associations_info_table[address][NTPQ_REFID]
        assoc_info["stratum"] = associations_info_table[address][NTPQ_ST]
        assoc_info["peer_type"] = translate_peer_type[\
            associations_info_table[address][NTPQ_T]]
        assoc_info["last_polled"] = associations_info_table[address][NTPQ_WHEN]
        assoc_info["polling_interval"] = associations_info_table[address][NTPQ_POLL]
        assoc_info["reachability_register"] = associations_info_table[address][NTPQ_REACH]
        assoc_info["network_delay"] = associations_info_table[address][NTPQ_DELAY]
        assoc_info["time_offset"] = associations_info_table[address][NTPQ_OFFSET]
        assoc_info["jitter"] = associations_info_table[address][NTPQ_JITTER]
        assoc_info["root_dispersion"] = associations_info_table[address][NTPQ_ROOT_DISPERSION]
        assoc_info["peer_status_word"] = translate_peer_status_word[\
            associations_info_table[address][NTPQ_PEER_STATUS_WORD]]
        assoc_info["associd"] = associations_info_table[address][NTPQ_ASSOCID]
        assoc_info["reference_time"] = associations_info_table[address][NTPQ_REFERENCE_TIME]
        ntpd_updates["associations_info"][address] = assoc_info

def ops_ntpd_get_ntpd_global_status(ntpd_updates):
    process = subprocess.Popen(args="ntpq -n -c \"sysstats\"",
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    shell=True)
    cmd_output = process.communicate()
    n_out = cmd_output[0].strip().split("\n")
    sysstat_table = {}
    for n in n_out:
        n = [i.lstrip() for i in n.strip().split(":")]
        sysstat_table[n[0]] = n[1]
    ntpd_updates["statistics"][NTP_STAT_NTP_PKTS_RECEIVED] = str(sysstat_table[NTPQ_PACKETS_RECEIVED])
    ntpd_updates["statistics"][NTP_STAT_NTP_PKTS_WITH_CURRENT_VERSION] = str(sysstat_table[NTPQ_CURRENT_VERSION])
    ntpd_updates["statistics"][NTP_STAT_NTP_PKTS_WITH_OLDER_VERSION] = str(sysstat_table[NTPQ_OLDER_VERSION])
    ntpd_updates["statistics"][NTP_STAT_NTP_PKTS_WITH_BAD_LENGTH_OR_FORMAT] = str(sysstat_table[NTPQ_BAD_LENGTH_OR_FORMAT])
    ntpd_updates["statistics"][NTP_STAT_NTP_PKTS_WITH_AUTH_FAILED] = str(sysstat_table[NTPQ_AUTHENTICATION_FAILED])
    ntpd_updates["statistics"][NTP_STAT_NTP_PKTS_DECLINED] = str(sysstat_table[NTPQ_DECLINED])
    ntpd_updates["statistics"][NTP_STAT_NTP_PKTS_RESTRICTED] = str(sysstat_table[NTPQ_RESTRICTED])
    ntpd_updates["statistics"][NTP_STAT_NTP_PKTS_RATE_LIMITED] = str(sysstat_table[NTPQ_RATE_LIMITED])
    ntpd_updates["statistics"][NTP_STAT_NTP_PKTS_KOD_RESPONSES] = str(sysstat_table[NTPQ_KOD_RESPONSES])
    ntpd_updates["status"][NTP_UPTIME] = str(sysstat_table[NTPQ_UPTIME])

def ops_ntpd_sync_updates_to_ovsdb():
    global g_ntpa_map
    ntpd_updates = {}
    ntpd_updates["associations_info"] = {}
    ntpd_updates["statistics"] = {}
    ntpd_updates["status"] = {}
    ops_ntpd_get_ntpd_associations_info(ntpd_updates)
    ops_ntpd_get_ntpd_global_status(ntpd_updates)
    str_ntpd_updates = json.dumps(ntpd_updates)
    vlog.dbg("Sync information is \n %s"%(pprint.pformat(ntpd_updates, indent=5)))
    os.system("ops_ntpd_sync_to_ovsdb -c update -d '%s'"%(str_ntpd_updates))
    vlog.info("Sync NTPD -> OVSDB : done")

def ops_ntpd_check_updates_with_ntp_associations(l_ntpa_map):
    global g_ntpa_map
    add = []
    delete = []
    add_configs = []
    add_template_string = ":config server "
    delete_template_string = ":config unconfig "
    for k in list(set(l_ntpa_map.keys() + g_ntpa_map.keys())):
        if k in l_ntpa_map.keys():
            v = l_ntpa_map[k]
            if k not in g_ntpa_map.keys():
                add.append(k)
                g_ntpa_map[k] = v
            elif v != g_ntpa_map[k]:
                delete.append(k)
                add.append(k)
                g_ntpa_map[k] = v
        else:
            delete.append(k)
            del g_ntpa_map[k]
    delete_configs = [delete_template_string+x[1] for x in delete]
    for x in add:
        (addr, vrf, key_id, ref_clk, pref, ver) = g_ntpa_map[x]
        add_config  = add_template_string+addr
        if key_id != DEFAULT_NTP_KEY_ID:
            add_config += " key "+key_id
        if ver != DEFAULT_NTP_VERSION:
            add_config += " version "+ver
        if pref != DEFAULT_NTP_PREF:
            add_config += " prefer"
        add_configs += [add_config]
    server_configs = delete_configs + add_configs
    return server_configs

def ops_ntpd_check_updates_with_ntp_keys(l_ntpk_db):
    global g_ntpk_db, ntpq_info
    add_template_string = " %s MD5 %s"
    trustedkey_template_string = ":config trustedkey "
    untrustedkey_template_string = ":config unconfig trustedkey "
    readkeys_template_string = ":config readkeys"
    trusted_keys = []
    untrusted_keys = []
    trusted_key_config = []
    untrusted_key_config = []
    keys_file_content = ops_ntpd_get_ntpd_default_keys_file_content()
    if len(l_ntpk_db) > 0 and len(g_ntpk_db) > 0:
        untrusted_keys = set(g_ntpk_db.keys())- set(l_ntpk_db.keys())
        g_ntpk_db = copy.copy(l_ntpk_db)
        trusted_keys = g_ntpk_db.keys()
    elif len(g_ntpk_db) == 0:
        g_ntpk_db = copy.copy(l_ntpk_db)
        trusted_keys = g_ntpk_db.keys()
    elif len(l_ntpk_db) == 0:
        untrusted_keys = g_ntpk_db.keys()
        g_ntpk_db = {}
    keys_file_content += "\n".join([add_template_string%(k,v[0]) for k,v in g_ntpk_db.iteritems()])
    if len(trusted_keys) > 0:
        trusted_key_config += [trustedkey_template_string+" ".join([str(x) for x in trusted_keys])]
    if len(untrusted_keys) > 0:
        untrusted_key_config += [untrustedkey_template_string+" ".join([str(x) for x in untrusted_keys])]
    key_config = untrusted_key_config + trusted_key_config
    keys_file_content += "\n"
    return key_config, keys_file_content

def ops_ntpd_check_updates_from_ovsdb():
    global idl
    global ntpd_command
    global ntpq_process
    global cmdline_str
    global g_ntpk_db
    ovs_rec = None
    associd = 0
    vlog.info("ops_ntpd_check_updates_from_ovsdb")
    authentication_enable = "disabled"
    update_map = {}
    #Get the NTP association configuration changes
    for ovs_rec in idl.tables[NTP_ASSOCIATION_TABLE].rows.itervalues():
        key_id = DEFAULT_NTP_KEY_ID
        prefer = DEFAULT_NTP_PREF
        ntp_version = DEFAULT_NTP_VERSION
        ref_clock_id = DEFAULT_NTP_REF_CLOCK_ID
        vrf = ovs_rec._data['vrf'].to_json()[1]
        if ovs_rec.address and ovs_rec.address is not None:
            ip_address = ovs_rec.address
        if ovs_rec.key_id and len(ovs_rec.key_id) > 0:
            key_id = str(ovs_rec.key_id[0].key_id)
        if ovs_rec.association_attributes and ovs_rec.association_attributes is not None:
            for key, value in ovs_rec.association_attributes.iteritems():
                if key == 'ref_clock_id':
                    ref_clock_id = value
                if key == 'prefer':
                    prefer = value
                if key == 'version':
                    ntp_version = value
        ops_ntpd_setup_ntp_config_map(update_map, vrf, ip_address,
                            associd, key_id, ref_clock_id, prefer, ntp_version)
    server_configs = ops_ntpd_check_updates_with_ntp_associations(update_map)
    vlog.dbg("Server config changes %s " %(pprint.pformat(server_configs)))

    update_map = {}
    #Check if ntp authentication is enabled
    for ovs_rec in idl.tables[SYSTEM_TABLE].rows.itervalues():
        if ovs_rec.ntp_config and ovs_rec.ntp_config is not None:
            for key, value in ovs_rec.ntp_config.iteritems():
                if key == 'authentication_enable':
                    authentication_enable = value
    vlog.dbg("Authentication is %s " %(authentication_enable))

    update_map = {}
    #Get the NTP key changes
    for ovs_rec in idl.tables[NTP_KEY_TABLE].rows.itervalues():
        trust_enable = DEFAULT_NTP_TRUST_ENABLE
        if ovs_rec.key_id and ovs_rec.key_id is not None:
            key_id = ovs_rec.key_id
        if ovs_rec.key_password and ovs_rec.key_password is not None:
            key_password = ovs_rec.key_password
        if ovs_rec.trust_enable and ovs_rec.trust_enable is not None:
            trust_enable = ovs_rec.trust_enable
        vlog.dbg("trust_enable is %s and auth is %s"%(trust_enable, authentication_enable))
        if trust_enable == True and authentication_enable == "enabled":
            ops_ntpd_setup_ntp_key_map(update_map, key_id, key_password, trust_enable)
    key_configs, keys_file_content = ops_ntpd_check_updates_with_ntp_keys(\
            update_map)
    vlog.dbg("Key config changes %s " %(pprint.pformat(key_configs)))

    ops_ntpd_sync_updates_to_ntpd(server_configs, key_configs, keys_file_content)

def ops_ntpd_connection_exit_handler(conn, unused_argv, unused_aux):
    global exiting
    exiting = True
    conn.reply(None)

def ops_ntpd_check_system_status():
    '''
    Checks if the system initialization is completed.
    If System:cur_cfg > 0:
        configuration completed: return True
    else:
        return False
    '''
    global idl
    for ovs_rec in idl.tables[SYSTEM_TABLE].rows.itervalues():
        if ovs_rec.cur_cfg:
            if ovs_rec.cur_cfg == 0:
                return False
            else:
                return True

    return False

def ops_ntpd_setup_ovsdb_monitoring(remote):
    '''
    Initializes the OVS-DB connection
    '''
    global idl
    schema_helper = ovs.db.idl.SchemaHelper(location=ovs_schema)
    schema_helper.register_columns(SYSTEM_TABLE,
                                   [SYSTEM_NTP_CONFIG,SYSTEM_CUR_CFG])
    schema_helper.register_columns(NTP_ASSOCIATION_TABLE,
                                   [NTP_ASSOCIATION_VRF,
                                   NTP_ASSOCIATION_ADDRESS,
                                   NTP_ASSOCIATION_KEY_ID,
                                   NTP_ASSOCIATION_ATTR])
    schema_helper.register_columns(NTP_KEY_TABLE,
                                   [NTP_KEY_ID,
                                   NTP_KEY_PASSWORD,
                                   NTP_KEY_TRUST_ENABLE])
    idl = ovs.db.idl.Idl(remote, schema_helper)

def ops_ntpd_setup_ntpd_default_config():
    ntp_dir_path = "/etc/ntp/"
    ops_ntpd_create_working_dir(ntp_dir_path)
    ops_ntpd_setup_ntpq_integration(ntp_dir_path)
    conf_file = ops_ntpd_setup_ntpd_default_config_file(ntp_dir_path)
    keys_file = ops_ntpd_setup_ntpd_default_keys_file(ntp_dir_path)
    log_file  = ops_ntpd_setup_ntpd_default_log_file(ntp_dir_path)
    return (conf_file, keys_file, log_file)

def ops_ntpd_start_ntpd(ntpd_info):
    global ntpd_process
    global ntpd_command
    ntpd_process = None
    (conf_file, keys_file, log_file) = ntpd_info
    ntpd_command = "ntpd -c %s -k %s -l %s"%(conf_file, keys_file, log_file)
    err, out = ops_ntpd_run_command(ntpd_command)
    if err != "":
        vlog.emer("%s" % (err))
        vlog.emer("Error with config, ntpd failed, command %s" %
                  (ntpd_command))
    else:
        vlog.info("ops-ntpd-debug - ntpd started")

def ops_ntpd_provision_ntpd_daemon():
    global idl
    global seqno
    global ntpd_started
    global ntpd_info
    idl.run()
    if seqno != idl.change_seqno:
        vlog.info("ops-ntpd-debug - seqno change from %d to %d "
                  % (seqno, idl.change_seqno))
        seqno = idl.change_seqno
        # Check if system is configured and startup config is restored
        if ops_ntpd_check_system_status() == False:
            return
        else:
            # Get the default ntp config, keys file
            ntpd_info = ops_ntpd_setup_ntpd_default_config()
            # Kill zombie ntpd process and Start a new ntpd daemon
            ops_ntpd_cleanup_ntpd_processes()
            ops_ntpd_start_ntpd(ntpd_info)
            # Get the ntp config
            time.sleep(5)
            ops_ntpd_check_updates_from_ovsdb()
            ntpd_started = True

def ops_ntpd_cleanup_ntpd_processes():
    err, out = ops_ntpd_run_command("ps -A")
    for line in out.splitlines():
        if 'ntpd -c' in line or 'ntpq' in line:
            pid = int(line.split(None, 1)[0])
            os.kill(pid, signal.SIGKILL)
            vlog.dbg("Killing zombie ntpd process pid : ",pid)

def ops_ntpd_init():
    global exiting
    global idl
    global seqno
    global ntpd_started

    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--database', metavar="DATABASE",
                        help="A socket on which ovsdb-server is listening.",
                        dest='database')

    ovs.vlog.add_args(parser)
    ovs.daemon.add_args(parser)
    args = parser.parse_args()
    ovs.vlog.handle_args(args)
    ovs.daemon.handle_args(args)

    if args.database is None:
        remote = def_db
    else:
        remote = args.database
    ops_ntpd_setup_ovsdb_monitoring(remote)
    ovs.daemon.daemonize()
    ovs.unixctl.command_register("exit", "", 0, 0, ops_ntpd_connection_exit_handler, None)
    error, unixctl_server = ovs.unixctl.server.UnixctlServer.create(None)

    if error:
        ovs.util.ovs_fatal(error, "ops_ntpd_helper: could not create "
                                  "unix-ctl server", vlog)
    while ntpd_started is False:
        ops_ntpd_provision_ntpd_daemon()
        time.sleep(2)
    seqno = idl.change_seqno    # Sequence number when we last processed the db
    exiting = False
    while not exiting:
        unixctl_server.run()
        if exiting:
            break
        idl.run()
        if seqno == idl.change_seqno:
            ops_ntpd_sync_updates_to_ovsdb()
            time.sleep(2)
        else:
            vlog.dbg("ops-ntpd-debug main - seqno change from %d to %d "
                     % (seqno, idl.change_seqno))
            ops_ntpd_check_updates_from_ovsdb()
            seqno = idl.change_seqno

    # Daemon exit
    unixctl_server.close()
    if ntpd_process is not None:
        vlog.dbg("ops-ntpd-debug - killing ntpd")
    idl.close()

if __name__ == '__main__':
    try:
        ops_ntpd_init()
    except SystemExit:
        # Let system.exit() calls complete normally
        raise
    except:
        vlog.exception("traceback")
        sys.exit(ovs.daemon.RESTART_EXIT_CODE)
