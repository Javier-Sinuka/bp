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
        BPNode_AppData.ClaInData[ContactId].TaskData.TaskId       = ContactId;
        BPNode_AppData.ClaInData[ContactId].TaskData.PerfId       = BPNODE_CLA_IN_PERF_ID_BASE + ContactId;
        BPNode_AppData.ClaInData[ContactId].TaskData.InitEid      = BPNODE_CLA_IN_INIT_INF_EID;
        BPNode_AppData.ClaInData[ContactId].TaskData.NotifErrEid  = BPNODE_CLA_IN_NOTIF_ERR_EID;
        BPNode_AppData.ClaInData[ContactId].TaskData.ExitEid      = BPNODE_CLA_IN_EXIT_CRT_EID;
        BPNode_AppData.ClaInData[ContactId].TaskData.TaskInitFunc = BPNode_ClaIn_TaskInit;
        BPNode_AppData.ClaInData[ContactId].TaskData.TaskMainFunc = BPNode_ClaIn_TaskMain;
        BPNode_AppData.ClaInData[ContactId].BitsIngressed         = 0;
        
        snprintf(BPNode_AppData.ClaInData[ContactId].TaskData.Name, OS_MAX_API_NAME,
                            "CLA In %d", ContactId);

        snprintf(NameBuff, OS_MAX_API_NAME, "%s_%d", BPNODE_CLA_IN_BASE_NAME, ContactId);
        TaskPriority = BPNODE_CLA_IN_PRIORITY_BASE + ContactId;

        /* Spawn CLA In child task */
        Status = CFE_ES_CreateChildTask(&BPNode_AppData.ClaInData[ContactId].TaskData.CfeTaskId,
                                        NameBuff, BPNode_TaskMain, 0, BPNODE_CLA_IN_STACK_SIZE,
                                        TaskPriority, 0);
        if (Status != CFE_SUCCESS)
        {
            BPLib_EM_SendEvent(BPNODE_CLA_IN_CREATE_ERR_EID, BPLib_EM_EventType_ERROR,
                                "Failed to create child task for CLA In #%d. Error = 0x%08X.",
                                ContactId, Status);
            break;
        }
    }

    return Status;
}

CFE_Status_t BPNode_ClaIn_TaskInit(uint32 ContactId)
{
    CFE_Status_t     Status = CFE_PSP_SUCCESS;
    char             PipeBuff[OS_MAX_API_NAME];

    /* This should never happen, indicates something is wrong with the function pointers */
    if (ContactId >= BPLIB_MAX_NUM_CONTACTS)
    {
        BPLib_EM_SendEvent(BPNODE_CLA_IN_INIT_PTR_CRT_EID, BPLib_EM_EventType_CRITICAL,
                        "Invalid contact ID %d passed into BPNode_ClaIn_TaskInit function pointer.",
                        ContactId);
        return CFE_STATUS_RANGE_ERROR;
    }

    /*
    ** Initialize UDP CLA infrastructure
    */

    #ifdef DEFAULT_UDP_CLA
    /* Get PSP module ID for the UDP socket driver */
    Status = CFE_PSP_IODriver_FindByName(BPNODE_CLA_PSP_DRIVER_NAME,
                            &BPNode_AppData.ClaInData[ContactId].PspLocation.PspModuleId);
    if (Status != CFE_PSP_SUCCESS)
    {
        BPLib_EM_SendEvent(BPNODE_CLA_IN_FIND_NAME_ERR_EID, BPLib_EM_EventType_ERROR,
                            "[CLA In #%d]: Couldn't find I/O driver. Error = %d",
                            ContactId, Status);
        return Status;
    }

    BPNode_AppData.ClaInData[ContactId].PspLocation.SubsystemId = 1 + ContactId;
    
    /* Set direction to input only */
    Status = CFE_PSP_IODriver_Command(&BPNode_AppData.ClaInData[ContactId].PspLocation,
                                        CFE_PSP_IODriver_SET_DIRECTION,
                                        CFE_PSP_IODriver_U32ARG(CFE_PSP_IODriver_Direction_INPUT_ONLY));
    if (Status != CFE_PSP_SUCCESS)
    {
        BPLib_EM_SendEvent(BPNODE_CLA_IN_CFG_DIR_ERR_EID, BPLib_EM_EventType_ERROR,
                            "[CLA In #%d]: Couldn't set I/O direction to input. Error = %d",
                            ContactId, Status);
        return Status;
    }
    #endif /* DEFAULT_UDP_CLA */

    /*
    ** Initialize SB CLA infrastructure
    */

    snprintf(PipeBuff, OS_MAX_API_NAME, "%s_%d", BPNODE_CLA_IN_BASE_NAME, ContactId);
    
    /* Create ingress pipe */
    Status = CFE_SB_CreatePipe(&(BPNode_AppData.ClaInData[ContactId].IngressPipe),
                                BPNODE_CLA_INGRESS_PIPE_DEPTH, PipeBuff);

    if (Status != CFE_SUCCESS)
    {
        BPLib_EM_SendEvent(BPNODE_CLA_IN_CREATE_PIPE_ERR_EID, BPLib_EM_EventType_ERROR,
                            "[CLA In #%d]: Error creating CLA In task SB pipe, RC = 0x%08lX",
                            ContactId, (unsigned long)Status);
    }

    return Status;
}

