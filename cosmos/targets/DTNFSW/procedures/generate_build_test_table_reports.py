#######################################################################
## generate_cf_test_table_reports
##
## The binary files will be overwritten, so copy them to bin/reports/
#######################################################################

prompt("*** Copy the binary files to bin/reports/")

#bin_dir = "DTNFSW-1/tables/target_node/bin/reports/"
bin_dir = "DTNFSW-1/tables/bin/reports/"
config_dir = "DTNFSW-1/tables/config/"

# Contacts table
def_file = "bpnode_contacts_def.txt"
for tbl_file in [
        "cont_bad_dst1.tbl",
        "cont_bad_dst2.tbl",
        "cont_bad_dst3.tbl",
        "cont_bad_dst4.tbl",
        "cont_bad_dst5.tbl",
        "cont_dup_dst.tbl",
        "cont_erate_lim.tbl",
        "cont_irate_lim.tbl",
        "cont_lg_trg.tbl",
        "cont_nom_no_retrans.tbl",
        "cont_rx_cssize_min.tbl",
        "cont_rx_cstime_60s.tbl",
        "cont_rx_large_trig.tbl",
        "cont_size_trg_max.tbl",
        "cont_size_trg_min.tbl",
        "cont_time_trg_max.tbl",
        "cont_time_trg_min.tbl",
        "cont_timeout_max.tbl",
        "cont_timeout_min.tbl",
        "contact_nominal.tbl",
        "contact_rx_only.tbl",
    ]:
    table = table_create_report(bin_dir+tbl_file, config_dir+def_file)
    #print(table)

# Channel table
def_file = "bpnode_channel_def.txt"
for tbl_file in [
        "chan0_no_cteb.tbl",
        "chan0_serv_64.tbl",
        "chan_bad_crc.tbl",
        "chan_bad_sspdst.tbl",
        "chan_bad_ssprep.tbl",
        "chan_dup_serv.tbl",
        "chan_inv_cteb.tbl",
        "chan_no_extblk.tbl",
        "chan_prev_crc_0.tbl",   ]:
    table = table_create_report(bin_dir+tbl_file, config_dir+def_file)

# MIB PN table
def_file = "bpnode_mib_pn_def.txt"
for tbl_file in [
        "mib_pn_200_64.tbl",
        "mib_pn_blen_0.tbl",
        "mib_pn_blen_200.tbl",
        "mib_pn_invplen.tbl",
        "mib_pn_n2.tbl",
        "mib_pn_n2_caps.tbl",
        "mib_short_life.tbl",
    ]:
    table = table_create_report(bin_dir+tbl_file, config_dir+def_file)

# CF table
def_file = "cf_def_config_def.txt"
for tbl_file in [
        "cf_n2.tbl", 
    ]:
    table = table_create_report(bin_dir+tbl_file, config_dir+def_file)
    #print(table)

# ADUP table
def_file = "bpnode_adup_def.txt"
for tbl_file in [
        "adup_n2.tbl", 
    ]:
    table = table_create_report(bin_dir+tbl_file, config_dir+def_file)
    #print(table)

