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
 *   This file contains the source code for the BPNode ADU In Child Task(s)
 */

/*
** Include Files
*/

#include "bpnode_app.h"
#include "bpnode_adu_in.h"


/*
** Function Definitions
*/

/* Create ADU In tasks */
CFE_Status_t BPNode_AduInCreateTasks(void)
{
    CFE_Status_t Status = CFE_SUCCESS;
    uint32       ChanId;
    uint16       TaskPriority;
    char         Name[OS_MAX_API_NAME];

    for (ChanId = 0; ChanId < BPLIB_MAX_NUM_CHANNELS; ChanId++)
    {
        /* Set up task data for the child task */
        BPNode_AppData.AduInData[ChanId].TaskData.TaskId       = ChanId;
        BPNode_AppData.AduInData[ChanId].TaskData.PerfId       = BPNODE_ADU_IN_PERF_ID_BASE + ChanId;
        BPNode_AppData.AduInData[ChanId].TaskData.InitEid      = BPNODE_ADU_IN_INIT_INF_EID;
        BPNode_AppData.AduInData[ChanId].TaskData.NotifErrEid  = BPNODE_ADU_IN_NOTIF_ERR_EID;
        BPNode_AppData.AduInData[ChanId].TaskData.ExitEid      = BPNODE_ADU_IN_EXIT_CRT_EID;
        BPNode_AppData.AduInData[ChanId].TaskData.TaskInitFunc = BPNode_AduIn_TaskInit;
        BPNode_AppData.AduInData[ChanId].TaskData.TaskMainFunc = BPNode_AduIn_TaskMain;
        BPNode_AppData.AduInData[ChanId].BitsIngressed         = 0;

        snprintf(BPNode_AppData.AduInData[ChanId].TaskData.Name, OS_MAX_API_NAME,
                         "ADU In %d", ChanId);
        snprintf(Name, OS_MAX_API_NAME, "%s_%d", BPNODE_ADU_IN_BASE_NAME, ChanId);
        
        TaskPriority = BPNODE_ADU_IN_PRIORITY_BASE + ChanId;

        /* Spawn ADU In child task */
        Status = CFE_ES_CreateChildTask(&BPNode_AppData.AduInData[ChanId].TaskData.CfeTaskId, 
                            Name, BPNode_TaskMain, 0, BPNODE_ADU_IN_STACK_SIZE, 
                            TaskPriority, 0);
        if (Status != CFE_SUCCESS)
        {
            BPLib_EM_SendEvent(BPNODE_ADU_IN_CREATE_ERR_EID, BPLib_EM_EventType_ERROR,
                            "Failed to create ADU In #%d child task. Error = 0x%08X.",
                            ChanId, Status);
            break;
        }
    }

    return Status;
}

/* Initialization operations for ADU In task(s) */
CFE_Status_t BPNode_AduIn_TaskInit(uint32 ChanId)
{
    CFE_Status_t Status;
    char         NameBuff[OS_MAX_API_NAME];

    /* This should never happen, indicates something is wrong with the function pointers */
    if (ChanId >= BPLIB_MAX_NUM_CHANNELS)
    {
        BPLib_EM_SendEvent(BPNODE_ADU_IN_INIT_PTR_CRT_EID, BPLib_EM_EventType_CRITICAL,
                        "Invalid channel ID %d passed into BPNode_AduIn_TaskInit function pointer.",
                        ChanId);
        return CFE_STATUS_RANGE_ERROR;
    }

    /* Create ADU ingest pipe */
    snprintf(NameBuff, OS_MAX_API_NAME, "%s_%d", BPNODE_ADU_IN_PIPE_BASE_NAME, ChanId);
    Status = CFE_SB_CreatePipe(&BPNode_AppData.AduInData[ChanId].AduPipe,
                                    BPNODE_ADU_PIPE_DEPTH, NameBuff);
    if (Status != CFE_SUCCESS)
    {
        BPLib_EM_SendEvent(BPNODE_ADU_IN_CR_PIPE_ERR_EID, BPLib_EM_EventType_ERROR,
                        "[ADU In #%d]: Error creating SB ADU Pipe, Error = %d",
                        ChanId, Status);
    }

    return Status;
}

/* Wakeup operations for ADU In task(s) */
void BPNode_AduIn_TaskMain(uint32 ChanId)
{
    CFE_Status_t Status = CFE_SUCCESS;
    CFE_SB_Buffer_t *BufPtr = NULL;
    size_t AduSize;

    /* This should never happen, indicates something is wrong with the function pointers */
    if (ChanId >= BPLIB_MAX_NUM_CHANNELS)
    {
        BPLib_EM_SendEvent(BPNODE_ADU_IN_MAIN_PTR_CRT_EID, BPLib_EM_EventType_CRITICAL,
                        "Invalid channel ID %d passed into BPNode_AduIn_TaskMain function pointer.",
                        ChanId);
    }
    /* Check if channel is started */
    else if (BPLib_NC_GetAppState(ChanId) == BPLIB_NC_APP_STATE_STARTED)
    {
        /* Check for ADUs to ingest */
        while (Status == CFE_SUCCESS &&
                (BPNode_AppData.AduInData[ChanId].BitsIngressed <
                BPNode_AppData.BplibInst.ChanCtxt[ChanId].Config.IngressBitsPerCycle))
        {
            BPLib_PL_PerfLogExit(BPNode_AppData.AduInData[ChanId].TaskData.PerfId);

            Status = CFE_SB_ReceiveBuffer(&BufPtr,
                                        BPNode_AppData.AduInData[ChanId].AduPipe,
                                        BPNODE_DATA_TIMEOUT_MSEC);

            BPLib_PL_PerfLogEntry(BPNode_AppData.AduInData[ChanId].TaskData.PerfId);

            if (Status == CFE_SUCCESS && BufPtr != NULL)
            {
                /* Ignore return code, errors reported internally */
                (void) BPA_ADUP_In((void *) BufPtr, ChanId, &AduSize);

                /* Even if bplib rejects the ADU, this ADU's size gets counted */
                BPNode_AppData.AduInData[ChanId].BitsIngressed += (AduSize * BPNODE_BITS_PER_BYTE);
            }
        }

        if (BPNode_AppData.AduInData[ChanId].BitsIngressed < BPNode_AppData.BplibInst.ChanCtxt[ChanId].Config.IngressBitsPerCycle)
        {
            BPNode_AppData.AduInData[ChanId].BitsIngressed = 0;
        }
        else
        {
            BPNode_AppData.AduInData[ChanId].BitsIngressed -= BPNode_AppData.BplibInst.ChanCtxt[ChanId].Config.IngressBitsPerCycle;
        }
    }
    else
    {
        /* Check if the application was recently stopped and the pipe needs to be cleared */
        if (BPNode_AppData.AduInData[ChanId].ClearPipe == true)
        {
            BPLib_PL_PerfLogExit(BPNode_AppData.AduInData[ChanId].TaskData.PerfId);

            while (Status == CFE_SUCCESS)
            {
                Status = CFE_SB_ReceiveBuffer(&BufPtr, BPNode_AppData.AduInData[ChanId].AduPipe,
                                            CFE_SB_POLL);
            }

            BPLib_PL_PerfLogEntry(BPNode_AppData.AduInData[ChanId].TaskData.PerfId);

            BPNode_AppData.AduInData[ChanId].ClearPipe = false;
        }
    }

    return;
}
