/*
 * NASA Docket No. GSC-18,587-1 and identified as “The Bundle Protocol Core Flight
 * System Application (BP) v6.5”
 *
 * Copyright © 2020 United States Government as represented by the Administrator of
 * the National Aeronautics and Space Administration. All Rights Reserved.
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
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
    BPNode_AppData.MaintData.TaskData.TaskId = 0;   /* Only one maintenace task */
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

    /* Check if main task has indicated that storage should be cleaned up */
    if (BPNode_NotifGetCount(&BPNode_AppData.ChildTaskCleanStorNotif) > 0)
    {
        BPLib_NC_CleanupStorage(&(BPNode_AppData.BplibInst));

        BPNode_NotifUnset(&BPNode_AppData.ChildTaskCleanStorNotif);
    }

    /* Activities that should only be done once per second */
    if (BPNode_NotifGetCount(&BPNode_AppData.ChildStartWorkNotif) % BPNODE_MAX_EXP_WAKEUP_RATE == 0)
    {
        /* Update time as needed */
        Status = BPLib_TIME_MaintenanceActivities();

        if (Status != BPLIB_SUCCESS)
        {
            BPLib_EM_SendEvent(BPNODE_TIME_WKP_ERR_EID, BPLib_EM_EventType_ERROR,
                                "[Maintenance Task]: Error doing time maintenance activities, RC = %d", Status);
        }

        /* Flush any bundles pending storage - error event issued by bplib */
        (void) BPLib_STOR_FlushPending(&BPNode_AppData.BplibInst);

        /* Garbage Collect: Ideally, you should do this if nothing is busy. For B 7.0
        ** Calling it once a second is enough, but this comes with the caveat that removing bundles
        ** from storage will take several cycles. There may be optimizations that can be done here
        ** such as detecting system "idle" time and doing a bulk delete then.
        */
        BPLib_STOR_GarbageCollect(&BPNode_AppData.BplibInst);
    }
}
