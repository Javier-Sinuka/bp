/*
 * NASA Docket No. GSC-19,559-1, and identified as "Delay/Disruption Tolerant Networking 
 * (DTN) Bundle Protocol (BP) v7 Core Flight System (cFS) Application Build 7.0
 *
 * Licensed under the Apache License, Version 2.0 (the "License"); you may not use this 
 * file except in compliance with the License. You may obtain a copy of the License at 
 *
 * http://www.apache.org/licenses/LICENSE-2.0 
 *
 * Unless required by applicable law or agreed to in writing, software distributed under 
 * the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF 
 * ANY KIND, either express or implied. See the License for the specific language 
 * governing permissions and limitations under the License. The copyright notice to be 
 * included in the software is as follows: 
 *
 * Copyright 2025 United States Government as represented by the Administrator of the 
 * National Aeronautics and Space Administration. All Rights Reserved.
 *
 */

/**
 * @file
 *
 * Define  BPNode Event IDs
 */

#ifndef BPNODE_EVENTS_H
#define BPNODE_EVENTS_H

#define BPNODE_RESERVED_EID                     0
#define BPNODE_INIT_INF_EID                     1
#define BPNODE_CC_ERR_EID                       2
#define BPNODE_NOOP_INF_EID                     3
#define BPNODE_MID_ERR_EID                      5
#define BPNODE_CMD_LEN_ERR_EID                  6
#define BPNODE_PIPE_ERR_EID                     7
#define BPNODE_CR_CMD_PIPE_ERR_EID              8
#define BPNODE_CR_WKP_PIPE_ERR_EID              9
#define BPNODE_SUB_CMD_ERR_EID                  10
#define BPNODE_SUB_WKP_ERR_EID                  11
#define BPNODE_TBL_REG_ERR_EID                  12
#define BPNODE_TBL_LD_ERR_EID                   13
#define BPNODE_TBL_ADDR_ERR_EID                 14
#define BPNODE_TBL_MNG_ERR_EID                  15
#define BPNODE_BPLIB_INIT_ERR_EID               16
#define BPNODE_EXIT_CRIT_EID                    17
#define BPNODE_AUTO_ADD_APP_INF_EID             18
#define BPNODE_ADU_START_SUB_DBG_EID            19
#define BPNODE_ADU_STOP_UNSUB_DBG_EID           20
#define BPNODE_DEL_HANDLER_ERR_EID              21
#define BPNODE_TIME_WKP_ERR_EID                 22
#define BPNODE_ADU_OUT_PI_OUT_ERR_EID           23
#define BPNODE_NC_CFG_UPDATE_ERR_EID            24
#define BPNODE_INIT_WORK_NOTIF_ERR_EID          25
#define BPNODE_INIT_INIT_NOTIF_ERR_EID          26
#define BPNODE_INIT_EXIT_NOTIF_ERR_EID          27
#define BPNODE_INIT_NOTIF_ERR_EID               28
#define BPNODE_EXIT_NOTIF_CRT_EID               29
#define BPNODE_TASK_NO_ID_ERR_EID               30
#define BPNODE_TASK_UNK_EXIT_CRIT_EID           31
#define BPNODE_INIT_STOR_NOTIF_ERR_EID          32

/* Event IDs 33-49 reserved for future main task event IDs */

#define BPNODE_ADU_IN_INIT_INF_EID              50
#define BPNODE_ADU_IN_EXIT_CRT_EID              51
#define BPNODE_ADU_IN_NOTIF_ERR_EID             52
#define BPNODE_ADU_IN_INIT_PTR_CRT_EID          53
#define BPNODE_ADU_IN_MAIN_PTR_CRT_EID          54
#define BPNODE_ADU_IN_CR_PIPE_ERR_EID           55
#define BPNODE_ADU_IN_CREATE_ERR_EID            56

/* Event IDs 58-59 reserved for future ADU In task event IDs */

