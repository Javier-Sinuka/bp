/************************************************************************
 * NASA Docket No. GSC-18,719-1, and identified as “core Flight System: Bootes”
 *
 * Copyright (c) 2020 United States Government as represented by the
 * Administrator of the National Aeronautics and Space Administration.
 * All Rights Reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License"); you may
 * not use this file except in compliance with the License. You may obtain
 * a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 ************************************************************************/

#include "cfe_tbl_filedef.h" /* Required to obtain the CFE_TBL_FILEDEF macro definition */
#include "sch_lab_tbl.h"
#include "cfe_sb.h" /* Required to use the CFE_SB_MSGID_WRAP_VALUE macro */
#include "cfe_msgids.h"

/*
** Include headers for message IDs here
*/
#include "ci_lab_msgids.h"
#include "to_lab_msgids.h"
#ifdef HAVE_SAMPLE_APP
#include "sample_app_msgids.h"
#endif

#include "bpnode_msgids.h"
#include "cf_msgids.h"

#ifdef HAVE_BPACC_FUN
#include "bpacc_fun_msgids.h"
#endif

/*
** SCH Lab schedule table
** When populating this table:
**  1. The entire table is processed (SCH_LAB_MAX_SCHEDULE_ENTRIES) but entries with a
**     packet rate of 0 are skipped
**  2. You can have commented out entries or entries with a packet rate of 0
**  3. If the table grows too big, increase SCH_LAB_MAX_SCHEDULE_ENTRIES
*/

SCH_LAB_ScheduleTable_t SCH_LAB_ScheduleTable = {
            .TickRate = 10,
            .Config   = {
                {CFE_SB_MSGID_WRAP_VALUE(CFE_ES_SEND_HK_MID), 40, 0},
                {CFE_SB_MSGID_WRAP_VALUE(CFE_EVS_SEND_HK_MID), 40, 0},
                {CFE_SB_MSGID_WRAP_VALUE(CFE_TIME_SEND_HK_MID), 40, 0},
                {CFE_SB_MSGID_WRAP_VALUE(CFE_SB_SEND_HK_MID), 40, 0},
                {CFE_SB_MSGID_WRAP_VALUE(CFE_TBL_SEND_HK_MID), 40, 0},
                {CFE_SB_MSGID_WRAP_VALUE(CI_LAB_SEND_HK_MID), 40, 0},
                {CFE_SB_MSGID_WRAP_VALUE(TO_LAB_SEND_HK_MID), 40, 0},
                {CFE_SB_MSGID_WRAP_VALUE(CF_SEND_HK_MID), 40, 0},
#ifdef HAVE_SAMPLE_APP
                {CFE_SB_MSGID_WRAP_VALUE(SAMPLE_APP_SEND_HK_MID), 40, 0},
#endif
                {CFE_SB_MSGID_WRAP_VALUE(BPNODE_CMD_MID),       40, 40}, /* BPNODE_SEND_NODE_MIB_CONFIG_HK_CC */
                {CFE_SB_MSGID_WRAP_VALUE(BPNODE_CMD_MID),       40, 41}, /* BPNODE_SEND_SOURCE_MIB_CONFIG_HK_CC */
                {CFE_SB_MSGID_WRAP_VALUE(BPNODE_CMD_MID),       40, 42}, /* BPNODE_SEND_NODE_MIB_COUNTERS_HK_CC */
                {CFE_SB_MSGID_WRAP_VALUE(BPNODE_CMD_MID),       40, 43}, /* BPNODE_SEND_SOURCE_MIB_COUNTERS_HK_CC */
                {CFE_SB_MSGID_WRAP_VALUE(BPNODE_CMD_MID),       40, 44}, /* BPNODE_SEND_STORAGE_HK_CC */
                {CFE_SB_MSGID_WRAP_VALUE(BPNODE_CMD_MID),       40, 45}, /* BPNODE_SEND_CHANNEL_CONTACT_STAT_HK_CC */
                {CFE_SB_MSGID_WRAP_VALUE(BPNODE_CMD_MID),       40, 46}, /* BPNODE_SEND_NODE_MIB_REPORTS_HK_CC */
                {CFE_SB_MSGID_WRAP_VALUE(BPNODE_WAKEUP_MID),    1, 0},
                {CFE_SB_MSGID_WRAP_VALUE(CF_WAKE_UP_MID),       10, 1},
#ifdef HAVE_BPACC_FUN
                {CFE_SB_MSGID_WRAP_VALUE(BPACC_FUN_SEND_HK_MID), 40, 0},
#endif
}};

/*
** The macro below identifies:
**    1) the data structure type to use as the table image format
**    2) the name of the table to be placed into the cFE Table File Header
**    3) a brief description of the contents of the file image
**    4) the desired name of the table image binary file that is cFE compatible
*/
CFE_TBL_FILEDEF(SCH_LAB_ScheduleTable, SCH_LAB_APP.ScheduleTable, Schedule Lab MsgID Table, sch_lab_table.tbl)
