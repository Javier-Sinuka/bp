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
 *   This file contains the source code for the BPNode CLA In Child Task(s)
 */

/*
** Include Files
*/
#include "bpnode_app.h"
#include "bpnode_cla_in.h"


/*
** Function Definitions
*/

CFE_Status_t BPNode_ClaInCreateTasks(void)
{
    CFE_Status_t Status = CFE_SUCCESS;
    uint32       ContactId;
    char         NameBuff[OS_MAX_API_NAME];
    uint16       TaskPriority;

    /* Create all of the CLA In task(s) */
    for (ContactId = 0; ContactId < BPLIB_MAX_NUM_CONTACTS; ContactId++)
    {
        /* Set up task data for the child task */
        BPNode_AppData.ClaInData[ContactId].TaskData.TaskId = ContactId;
        BPNode_AppData.ClaInData[ContactId].TaskData.PerfId = BPNODE_CLA_IN_PERF_ID_BASE + ContactId;
        BPNode_AppData.ClaInData[ContactId].TaskData.InitEid = BPNODE_CLA_IN_INIT_INF_EID;
        BPNode_AppData.ClaInData[ContactId].TaskData.NotifErrEid = BPNODE_CLA_IN_NOTIF_ERR_EID;
        BPNode_AppData.ClaInData[ContactId].TaskData.ExitEid = BPNODE_CLA_IN_EXIT_CRT_EID;
        BPNode_AppData.ClaInData[ContactId].TaskData.TaskInitFunc = BPNode_ClaIn_TaskInit;
        BPNode_AppData.ClaInData[ContactId].TaskData.TaskMainFunc = BPNode_ClaIn_TaskMain;
        
        strncpy(BPNode_AppData.ClaInData[ContactId].TaskData.Type, "CLA In", OS_MAX_API_NAME);

        snprintf(NameBuff, OS_MAX_API_NAME, "%s_%d", BPNODE_CLA_IN_BASE_NAME, ContactId);
        TaskPriority = BPNODE_CLA_IN_PRIORITY_BASE + ContactId;

        /* Spawn CLA In child task */
        Status = CFE_ES_CreateChildTask(&BPNode_AppData.ClaInData[ContactId].TaskData.CfeTaskId,
                                        NameBuff, BPNode_TaskMain, 0, BPNODE_CLA_IN_STACK_SIZE,
                                        TaskPriority, 0);
        if (Status != CFE_SUCCESS)
        {
            BPLib_EM_SendEvent(BPNODE_CLA_IN_CREATE_ERR_EID, BPLib_EM_EventType_ERROR,
                                "Failed to create child task for CLA In #%d. Error = %d",
                                ContactId, Status);
            break;
        }
    }

    return Status;
}

