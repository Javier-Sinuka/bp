#######################################################################
## generate_test_table_reports
##
## The binary files will be overwritten, so copy them to bin/reports/
##
#######################################################################

prompt("*** Copy the binary files to bin/reports/")

import os
from pathlib import Path

#bin_dir = "DTNFSW-1/tables/target_node/bin/reports/"
bin_dir = "DTNFSW-1/tables/bin/reports/"
config_dir = "DTNFSW-1/tables/config/"

# Get the directory path on the host 
#directory_path = Path(os.getenv("HOST_HOME")+"/table_reports")
report_host_dir = Path(os.getenv("HOST_HOME")+"/cosmos/plugins/DEFAULT/targets_modified/"+bin_dir)
directory_path = Path(report_host_dir)

# Contacts table
def_file = "bpnode_contacts_def.txt"
for tbl in directory_path.glob("cont*.tbl"):
    tbl_file = Path(tbl).name
    print(f"Processing {tbl_file}")
    table = table_create_report(bin_dir+tbl_file, config_dir+def_file)
    #print(table)

# Channel table
def_file = "bpnode_channel_def.txt"
for tbl in directory_path.glob("chan*.tbl"):
    tbl_file = Path(tbl).name
    print(f"Processing {tbl_file}")
    table = table_create_report(bin_dir+tbl_file, config_dir+def_file)

# MIB PN table
def_file = "bpnode_mib_pn_def.txt"
for tbl in directory_path.glob("mib*.tbl"):
    tbl_file = Path(tbl).name
    print(f"Processing {tbl_file}")
    table = table_create_report(bin_dir+tbl_file, config_dir+def_file)


# CF table
def_file = "cf_def_config_def.txt"
for tbl in directory_path.glob("cf*.tbl"):
    tbl_file = Path(tbl).name
    print(f"Processing {tbl_file}")
    table = table_create_report(bin_dir+tbl_file, config_dir+def_file)


# ADUP table
def_file = "bpnode_adup_def.txt"
for tbl in directory_path.glob("adu*.tbl"):
    tbl_file = Path(tbl).name
    print(f"Processing {tbl_file}")
    table = table_create_report(bin_dir+tbl_file, config_dir+def_file)