/* Main loop for CLA In task(s) */
void BPNode_ClaIn_TaskMain(uint32 ContactId)
{
    BPLib_Status_t              Status;
    BPLib_CLA_ContactRunState_t RunState;
    size_t                      BundleSize = 0;
    CFE_SB_Buffer_t            *BufPtr = NULL;

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
        while (Status != BPLIB_TIMEOUT &&
                (BPNode_AppData.ClaInData[ContactId].BitsIngressed <
                BPNode_AppData.ClaInData[ContactId].RateLimit))
        {
            Status = BPNode_ClaIn_ProcessBundleInput(ContactId, &BundleSize);
            if (Status == BPLIB_SUCCESS)
            {
                BPNode_AppData.ClaInData[ContactId].BitsIngressed += (BundleSize * BPNODE_BITS_PER_BYTE);
            }
        }

        if (BPNode_AppData.ClaInData[ContactId].BitsIngressed < BPNode_AppData.ClaInData[ContactId].RateLimit)
        {
            BPNode_AppData.ClaInData[ContactId].BitsIngressed = 0;
        }
        else
        {
            BPNode_AppData.ClaInData[ContactId].BitsIngressed -= BPNode_AppData.ClaInData[ContactId].RateLimit;
        }
    }
    else
    {
        if (BPNode_AppData.ClaInData[ContactId].ClearPipe == true &&
            BPNode_AppData.ClaInData[ContactId].ClaType == BPLib_SB_CLA)
        {
            /* Clear pipe */
            BPLib_PL_PerfLogExit(BPNode_AppData.ClaInData[ContactId].TaskData.PerfId);

            while (Status == CFE_SUCCESS)
            {
                Status = CFE_SB_ReceiveBuffer(&BufPtr, 
                                        BPNode_AppData.ClaInData[ContactId].IngressPipe,
                                        CFE_SB_POLL);
            }

            BPLib_PL_PerfLogEntry(BPNode_AppData.ClaInData[ContactId].TaskData.PerfId);    
        }    
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

    Status      = CFE_PSP_SUCCESS;
    *BundleSize = 0;

    switch (BPNode_AppData.ClaInData[ContId].ClaType)
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

            if (Status == CFE_SUCCESS && *BundleSize > sizeof(CFE_MSG_CommandHeader_t))
            { /* Ingress received bundle to bplib CLA */
                /* Extract the bundle from the space packet */
                BPNode_AppData.ClaInData[ContId].SB_Buffer = CFE_SB_GetUserData(MsgPtr);
                *BundleSize -= sizeof(CFE_MSG_CommandHeader_t);

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
    switch (BPNode_AppData.ClaInData[ContactId].ClaType)
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
    CFE_Status_t     CfeStatus;
    BPLib_Status_t   Status;

    Status  = BPLIB_SUCCESS;

    /* Default to a PSP status that will output an error */
    PspStatus = CFE_PSP_ERROR_NOT_IMPLEMENTED;

    switch (BPNode_AppData.ClaInData[ContactId].ClaType)
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
            /* Subscribe to bundles on ingress pipe */
            CfeStatus = CFE_SB_SubscribeEx(CFE_SB_ValueToMsgId(BPNODE_CLA_IN_BUNDLE_MID),
                                        BPNode_AppData.ClaInData[ContactId].IngressPipe,
                                        CFE_SB_DEFAULT_QOS, BPNODE_CLA_INGRESS_MSG_LIMIT);

            if (CfeStatus != CFE_SUCCESS)
            {
                Status = BPLIB_CLA_IO_ERROR;
                BPLib_EM_SendEvent(BPNODE_CLA_IN_SUB_ERR_EID, BPLib_EM_EventType_ERROR,
                                    "Error subscribing to CLA In %d task messages, RC = 0x%08lX",
                                    ContactId, (unsigned long)CfeStatus);
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

BPLib_Status_t BPNode_ClaIn_Stop(uint32 ContactId)
{
    BPLib_Status_t   Status;
    CFE_Status_t     CfeStatus;
    int32            PspStatus;

    Status  = BPLIB_SUCCESS;

    /* Default to a PSP status that will output an error */
    PspStatus = CFE_PSP_ERROR_NOT_IMPLEMENTED;

    switch (BPNode_AppData.ClaInData[ContactId].ClaType)
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
            /* Unsubscribe to bundles on ingress pipe */
            CfeStatus = CFE_SB_Unsubscribe(CFE_SB_ValueToMsgId(BPNODE_CLA_IN_BUNDLE_MID),
                                        BPNode_AppData.ClaInData[ContactId].IngressPipe);

            if (CfeStatus != CFE_SUCCESS)
            {
                Status = BPLIB_CLA_IO_ERROR;
                BPLib_EM_SendEvent(BPNODE_CLA_IN_UNSUB_ERR_EID, BPLib_EM_EventType_ERROR,
                                    "Error unsubscribing from CLA In %d task messages, RC = 0x%08lX",
                                    ContactId, (unsigned long)CfeStatus);
            }

            BPNode_AppData.ClaInData[ContactId].ClearPipe = true;
            
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
    return;
}