CFE_Status_t BPNode_ClaIn_TaskInit(uint32 ContactId)
{
    CFE_Status_t     Status = CFE_PSP_SUCCESS;
    BPLib_CLA_Type_t ClaType;

    /* This should never happen, indicates something is wrong with the function pointers */
    if (ContactId >= BPLIB_MAX_NUM_CONTACTS)
    {
        BPLib_EM_SendEvent(BPNODE_CLA_IN_INIT_PTR_CRT_EID, BPLib_EM_EventType_CRITICAL,
                        "Invalid contact ID %d passed into BPNode_ClaIn_TaskInit function pointer.",
                        ContactId);
        return CFE_STATUS_RANGE_ERROR;
    }

    /* Shorten the variable name for the CLA type of the contact */
    ClaType = BPNode_AppData.ConfigPtrs.ContactsConfigPtr->ContactSet[ContactId].CLAType;

    switch (ClaType)
    {
        case BPLib_UDP_CLA:
            #ifdef DEFAULT_UDP_CLA
            /* Get PSP module ID for either the Unix or UDP socket driver */
            Status = CFE_PSP_IODriver_FindByName(BPNODE_CLA_PSP_DRIVER_NAME,
                                                    &BPNode_AppData.ClaInData[ContactId].PspLocation.PspModuleId);
            #endif /* DEFAULT_UDP_CLA */

            if (Status != CFE_PSP_SUCCESS)
            {
                BPLib_EM_SendEvent(BPNODE_CLA_IN_FIND_NAME_ERR_EID, BPLib_EM_EventType_ERROR,
                                    "[CLA In #%d]: Couldn't find I/O driver. Error = %d",
                                    ContactId, Status);
            }
            else
            {
                #ifdef DEFAULT_UDP_CLA
                BPNode_AppData.ClaInData[ContactId].PspLocation.SubsystemId = 1 + (CFE_PSP_GetProcessorId() & 1);

                /* Set direction to input only */
                Status = CFE_PSP_IODriver_Command(&BPNode_AppData.ClaInData[ContactId].PspLocation,
                                                    CFE_PSP_IODriver_SET_DIRECTION,
                                                    CFE_PSP_IODriver_U32ARG(CFE_PSP_IODriver_Direction_INPUT_ONLY));
                #endif /* DEFAULT_UDP_CLA */

                if (Status != CFE_PSP_SUCCESS)
                {
                    BPLib_EM_SendEvent(BPNODE_CLA_IN_CFG_DIR_ERR_EID, BPLib_EM_EventType_ERROR,
                                        "[CLA In #%d]: Couldn't set I/O direction to input. Error = %d",
                                        ContactId,
                                        Status);
                }
            }
            break;

        case BPLib_SB_CLA:
            /* Create ingress pipe */
            Status = CFE_SB_CreatePipe(&(BPNode_AppData.ClaInData[ContactId].IngressPipe),
                                        BPNODE_CLA_INGRESS_PIPE_DEPTH,
                                        "BPNODE_CLA_IN_PIPE");

            if (Status != CFE_SUCCESS)
            {
                BPLib_EM_SendEvent(BPNODE_CLA_IN_CREATE_PIPE_ERR_EID, BPLib_EM_EventType_ERROR,
                                    "[CLA In #%d]: Error creating CLA In task SB pipe, RC = 0x%08lX",
                                    ContactId, (unsigned long)Status);
            }
            else
            {
                /* Put bundles from SB into ingress pipe */
                Status = CFE_SB_Subscribe(CFE_SB_ValueToMsgId(BPNODE_CLA_IN_BUNDLE_MID),
                                            BPNode_AppData.ClaInData[ContactId].IngressPipe);

                if (Status != CFE_SUCCESS)
                {
                    BPLib_EM_SendEvent(BPNODE_CLA_IN_SUB_ERR_EID, BPLib_EM_EventType_ERROR,
                                        "[CLA In #%d]: Error subscribing to CLA In task messages, RC = 0x%08lX",
                                        ContactId, (unsigned long)Status);
                }
                else
                {
                    /* CFE_SUCCESS ~= CFE_PSP_SUCCESS but the logic makes more sense this way */
                    Status = CFE_PSP_SUCCESS;
                }
            }
            break;

        case BPLib_LTP_CLA:
            break;

        case BPLib_EPP_CLA:
            break;

        case BPLib_TCP_CLA:
            break;

        default:
            break;

    }

    return Status;
}

/* Main loop for CLA In task(s) */
void BPNode_ClaIn_TaskMain(uint32 ContactId)
{
    BPLib_Status_t              Status;
    size_t                      BytesIngressed;
    BPLib_CLA_ContactRunState_t RunState;
    size_t                      BundleSize = 0;

    /* This should never happen, indicates something is wrong with the function pointers */
    if (ContactId >= BPLIB_MAX_NUM_CONTACTS)
    {
        BPLib_EM_SendEvent(BPNODE_CLA_IN_MAIN_PTR_CRT_EID, BPLib_EM_EventType_CRITICAL,
                        "Invalid contact ID %d passed into BPNode_ClaIn_TaskMain function pointer.",
                        ContactId);
        return;
    }

    Status = BPLib_CLA_GetContactRunState(ContactId, &RunState);

    /* Ingress bundles only when the contact has been started */
    if (Status == BPLIB_SUCCESS && RunState == BPLIB_CLA_STARTED)
    {
        BytesIngressed = 0;

        do
        {
            Status = BPNode_ClaIn_ProcessBundleInput(ContactId, &BundleSize);
            if (Status == BPLIB_SUCCESS)
            {
                BytesIngressed += BundleSize;
            }
        } while (Status != BPLIB_TIMEOUT && ((BytesIngressed * BPNODE_BITS_PER_BYTE) <
                    BPNode_AppData.ClaInData[ContactId].RateLimit));
    }

    return;
}