#define BPNODE_ADU_OUT_INIT_INF_EID             60
#define BPNODE_ADU_OUT_NOTIF_ERR_EID            61
#define BPNODE_ADU_OUT_EXIT_CRT_EID             62
#define BPNODE_ADU_OUT_INIT_PTR_CRT_EID         63
#define BPNODE_ADU_OUT_MAIN_PTR_CRT_EID         64
#define BPNODE_ADU_OUT_CREATE_ERR_EID           65

/* Event IDs 66-69 reserved for future ADU Out task event IDs */

#define BPNODE_CLA_IN_INIT_INF_EID              70
#define BPNODE_CLA_IN_NOTIF_ERR_EID             71
#define BPNODE_CLA_IN_EXIT_CRT_EID              72
#define BPNODE_CLA_IN_INIT_PTR_CRT_EID          73
#define BPNODE_CLA_IN_MAIN_PTR_CRT_EID          74
#define BPNODE_CLA_IN_FIND_NAME_ERR_EID         75
#define BPNODE_CLA_IN_CFG_PORT_ERR_EID          76
#define BPNODE_CLA_IN_CFG_IP_ERR_EID            77
#define BPNODE_CLA_IN_CFG_DIR_ERR_EID           78
#define BPNODE_CLA_IN_CFG_SET_RUN_ERR_EID       79
#define BPNODE_CLA_IN_CFG_STOP_ERR_EID          80
#define BPNODE_CLA_IN_CREATE_ERR_EID            81
#define BPNODE_CLA_IN_CREATE_PIPE_ERR_EID       82
#define BPNODE_CLA_IN_SUB_ERR_EID               83
#define BPNODE_CLA_IN_RECV_BUFF_ERR_EID         84
#define BPNODE_CLA_IN_IO_READ_ERR_EID           85
#define BPNODE_CLA_IN_UNSUB_ERR_EID             86

/* Event IDs 87-99 reserved for future CLA In task event IDs */

#define BPNODE_CLA_OUT_INIT_INF_EID            100
#define BPNODE_CLA_OUT_NOTIF_ERR_EID           101
#define BPNODE_CLA_OUT_EXIT_CRT_EID            102
#define BPNODE_CLA_OUT_MAIN_PTR_CRT_EID        103
#define BPNODE_CLA_OUT_INIT_PTR_CRT_EID        104 
#define BPNODE_CLA_OUT_LIB_LOAD_ERR_EID        105
#define BPNODE_CLA_OUT_FIND_NAME_ERR_EID       106
#define BPNODE_CLA_OUT_CFG_PORT_ERR_EID        107
#define BPNODE_CLA_OUT_CFG_IP_ERR_EID          108
#define BPNODE_CLA_OUT_CFG_DIR_ERR_EID         109
#define BPNODE_CLA_OUT_CFG_SET_RUN_ERR_EID     110
#define BPNODE_CLA_OUT_CFG_STOP_ERR_EID        111
#define BPNODE_CLA_OUT_CREATE_ERR_EID          112
#define BPNODE_CLA_OUT_RUN_ERR_EID             113

/* Event IDs 114-129 reserved for future CLA Out task event IDs */

#define BPNODE_GEN_WRKR_INIT_INF_EID           130
#define BPNODE_GEN_WRKR_EXIT_CRT_EID           131
#define BPNODE_GEN_WRKR_NOTIF_ERR_EID          132
#define BPNODE_GEN_WRKR_INIT_PTR_CRT_EID       133
#define BPNODE_GEN_WRKR_MAIN_PTR_CRT_EID       134
#define BPNODE_GEN_WRKR_TASKRUN_ERR_EID        135
#define BPNODE_GEN_WRKR_CREATE_ERR_EID         136
#define BPNODE_GEN_WRKR_REGISTER_ERR_EID       137

/* Event IDs 138-149 reserved for future Generic Worker task event IDs */

#define BPNODE_MAINT_INIT_INF_EID              150
#define BPNODE_MAINT_NOTIF_ERR_EID             151
#define BPNODE_MAINT_EXIT_CRT_EID              152
#define BPNODE_MAINT_CREATE_ERR_EID            153
#define BPNODE_MAINT_EGRESS_ERR_EID            154

#endif /* BPNODE_EVENTS_H */
