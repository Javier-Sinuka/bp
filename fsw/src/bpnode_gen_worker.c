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
 *   This file contains the source code for the BPNode Generic Worker Child Task(s)
 */

/*
** Include Files
*/

#include "bpnode_app.h"
#include "bpnode_gen_worker.h"


/*
** Function Definitions
*/

/* Create all Generic Worker child task(s) */
CFE_Status_t BPNode_GenWorkerCreateTasks(void)
{
    CFE_Status_t Status = CFE_SUCCESS;
    uint32 WorkerId;
    char   NameBuff[OS_MAX_API_NAME];
    uint16 TaskPriority;

    /* Create all of the Generic Worker task(s) */
    for (WorkerId = 0; WorkerId < BPNODE_NUM_GEN_WRKR_TASKS; WorkerId++)
    {
        /* Set up task data for the child task */
        BPNode_AppData.GenWorkerData[WorkerId].TaskData.TaskId = WorkerId;
        BPNode_AppData.GenWorkerData[WorkerId].TaskData.PerfId = BPNODE_GEN_WRKR_PERF_ID_BASE + WorkerId;
        BPNode_AppData.GenWorkerData[WorkerId].TaskData.InitEid = BPNODE_GEN_WRKR_INIT_INF_EID;
        BPNode_AppData.GenWorkerData[WorkerId].TaskData.NotifErrEid = BPNODE_GEN_WRKR_NOTIF_ERR_EID;
        BPNode_AppData.GenWorkerData[WorkerId].TaskData.ExitEid = BPNODE_GEN_WRKR_EXIT_CRT_EID;
        BPNode_AppData.GenWorkerData[WorkerId].TaskData.TaskInitFunc = BPNode_GenWorker_TaskInit;
        BPNode_AppData.GenWorkerData[WorkerId].TaskData.TaskMainFunc = BPNode_GenWorker_TaskMain;
        
        snprintf(BPNode_AppData.GenWorkerData[WorkerId].TaskData.Name, OS_MAX_API_NAME, 
                                                            "Generic Worker %d", WorkerId);

        snprintf(NameBuff, OS_MAX_API_NAME, "%s_%d", BPNODE_GEN_WRKR_BASE_NAME, WorkerId);
        TaskPriority = BPNODE_GEN_WRKR_PRIORITY_BASE + WorkerId;

        /* Spawn Generic Worker child task */
        Status = CFE_ES_CreateChildTask(&BPNode_AppData.GenWorkerData[WorkerId].TaskData.CfeTaskId,
                                NameBuff, BPNode_TaskMain, 0, BPNODE_GEN_WRKR_STACK_SIZE, 
                                TaskPriority, 0);
        if (Status != CFE_SUCCESS)
        {
            BPLib_EM_SendEvent(BPNODE_GEN_WRKR_CREATE_ERR_EID, BPLib_EM_EventType_ERROR,
                            "Failed to create Generic Worker #%d child task. Error = 0x%08X.",
                            WorkerId, Status);
            break;
        }
    }

    return Status;
}

/* Task initialization for Generic Worker task(s) */
CFE_Status_t BPNode_GenWorker_TaskInit(uint32 WorkerId)
{
    CFE_Status_t   Status = CFE_SUCCESS;
    BPLib_Status_t BpStatus;

    /* This should never happen, indicates something is wrong with the function pointers */
    if (WorkerId >= BPNODE_NUM_GEN_WRKR_TASKS)
    {
        BPLib_EM_SendEvent(BPNODE_GEN_WRKR_INIT_PTR_CRT_EID, BPLib_EM_EventType_CRITICAL,
                        "Invalid worker ID %d passed into BPNode_GenWorker_TaskInit function pointer.",
                        WorkerId);
        return CFE_STATUS_RANGE_ERROR;
    }

    /* Register the worker with BPLib */
    BpStatus = BPLib_QM_RegisterWorker(&BPNode_AppData.BplibInst, 
                                &BPNode_AppData.GenWorkerData[WorkerId].BPLibWorkerId);
    if (BpStatus != BPLIB_SUCCESS)
    {
        BPLib_EM_SendEvent(BPNODE_GEN_WRKR_REGISTER_ERR_EID, BPLib_EM_EventType_ERROR,
            "[Generic Worker #%d]: Failed to register worker with BPLib. Status = %d",
            WorkerId, BpStatus);
        Status = CFE_STATUS_EXTERNAL_RESOURCE_FAIL;
    }

    return Status;
}

/* Main loop for Generic Worker task(s) */
void BPNode_GenWorker_TaskMain(uint32 WorkerId)
{
    BPLib_Status_t BpStatus;
    size_t         JobsRun = 0;

    /* This should never happen, indicates something is wrong with the function pointers */
    if (WorkerId >= BPNODE_NUM_GEN_WRKR_TASKS)
    {
        BPLib_EM_SendEvent(BPNODE_GEN_WRKR_MAIN_PTR_CRT_EID, BPLib_EM_EventType_CRITICAL,
                        "Invalid worker ID %d passed into BPNode_GenWorker_TaskMain function pointer.",
                        WorkerId);
    }
    else
    {
        #ifdef BPNODE_INCLUDE_PERFORMANCE_DEBUGS
        int64_t StartTime = BPLib_TIME_GetMonotonicTime();
        #endif

        do
        {
            BPLib_PL_PerfLogExit(BPNode_AppData.GenWorkerData[WorkerId].TaskData.PerfId);
            BpStatus = BPLib_QM_WorkerRunJob(&BPNode_AppData.BplibInst, 
                            BPNode_AppData.GenWorkerData[WorkerId].BPLibWorkerId,
                            BPNODE_WAKEUP_WAIT_MSEC);
            BPLib_PL_PerfLogEntry(BPNode_AppData.GenWorkerData[WorkerId].TaskData.PerfId);
            if (BpStatus == BPLIB_SUCCESS)
            {
                JobsRun++;
            }
            else if (BpStatus != BPLIB_TIMEOUT)
            {
                BPLib_EM_SendEvent(BPNODE_GEN_WRKR_TASKRUN_ERR_EID, BPLib_EM_EventType_INFORMATION,
                    "[Generic Worker #%d]: Failed to run job, BPLib RC = %d",
                    WorkerId, BpStatus);
                break;
            }
        } while (BpStatus == BPLIB_SUCCESS && JobsRun < BPNODE_NUM_JOBS_PER_CYCLE);

        #ifdef BPNODE_INCLUDE_PERFORMANCE_DEBUGS
        printf("Processed %ld jobs in %ld msec\n", JobsRun, 
                                BPLib_TIME_GetMonotonicTime() - StartTime);
        #endif
    }

    return;
}