/* Receive bundles from network CL and forward ingress bundles to CLA  */
int32 BPNode_ClaIn_ProcessBundleInput(uint32 ContId, size_t *BundleSize)
{
    #ifdef DEFAULT_UDP_CLA
    CFE_PSP_IODriver_ReadPacketBuffer_t RdBuf;
    #endif /* DEFAULT_UDP_CLA */

    int32                               Status;
    BPLib_Status_t                      BpStatus = BPLIB_TIMEOUT;
    CFE_MSG_Message_t*                  MsgPtr;
    BPLib_CLA_Type_t                    ClaType;

    ClaType     = BPNode_AppData.ConfigPtrs.ContactsConfigPtr->ContactSet[ContId].CLAType;
    Status      = CFE_PSP_SUCCESS;
    *BundleSize = 0;

    switch (ClaType)
    {
        case BPLib_UDP_CLA:
            #ifdef DEFAULT_UDP_CLA
            RdBuf.BufferSize = BPNODE_CLA_PSP_INPUT_BUFFER_SIZE;
            RdBuf.BufferMem  = BPNode_AppData.ClaInData[ContId].PSP_Buffer;

            BPLib_PL_PerfLogExit(BPNode_AppData.ClaInData[ContId].TaskData.PerfId);

            Status = CFE_PSP_IODriver_Command(&BPNode_AppData.ClaInData[ContId].PspLocation,
                                                CFE_PSP_IODriver_PACKET_IO_READ,
                                                CFE_PSP_IODriver_VPARG(&RdBuf));

            BPLib_PL_PerfLogEntry(BPNode_AppData.ClaInData[ContId].TaskData.PerfId);
            #endif /* DEFAULT_UDP_CLA */

            #ifdef DEFAULT_UDP_CLA
            if (Status == CFE_PSP_SUCCESS && RdBuf.BufferSize != 0)
            { /* Ingress received bundle to bplib CLA */
                *BundleSize = RdBuf.BufferSize;

                BPLib_PL_PerfLogExit(BPNode_AppData.ClaInData[ContId].TaskData.PerfId);

                BpStatus = BPLib_CLA_Ingress(&BPNode_AppData.BplibInst,
                                            ContId,
                                            BPNode_AppData.ClaInData[ContId].PSP_Buffer,
                                            RdBuf.BufferSize,
                                            0);

                BPLib_PL_PerfLogEntry(BPNode_AppData.ClaInData[ContId].TaskData.PerfId);
            }
            else if (Status != CFE_PSP_ERROR_TIMEOUT)
            {
                BPLib_EM_SendEvent(BPNODE_CLA_IN_IO_READ_ERR_EID,
                                    BPLib_EM_EventType_ERROR,
                                    "[CLA In #%d]: Failed to read packet from UDP socket, RC = %d",
                                    ContId,
                                    Status);
            }
            #else
            if (Status > 0)
            {
                *BundleSize = Status;
                BPLib_PL_PerfLogExit(BPNode_AppData.ClaInData[ContId].TaskData.PerfId);

                BpStatus = BPLib_CLA_Ingress(&BPNode_AppData.BplibInst,
                                                ContId,
                                                BPNode_AppData.ClaInData[ContId].PSP_Buffer,
                                                *BundleSize,
                                                0);

                BPLib_PL_PerfLogEntry(BPNode_AppData.ClaInData[ContId].TaskData.PerfId);
            }
            #endif /* DEFAULT_UDP_CLA */

            break;
        case BPLib_SB_CLA:
            BPLib_PL_PerfLogExit(BPNode_AppData.ClaInData[ContId].TaskData.PerfId);

            /* Read next bundle from SB */
            Status = CFE_SB_ReceiveBuffer((CFE_SB_Buffer_t**) &MsgPtr,
                                            BPNode_AppData.ClaInData[ContId].IngressPipe,
                                            BPNODE_DATA_TIMEOUT_MSEC);

            BPLib_PL_PerfLogEntry(BPNode_AppData.ClaInData[ContId].TaskData.PerfId);

            /* Grab the size of the bundle */
            CFE_MSG_GetSize(MsgPtr, BundleSize);

            if (Status == CFE_SUCCESS && *BundleSize != 0)
            { /* Ingress received bundle to bplib CLA */
                /* Extract the bundle from the space packet */
                BPNode_AppData.ClaInData[ContId].SB_Buffer = CFE_SB_GetUserData(MsgPtr);

                BPLib_PL_PerfLogExit(BPNode_AppData.ClaInData[ContId].TaskData.PerfId);

                BpStatus = BPLib_CLA_Ingress(&BPNode_AppData.BplibInst,
                                            ContId,
                                            BPNode_AppData.ClaInData[ContId].SB_Buffer,
                                            *BundleSize,
                                            0);

                BPLib_PL_PerfLogEntry(BPNode_AppData.ClaInData[ContId].TaskData.PerfId);
            }
            else if (Status != CFE_SB_TIME_OUT)
            {
                BPLib_EM_SendEvent(BPNODE_CLA_IN_RECV_BUFF_ERR_EID,
                                    BPLib_EM_EventType_ERROR,
                                    "[CLA In #%d]: Failed to receive from the SB buffer. Error = %d",
                                    ContId,
                                    Status);
            }

            break;
        case BPLib_LTP_CLA:
            break;
        case BPLib_EPP_CLA:
            break;
        case BPLib_TCP_CLA:
            break;
        default:
            break;
    }

    return BpStatus;
}

