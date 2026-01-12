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
 *   This file contains the source code for the BPNode ADU Out Child Task(s)
 */

/*
** Include Files
*/

#include "bpnode_app.h"
#include "bpnode_adu_out.h"


/*
** Function Definitions
*/

/* Create all ADU Out child task(s) */
CFE_Status_t BPNode_AduOutCreateTasks(void)
{
    CFE_Status_t Status = CFE_SUCCESS;
    uint32 ChanId;
    char   NameBuff[OS_MAX_API_NAME];
    uint16 TaskPriority;

    /* Create all of the ADU Out task(s) */
    for (ChanId = 0; ChanId < BPLIB_MAX_NUM_CHANNELS; ChanId++)
    {
        BPNode_AppData.AduOutData[ChanId].TaskData.TaskId       = ChanId;
        BPNode_AppData.AduOutData[ChanId].TaskData.PerfId       = BPNODE_ADU_OUT_PERF_ID_BASE + ChanId;
        BPNode_AppData.AduOutData[ChanId].TaskData.InitEid      = BPNODE_ADU_OUT_INIT_INF_EID;
        BPNode_AppData.AduOutData[ChanId].TaskData.NotifErrEid  = BPNODE_ADU_OUT_NOTIF_ERR_EID;
        BPNode_AppData.AduOutData[ChanId].TaskData.ExitEid      = BPNODE_ADU_OUT_EXIT_CRT_EID;
        BPNode_AppData.AduOutData[ChanId].TaskData.TaskInitFunc = BPNode_AduOut_TaskInit;
        BPNode_AppData.AduOutData[ChanId].TaskData.TaskMainFunc = BPNode_AduOut_TaskMain;
        BPNode_AppData.AduOutData[ChanId].BitsEgressed          = 0;

        snprintf(BPNode_AppData.AduOutData[ChanId].TaskData.Name, OS_MAX_API_NAME,
                         "ADU Out %d", ChanId);

        snprintf(NameBuff, OS_MAX_API_NAME, "%s_%d", BPNODE_ADU_OUT_BASE_NAME, ChanId);
        TaskPriority = BPNODE_ADU_OUT_PRIORITY_BASE + ChanId;

        /* Spawn ADU Out child task */
        Status = CFE_ES_CreateChildTask(&BPNode_AppData.AduOutData[ChanId].TaskData.CfeTaskId,
                                NameBuff, BPNode_TaskMain, 0, BPNODE_ADU_OUT_STACK_SIZE, 
                                TaskPriority, 0);
        if (Status != CFE_SUCCESS)
        {
            BPLib_EM_SendEvent(BPNODE_ADU_OUT_CREATE_ERR_EID, BPLib_EM_EventType_ERROR,
                            "Failed to create ADU Out #%d child task. Error = 0x%08X.",
                            ChanId, Status);
            break;
        }
    }

    return Status;
}

/* Initialization operations for ADU Out task(s) */
CFE_Status_t BPNode_AduOut_TaskInit(uint32 ChanId)
{
    CFE_Status_t Status = CFE_SUCCESS;

    /* This should never happen, indicates something is wrong with the function pointers */
    if (ChanId >= BPLIB_MAX_NUM_CHANNELS)
    {
        BPLib_EM_SendEvent(BPNODE_ADU_OUT_INIT_PTR_CRT_EID, BPLib_EM_EventType_CRITICAL,
                        "Invalid channel ID %d passed into BPNode_AduOut_TaskInit function pointer.",
                        ChanId);
        Status = CFE_STATUS_RANGE_ERROR;
    }
    else
    {
        /* Initialize generic output buffer with a dummy msgid and max possible size */
        CFE_MSG_Init(CFE_MSG_PTR(BPNode_AppData.AduOutData[ChanId].OutBuf.TelemetryHeader), 
                CFE_SB_ValueToMsgId(1), sizeof(BPNode_AduOutBuf_t));
    }

    return Status;
}

/* Main loop for ADU Out task(s) */
void BPNode_AduOut_TaskMain(uint32 ChanId)
{
    BPLib_Status_t BpStatus = BPLIB_SUCCESS;
    size_t AduSize;

    /* This should never happen, indicates something is wrong with the function pointers */
    if (ChanId >= BPLIB_MAX_NUM_CHANNELS)
    {
        BPLib_EM_SendEvent(BPNODE_ADU_OUT_MAIN_PTR_CRT_EID, BPLib_EM_EventType_CRITICAL,
                        "Invalid channel ID %d passed into BPNode_AduOut_TaskMain function pointer.",
                        ChanId);
    }
    /* Check if channel is started */
    else if (BPLib_NC_GetAppState(ChanId) == BPLIB_NC_APP_STATE_STARTED)
    {
        while (BpStatus == BPLIB_SUCCESS &&
                (BPNode_AppData.AduOutData[ChanId].BitsEgressed <
                BPNode_AppData.BplibInst.ChanCtxt[ChanId].Config.EgressBitsPerCycle))
        {
            /* Poll bundle from PI out queue */
            BpStatus = BPA_ADUP_Out(ChanId, BPNODE_DATA_TIMEOUT_MSEC, &AduSize);
            if (BpStatus == BPLIB_SUCCESS)
            {
                BPNode_AppData.AduOutData[ChanId].BitsEgressed += (AduSize * BPNODE_BITS_PER_BYTE);
            }
        }

        if (BPNode_AppData.AduOutData[ChanId].BitsEgressed < BPNode_AppData.BplibInst.ChanCtxt[ChanId].Config.EgressBitsPerCycle)
        {
            BPNode_AppData.AduOutData[ChanId].BitsEgressed = 0;
        }
        else
        {
            BPNode_AppData.AduOutData[ChanId].BitsEgressed -= BPNode_AppData.BplibInst.ChanCtxt[ChanId].Config.EgressBitsPerCycle;
        }
    }

    return;
}
