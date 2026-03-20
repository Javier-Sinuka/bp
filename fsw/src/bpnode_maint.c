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
 * \file
 *   This file contains the source code for the BPNode Maintenance Task
 */

/*
** Include Files
*/

#include "bpnode_app.h"
#include "bpnode_maint.h"

/*
** Function Definitions
*/

CFE_Status_t BPNode_MaintCreateTask(void)
{
    CFE_Status_t Status = CFE_SUCCESS;

    /* Set up task data for the child task */
    BPNode_AppData.MaintData.TaskData.TaskId = 0;   /* Only one maintenace task, this is really just a dummy variable */
    BPNode_AppData.MaintData.TaskData.PerfId = BPNODE_MAINT_PERF_ID;
    BPNode_AppData.MaintData.TaskData.InitEid = BPNODE_MAINT_INIT_INF_EID;
    BPNode_AppData.MaintData.TaskData.NotifErrEid = BPNODE_MAINT_NOTIF_ERR_EID;
    BPNode_AppData.MaintData.TaskData.ExitEid = BPNODE_MAINT_EXIT_CRT_EID;
    BPNode_AppData.MaintData.TaskData.TaskInitFunc = BPNode_Maint_TaskInit;
    BPNode_AppData.MaintData.TaskData.TaskMainFunc = BPNode_Maint_TaskMain;

    strncpy(BPNode_AppData.MaintData.TaskData.Name, "Maintenance Task", OS_MAX_API_NAME);

    /* Spawn Maintenance child task */
    Status = CFE_ES_CreateChildTask(&BPNode_AppData.MaintData.TaskData.CfeTaskId,
                            BPNODE_MAINT_BASE_NAME, BPNode_TaskMain, 0, BPNODE_GEN_WRKR_STACK_SIZE,
                            BPNODE_MAINTENANCE_PRIORITY, 0);
    if (Status != CFE_SUCCESS)
    {
        BPLib_EM_SendEvent(BPNODE_MAINT_CREATE_ERR_EID, BPLib_EM_EventType_ERROR,
                        "Failed to create Maintenance Task. Error = 0x%08X.",
                        Status);
    }

    return Status;
}

CFE_Status_t BPNode_Maint_TaskInit(uint32 TaskId)
{
    return CFE_SUCCESS;
}

void BPNode_Maint_TaskMain(uint32 TaskId)
{
    BPLib_Status_t Status;
    uint32         WorkNotifCount;

    /* Check if main task has indicated that storage should be cleaned up */
    if (BPNode_NotifGetCount(&BPNode_AppData.ChildTaskCleanStorNotif) > 0)
    {
        BPLib_NC_CleanupStorage(&(BPNode_AppData.BplibInst));

        BPNode_NotifUnset(&BPNode_AppData.ChildTaskCleanStorNotif);
    }

    WorkNotifCount = BPNode_NotifGetCount(&BPNode_AppData.ChildStartWorkNotif);

    /* Activities that should only be done once per second */
    if (WorkNotifCount >= (BPNode_AppData.MaintData.LastGarbageCollectCycle + BPNODE_MAX_EXP_WAKEUP_RATE) ||
        WorkNotifCount < BPNode_AppData.MaintData.LastGarbageCollectCycle)
    {
        BPNode_AppData.MaintData.LastGarbageCollectCycle = WorkNotifCount;

        BPLib_NC_RunMaintenanceActivities(&BPNode_AppData.BplibInst);
    }

    /* Load bundles from storage into memory */
    Status = BPLib_STOR_Egress(&BPNode_AppData.BplibInst, BPNODE_MAX_BUNDLES_LOADED);
    if (Status != BPLIB_SUCCESS)
    {
        BPLib_EM_SendEvent(BPNODE_MAINT_EGRESS_ERR_EID, BPLib_EM_EventType_ERROR,
                "[Maintenance Task]: Error loading bundles from storage, RC = %d", Status);
    }
}