BPLib_Status_t BPNode_ClaIn_Setup(uint32 ContactId)
{
    BPLib_Status_t           Status;
    BPLib_CLA_ContactsSet_t* ContactInfo;

    #ifdef DEFAULT_UDP_CLA
    int32           PspStatus;
    char            Str[100];

    PspStatus = CFE_PSP_ERROR_NOT_IMPLEMENTED;
    #endif /* DEFAULT_UDP_CLA */

    Status      = BPLIB_SUCCESS;
    ContactInfo = &(BPNode_AppData.ConfigPtrs.ContactsConfigPtr->ContactSet[ContactId]);

    /* Nothing special needs to happen for an SB contact */
    switch (ContactInfo->CLAType)
    {
        case BPLib_UDP_CLA:
            #ifdef DEFAULT_UDP_CLA
            /* Configure Port Number */
            snprintf(Str, sizeof(Str), "port=%d", ContactInfo->ClaInPort);
            PspStatus = CFE_PSP_IODriver_Command(&BPNode_AppData.ClaInData[ContactId].PspLocation,
                                                    CFE_PSP_IODriver_SET_CONFIGURATION,
                                                    CFE_PSP_IODriver_CONST_STR(Str));

            if (PspStatus != CFE_PSP_SUCCESS)
            {
                BPLib_EM_SendEvent(BPNODE_CLA_IN_CFG_PORT_ERR_EID, BPLib_EM_EventType_ERROR,
                                    "Couldn't configure port number for CLA In #%d. Error = %d",
                                    ContactId,
                                    PspStatus);

                Status = BPLIB_CLA_IO_ERROR;
            }
            #endif /* DEFAULT_UDP_CLA */

            if (Status == BPLIB_SUCCESS)
            {
                #ifdef DEFAULT_UDP_CLA
                /* Configure IP Address */
                snprintf(Str, sizeof(Str), "IpAddr=%s", ContactInfo->ClaInAddr);
                PspStatus = CFE_PSP_IODriver_Command(&BPNode_AppData.ClaInData[ContactId].PspLocation,
                                                        CFE_PSP_IODriver_SET_CONFIGURATION,
                                                        CFE_PSP_IODriver_CONST_STR(Str));

                if (PspStatus != CFE_PSP_SUCCESS)
                {
                    BPLib_EM_SendEvent(BPNODE_CLA_IN_CFG_IP_ERR_EID, BPLib_EM_EventType_ERROR,
                                        "Couldn't configure IP address for CLA In #%d. Error = %d",
                                        ContactId,
                                        PspStatus);

                    Status = BPLIB_CLA_IO_ERROR;
                }
                else
                {
                    OS_printf("CLA In #%d receiving on %s:%d\n", ContactId, ContactInfo->ClaInAddr, ContactInfo->ClaInPort);
                }
                #endif /* DEFAULT_UDP_CLA */
            }

            break;
        case BPLib_SB_CLA:
            break;
        case BPLib_LTP_CLA:
            break;
        case BPLib_EPP_CLA:
            break;
        case BPLib_TCP_CLA:
            break;
        default:
            break;
    }

    return Status;
}

BPLib_Status_t BPNode_ClaIn_Start(uint32 ContactId)
{
    int32            PspStatus;
    BPLib_Status_t   Status;
    BPLib_CLA_Type_t ClaType;

    ClaType = BPNode_AppData.ConfigPtrs.ContactsConfigPtr->ContactSet[ContactId].CLAType;
    Status  = BPLIB_SUCCESS;

    /* Default to a PSP status that will output an error */
    PspStatus = CFE_PSP_ERROR_NOT_IMPLEMENTED;

    switch (ClaType)
    {
        case BPLib_UDP_CLA:
            #ifdef DEFAULT_UDP_CLA
            /* Set I/O to running */
            PspStatus = CFE_PSP_IODriver_Command(&BPNode_AppData.ClaInData[ContactId].PspLocation,
                                                    CFE_PSP_IODriver_SET_RUNNING,
                                                    CFE_PSP_IODriver_U32ARG(true));
            #endif /* DEFAULT_UDP_CLA */

            if (PspStatus != CFE_PSP_SUCCESS)
            {
                BPLib_EM_SendEvent(BPNODE_CLA_IN_CFG_SET_RUN_ERR_EID, BPLib_EM_EventType_ERROR,
                                    "Couldn't set I/O state for CLA In #%d to running. Error = %d",
                                    ContactId,
                                    PspStatus);

                Status = BPLIB_CLA_IO_ERROR;
            }
            break;
        case BPLib_SB_CLA:
            break;
        case BPLib_LTP_CLA:
            break;
        case BPLib_EPP_CLA:
            break;
        case BPLib_TCP_CLA:
            break;
        default:
            break;
    }

    return Status;
}

BPLib_Status_t BPNode_ClaIn_Stop(uint32 ContactId)
{
    BPLib_Status_t   Status;
    int32            PspStatus;
    BPLib_CLA_Type_t ClaType;

    /* Shorten the variable name for the CLA type of the contact */
    ClaType = BPNode_AppData.ConfigPtrs.ContactsConfigPtr->ContactSet[ContactId].CLAType;
    Status  = BPLIB_SUCCESS;

    /* Default to a PSP status that will output an error */
    PspStatus = CFE_PSP_ERROR_NOT_IMPLEMENTED;

    switch (ClaType)
    {
        case BPLib_UDP_CLA:
            #ifdef DEFAULT_UDP_CLA
            /* Set I/O to stop running */
            PspStatus = CFE_PSP_IODriver_Command(&BPNode_AppData.ClaInData[ContactId].PspLocation,
                                                    CFE_PSP_IODriver_SET_RUNNING,
                                                    CFE_PSP_IODriver_U32ARG(false));
            #endif /* DEFAULT_UDP_CLA */

            if (PspStatus != CFE_PSP_SUCCESS)
            {
                BPLib_EM_SendEvent(BPNODE_CLA_IN_CFG_STOP_ERR_EID,
                                    BPLib_EM_EventType_ERROR,
                                    "Couldn't set I/O state to stop for CLA In #%d. Error = %d",
                                    ContactId,
                                    PspStatus);

                Status = BPLIB_CLA_IO_ERROR;
            }
            break;
        case BPLib_SB_CLA:
            break;
        case BPLib_LTP_CLA:
            break;
        case BPLib_EPP_CLA:
            break;
        case BPLib_TCP_CLA:
            break;
        default:
            break;
    }

    return Status;
}

void BPNode_ClaIn_Teardown(uint32 ContactId)
{
    /*
    ** Disestablish CLA
    ** Free all CLA resources
    ** Discard output queue
    ** Delete custody timers
    */

    /*
    switch (CLAType)
    {
        case BPLib_UDP_CLA:
            break;
        case BPLib_SB_CLA:
            break;
        case BPLib_LTP_CLA:
            break;
        case BPLib_EPP_CLA:
            break;
        case BPLib_TCP_CLA:
            break;
        default:
            break;
    */

    return;
}

