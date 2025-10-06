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
 *  Unit tests for bpnode_cla_in.c
 */

/*
** Include Files
*/

#include "bpnode_cla_in.h"
#include "bpnode_test_utils.h"


/*
** Function Definitions
*/

/* Test BPNode_ClaInCreateTasks when everything succeeds */
void Test_BPNode_ClaInCreateTasks_Nominal(void)
{
    UtAssert_INT32_EQ(BPNode_ClaInCreateTasks(), CFE_SUCCESS);

    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 0);
    UtAssert_STUB_COUNT(CFE_ES_CreateChildTask, BPLIB_MAX_NUM_CONTACTS);
}

/* Test BPNode_ClaInCreateTasks when the child task creation fails */
void Test_BPNode_ClaInCreateTasks_TaskCrErr(void)
{
    UT_SetDeferredRetcode(UT_KEY(CFE_ES_CreateChildTask), 1, CFE_ES_ERR_CHILD_TASK_CREATE);

    UtAssert_INT32_EQ(BPNode_ClaInCreateTasks(), CFE_ES_ERR_CHILD_TASK_CREATE);

    UtAssert_INT32_EQ(context_BPLib_EM_SendEvent[0].EventID, BPNODE_CLA_IN_CREATE_ERR_EID);
    UtAssert_STRINGBUF_EQ("Failed to create child task for CLA In #%d. Error = 0x%08X.",
                            BPLIB_EM_EXPANDED_EVENT_SIZE,
                            context_BPLib_EM_SendEvent[0].Spec,
                            BPLIB_EM_EXPANDED_EVENT_SIZE);
    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 1);
    UtAssert_STUB_COUNT(CFE_ES_CreateChildTask, 1);
}

/* Test BPNode_ClaIn_TaskInit when the PSP module can't be found */
void Test_BPNode_ClaIn_TaskInit_FindByNameErr(void)
{
    UT_SetDeferredRetcode(UT_KEY(CFE_PSP_IODriver_FindByName), 1, CFE_PSP_ERROR);

    UtAssert_INT32_EQ(BPNode_ClaIn_TaskInit(0), CFE_PSP_ERROR);

    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 1);
    UtAssert_INT32_EQ(context_BPLib_EM_SendEvent[0].EventID, BPNODE_CLA_IN_FIND_NAME_ERR_EID);
    UtAssert_STRINGBUF_EQ("[CLA In #%d]: Couldn't find I/O driver. Error = %d",
                            BPLIB_EM_EXPANDED_EVENT_SIZE,
                            context_BPLib_EM_SendEvent[0].Spec,
                            BPLIB_EM_EXPANDED_EVENT_SIZE);

    UtAssert_STUB_COUNT(CFE_PSP_IODriver_FindByName, 1);
    UtAssert_STUB_COUNT(CFE_PSP_IODriver_Command, 0);
}

void Test_BPNode_ClaIn_TaskInit_DirErr(void)
{
    UT_SetDeferredRetcode(UT_KEY(CFE_PSP_IODriver_Command), 1, CFE_PSP_ERROR);

    UtAssert_INT32_EQ(BPNode_ClaIn_TaskInit(0), CFE_PSP_ERROR);

    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 1);
    UtAssert_INT32_EQ(context_BPLib_EM_SendEvent[0].EventID, BPNODE_CLA_IN_CFG_DIR_ERR_EID);
    UtAssert_STRINGBUF_EQ("[CLA In #%d]: Couldn't set I/O direction to input. Error = %d",
                            BPLIB_EM_EXPANDED_EVENT_SIZE,
                            context_BPLib_EM_SendEvent[0].Spec,
                            BPLIB_EM_EXPANDED_EVENT_SIZE);

    UtAssert_STUB_COUNT(CFE_PSP_IODriver_Command, 1);
}


void Test_BPNode_ClaIn_TaskInit_CreatePipeErr(void)
{
    uint32 ContactNum = 0;

    UT_SetDefaultReturnValue(UT_KEY(CFE_SB_CreatePipe), CFE_SB_BAD_ARGUMENT);

    BPNode_AppData.ConfigPtrs.ContactsConfigPtr->ContactSet[ContactNum].CLAType = BPLib_SB_CLA;
    UtAssert_EQ(CFE_Status_t, BPNode_ClaIn_TaskInit(ContactNum), CFE_SB_BAD_ARGUMENT);

    BPNode_Test_Verify_Event(0, BPNODE_CLA_IN_CREATE_PIPE_ERR_EID,
                                "[CLA In #%d]: Error creating CLA In task SB pipe, RC = 0x%08lX");
}

/* Test BPNode_ClaIn_TaskInit when the contact ID is invalid */
void Test_BPNode_ClaIn_TaskInit_IdErr(void)
{
    uint32 ContactId = BPLIB_MAX_NUM_CONTACTS;

    UtAssert_INT32_EQ(BPNode_ClaIn_TaskInit(ContactId), CFE_STATUS_RANGE_ERROR);

    BPNode_Test_Verify_Event(0, BPNODE_CLA_IN_INIT_PTR_CRT_EID,
                                "Invalid contact ID %d passed into BPNode_ClaIn_TaskInit function pointer.");
    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 1);
    UtAssert_STUB_COUNT(CFE_PSP_IODriver_FindByName, 0);
}

/* Test BPNode_ClaIn_TaskInit on nominal UDP case */
void Test_BPNode_ClaIn_TaskInit_UdpNom(void)
{
    uint32 ContactNum = 0;

    BPNode_AppData.ConfigPtrs.ContactsConfigPtr->ContactSet[ContactNum].CLAType = BPLib_UDP_CLA;
    UtAssert_EQ(CFE_Status_t, BPNode_ClaIn_TaskInit(ContactNum), CFE_PSP_SUCCESS);

    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 0);
}

/* Test BPNode_ClaIn_TaskInit on nominal SB case */
void Test_BPNode_ClaIn_TaskInit_SbNom(void)
{
    uint32 ContactNum = 0;

    BPNode_AppData.ConfigPtrs.ContactsConfigPtr->ContactSet[ContactNum].CLAType = BPLib_SB_CLA;
    UtAssert_EQ(CFE_Status_t, BPNode_ClaIn_TaskInit(ContactNum), CFE_PSP_SUCCESS);

    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 0);
}

/* Test BPNode_ClaIn_TaskInit on nominal LTP case */
void Test_BPNode_ClaIn_TaskInit_LtpNom(void)
{
    uint32 ContactNum = 0;

    BPNode_AppData.ConfigPtrs.ContactsConfigPtr->ContactSet[ContactNum].CLAType = BPLib_LTP_CLA;
    UtAssert_EQ(CFE_Status_t, BPNode_ClaIn_TaskInit(ContactNum), CFE_PSP_SUCCESS);

    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 0);
}

/* Test BPNode_ClaIn_TaskInit on nominal EPP case */
void Test_BPNode_ClaIn_TaskInit_EppNom(void)
{
    uint32 ContactNum = 0;

    BPNode_AppData.ConfigPtrs.ContactsConfigPtr->ContactSet[ContactNum].CLAType = BPLib_EPP_CLA;
    UtAssert_EQ(CFE_Status_t, BPNode_ClaIn_TaskInit(ContactNum), CFE_PSP_SUCCESS);

    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 0);
}

/* Test BPNode_ClaIn_TaskInit on nominal TCPCL case */
void Test_BPNode_ClaIn_TaskInit_TcpNom(void)
{
    uint32 ContactNum = 0;

    BPNode_AppData.ConfigPtrs.ContactsConfigPtr->ContactSet[ContactNum].CLAType = BPLib_TCP_CLA;
    UtAssert_EQ(CFE_Status_t, BPNode_ClaIn_TaskInit(ContactNum), CFE_PSP_SUCCESS);

    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 0);
}

/* Test BPNode_ClaIn_TaskInit on default case */
void Test_BPNode_ClaIn_TaskInit_Default(void)
{
    uint32 ContactNum = 0;

    BPNode_AppData.ConfigPtrs.ContactsConfigPtr->ContactSet[ContactNum].CLAType = 0xff;
    UtAssert_EQ(CFE_Status_t, BPNode_ClaIn_TaskInit(ContactNum), CFE_PSP_SUCCESS);

    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 0);
}

void Test_BPNode_ClaIn_Setup_UdpNom(void)
{
#ifdef DEFAULT_UDP_CLA
    uint32 ContactId = 0;

    strcpy(BPNode_AppData.ConfigPtrs.ContactsConfigPtr->ContactSet[ContactId].ClaInAddr, "0.0.0.0");
    BPNode_AppData.ConfigPtrs.ContactsConfigPtr->ContactSet[ContactId].ClaInPort = 0;
    BPNode_AppData.ClaInData[ContactId].ClaType = BPLib_UDP_CLA;

    /* Force called function to return values that will create a success return value */
    UT_SetDefaultReturnValue(UT_KEY(CFE_PSP_IODriver_Command), CFE_PSP_SUCCESS);

    /* Call function under test and verify return status */
    UtAssert_EQ(BPLib_Status_t, BPNode_ClaIn_Setup(ContactId), BPLIB_SUCCESS);
#endif /* DEFAULT_UDP_CLA */
}

void Test_BPNode_ClaIn_Setup_SbNom(void)
{
    uint32 ContactId = 0;

    BPNode_AppData.ClaInData[ContactId].ClaType = BPLib_SB_CLA;

    UtAssert_EQ(BPLib_Status_t, BPNode_ClaIn_Setup(ContactId), BPLIB_SUCCESS);
}

void Test_BPNode_ClaIn_Setup_LtpNom(void)
{
    uint32 ContactId = 0;

    BPNode_AppData.ClaInData[ContactId].ClaType = BPLib_LTP_CLA;

    UtAssert_EQ(BPLib_Status_t, BPNode_ClaIn_Setup(ContactId), BPLIB_SUCCESS);
}

void Test_BPNode_ClaIn_Setup_EppNom(void)
{
    uint32 ContactId = 0;

    BPNode_AppData.ClaInData[ContactId].ClaType = BPLib_EPP_CLA;

    UtAssert_EQ(BPLib_Status_t, BPNode_ClaIn_Setup(ContactId), BPLIB_SUCCESS);
}

void Test_BPNode_ClaIn_Setup_TcpNom(void)
{
    uint32 ContactId = 0;

    BPNode_AppData.ClaInData[ContactId].ClaType = BPLib_TCP_CLA;

    UtAssert_EQ(BPLib_Status_t, BPNode_ClaIn_Setup(ContactId), BPLIB_SUCCESS);
}

void Test_BPNode_ClaIn_Setup_Default(void)
{
    uint32 ContactId = 0;

    BPNode_AppData.ClaInData[ContactId].ClaType = 0xff;

    UtAssert_EQ(BPLib_Status_t, BPNode_ClaIn_Setup(ContactId), BPLIB_SUCCESS);
}

void Test_BPNode_ClaIn_Setup_PortErr(void)
{
#ifdef DEFAULT_UDP_CLA
    uint32 ContactId = 0;

    strcpy(BPNode_AppData.ConfigPtrs.ContactsConfigPtr->ContactSet[ContactId].ClaInAddr, "0.0.0.0");
    BPNode_AppData.ConfigPtrs.ContactsConfigPtr->ContactSet[ContactId].ClaInPort = 0;

    UT_SetDeferredRetcode(UT_KEY(CFE_PSP_IODriver_Command), 1, CFE_PSP_ERROR);

    UtAssert_INT32_EQ(BPNode_ClaIn_Setup(ContactId), BPLIB_CLA_IO_ERROR);

    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 1);
    UtAssert_INT32_EQ(context_BPLib_EM_SendEvent[0].EventID, BPNODE_CLA_IN_CFG_PORT_ERR_EID);
    UtAssert_STRINGBUF_EQ("Couldn't configure port number for CLA In #%d. Error = %d",
                            BPLIB_EM_EXPANDED_EVENT_SIZE,
                            context_BPLib_EM_SendEvent[0].Spec,
                            BPLIB_EM_EXPANDED_EVENT_SIZE);

    UtAssert_STUB_COUNT(CFE_PSP_IODriver_Command, 1);
#endif /* DEFAULT_UDP_CLA */
}

void Test_BPNode_ClaIn_Setup_IpErr(void)
{
#ifdef DEFAULT_UDP_CLA
    uint32 ContactId = 0;

    strcpy(BPNode_AppData.ConfigPtrs.ContactsConfigPtr->ContactSet[ContactId].ClaInAddr, "0.0.0.0");
    BPNode_AppData.ConfigPtrs.ContactsConfigPtr->ContactSet[ContactId].ClaInPort = 0;

    UT_SetDeferredRetcode(UT_KEY(CFE_PSP_IODriver_Command), 2, CFE_PSP_ERROR);

    UtAssert_INT32_EQ(BPNode_ClaIn_Setup(ContactId), BPLIB_CLA_IO_ERROR);

    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 1);
    UtAssert_INT32_EQ(context_BPLib_EM_SendEvent[0].EventID, BPNODE_CLA_IN_CFG_IP_ERR_EID);
    UtAssert_STRINGBUF_EQ("Couldn't configure IP address for CLA In #%d. Error = %d",
                            BPLIB_EM_EXPANDED_EVENT_SIZE,
                            context_BPLib_EM_SendEvent[0].Spec,
                            BPLIB_EM_EXPANDED_EVENT_SIZE);

    UtAssert_STUB_COUNT(CFE_PSP_IODriver_Command, 2);
#endif /* DEFAULT_UDP_CLA */
}

/* Test BPNode_ClaIn_TaskMain when app state is started and one CLA is received */
void Test_BPNode_ClaIn_TaskMain_Nominal(void)
{
    uint32_t                    ContactId;
    BPLib_CLA_ContactRunState_t RunState;
    BPLib_CLA_ContactRunState_t RunState2 = BPLIB_CLA_EXITED;

    ContactId = 0;
    RunState  = BPLIB_CLA_STOPPED;

    /* Test setup */
    UT_SetDataBuffer(UT_KEY(BPLib_CLA_GetContactRunState), &RunState, sizeof(RunState), false); /* Exits the run loop */
    UT_SetDataBuffer(UT_KEY(BPLib_CLA_GetContactRunState), &RunState2, sizeof(RunState2), false); /* Exits the run loop */

    UtAssert_VOIDCALL(BPNode_ClaIn_TaskMain(ContactId));

    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 0);
}

/* Test BPNode_ClaIn_TaskMain when the SB pipe needs flushing */
void Test_BPNode_ClaIn_TaskMain_ClearPipe(void)
{
    uint32_t                    ContactId = 0;
    BPLib_CLA_ContactRunState_t RunState = BPLIB_CLA_STOPPED;

    BPNode_AppData.ClaInData[ContactId].ClearPipe = true;
    BPNode_AppData.ClaInData[ContactId].ClaType = BPLib_SB_CLA;

    /* Test setup */
    UT_SetDataBuffer(UT_KEY(BPLib_CLA_GetContactRunState), &RunState, sizeof(RunState), false);
    UT_SetDeferredRetcode(UT_KEY(CFE_SB_ReceiveBuffer), 1, CFE_SUCCESS);
    UT_SetDeferredRetcode(UT_KEY(CFE_SB_ReceiveBuffer), 1, CFE_SB_NO_MESSAGE);

    UtAssert_VOIDCALL(BPNode_ClaIn_TaskMain(ContactId));

    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 0);
    UtAssert_STUB_COUNT(CFE_SB_ReceiveBuffer, 2);
}

/* Test BPNode_ClaIn_TaskMain when clear pipe is marked but the CLA type is not SB */
void Test_BPNode_ClaIn_TaskMain_NoClearPipe(void)
{
    uint32_t                    ContactId = 0;
    BPLib_CLA_ContactRunState_t RunState = BPLIB_CLA_STOPPED;

    BPNode_AppData.ClaInData[ContactId].ClearPipe = true;
    BPNode_AppData.ClaInData[ContactId].ClaType = BPLib_UDP_CLA;

    /* Test setup */
    UT_SetDataBuffer(UT_KEY(BPLib_CLA_GetContactRunState), &RunState, sizeof(RunState), false);
    UT_SetDeferredRetcode(UT_KEY(CFE_SB_ReceiveBuffer), 1, CFE_SUCCESS);
    UT_SetDeferredRetcode(UT_KEY(CFE_SB_ReceiveBuffer), 1, CFE_SB_NO_MESSAGE);

    UtAssert_VOIDCALL(BPNode_ClaIn_TaskMain(ContactId));

    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 0);
    UtAssert_STUB_COUNT(CFE_SB_ReceiveBuffer, 0);
}

/* Test BPNode_ClaIn_TaskMain when the contact ID is invalid */
void Test_BPNode_ClaIn_TaskMain_IdErr(void)
{
    uint32 ContactId = BPLIB_MAX_NUM_CONTACTS;

    UtAssert_VOIDCALL(BPNode_ClaIn_TaskMain(ContactId));

    BPNode_Test_Verify_Event(0, BPNODE_CLA_IN_MAIN_PTR_CRT_EID,
                                "Invalid contact ID %d passed into BPNode_ClaIn_TaskMain function pointer.");
    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 1);
    UtAssert_STUB_COUNT(BPLib_CLA_GetContactRunState, 0);
}

/* Test BPNode_ClaIn_TaskMain when ingress service is disabled */
void Test_BPNode_ClaIn_TaskMain_NoIngress(void)
{
    uint32_t                    ContactId;
    BPLib_CLA_ContactRunState_t RunState;

    ContactId = 0;
    RunState  = BPLIB_CLA_EXITED;

    /* Test setup */
    UT_SetDataBuffer(UT_KEY(BPLib_CLA_GetContactRunState), &RunState, sizeof(BPLib_CLA_ContactRunState_t), false);

    UtAssert_VOIDCALL(BPNode_ClaIn_TaskMain(ContactId));

    UtAssert_STUB_COUNT(BPLib_CLA_GetContactRunState, 1);
    UtAssert_STUB_COUNT(BPNode_ClaIn_ProcessBundleInput, 0);
}

/* Test BPNode_ClaIn_TaskMain when getting the contact state fails */
void Test_BPNode_ClaIn_TaskMain_StateErr(void)
{
    uint32                      ContactId;
    BPLib_CLA_ContactRunState_t RunState;

    ContactId = 0;
    RunState = BPLIB_CLA_STARTED;

    /* Test setup */
    UT_SetDataBuffer(UT_KEY(BPLib_CLA_GetContactRunState), &RunState, sizeof(BPLib_CLA_ContactRunState_t), false);
    UT_SetDefaultReturnValue(UT_KEY(BPLib_CLA_GetContactRunState), BPLIB_ERROR);

    UtAssert_VOIDCALL(BPNode_ClaIn_TaskMain(ContactId));

    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 0);
    UtAssert_STUB_COUNT(CFE_PSP_IODriver_Command, 0);
}

void Test_BPNode_ClaIn_TaskMain_FailedProcBundle(void)
{
    uint32_t                    ContactId;
    BPLib_CLA_ContactRunState_t RunState;

    ContactId = 0;
    RunState  = BPLIB_CLA_STARTED;

    /* Test setup */
    UT_SetDataBuffer(UT_KEY(BPLib_CLA_GetContactRunState), &RunState, sizeof(BPLib_CLA_ContactRunState_t), false);
    UT_SetDefaultReturnValue(UT_KEY(CFE_PSP_IODriver_Command), CFE_PSP_ERROR);

    UtAssert_VOIDCALL(BPNode_ClaIn_TaskMain(ContactId));

    UtAssert_STUB_COUNT(CFE_PSP_IODriver_Command, 1);
}

void Test_BPNode_ClaIn_TaskMain_OneBundle(void)
{
    uint32_t                    ContactId;
    BPLib_CLA_ContactRunState_t RunState;

    ContactId = 0;
    RunState = BPLIB_CLA_STARTED;

    /* Test setup */
    UT_SetDataBuffer(UT_KEY(BPLib_CLA_GetContactRunState), &RunState, sizeof(BPLib_CLA_ContactRunState_t), false);
    UT_SetDefaultReturnValue(UT_KEY(BPLib_CLA_GetContactRunState), BPLIB_SUCCESS);

    UT_SetDeferredRetcode(UT_KEY(CFE_PSP_IODriver_Command), 1, CFE_PSP_SUCCESS);
    UT_SetDeferredRetcode(UT_KEY(CFE_PSP_IODriver_Command), 1, CFE_PSP_ERROR_TIMEOUT);

    BPNode_AppData.ClaInData[ContactId].RateLimit = 80000;

    UtAssert_VOIDCALL(BPNode_ClaIn_TaskMain(ContactId));

    UtAssert_STUB_COUNT(BPLib_CLA_Ingress, 1);
    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 0);
}

void Test_BPNode_ClaIn_TaskMain_MaxLimit(void)
{
    uint32_t                    ContactId;
    BPLib_CLA_ContactRunState_t RunState;

    ContactId = 0;
    RunState = BPLIB_CLA_STARTED;

    /* Test setup */
    UT_SetDataBuffer(UT_KEY(BPLib_CLA_GetContactRunState), &RunState, sizeof(BPLib_CLA_ContactRunState_t), false);
    UT_SetDefaultReturnValue(UT_KEY(BPLib_CLA_GetContactRunState), BPLIB_SUCCESS);
    UT_SetDefaultReturnValue(UT_KEY(CFE_PSP_IODriver_Command), BPLIB_SUCCESS);

    /* Rate limit will be reached by two bundles of max default size */
    BPNode_AppData.ClaInData[ContactId].RateLimit = BPLIB_MAX_BUNDLE_LEN * 2 * 8;

    UtAssert_VOIDCALL(BPNode_ClaIn_TaskMain(ContactId));

    UtAssert_STUB_COUNT(CFE_PSP_IODriver_Command, 2);
    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 0);
}

void Test_BPNode_ClaIn_TaskMain_RateLimitedOver(void)
{
    uint32 ContactId         = 0;
    size_t OrigBitsIngressed = 5000;

    /* Test setup */
    UT_SetDefaultReturnValue(UT_KEY(BPLib_CLA_GetContactRunState), BPLIB_CLA_STARTED);
    BPNode_AppData.ClaInData[ContactId].BitsIngressed = OrigBitsIngressed;
    BPNode_AppData.ClaInData[ContactId].RateLimit     = 1000;

    UtAssert_VOIDCALL(BPNode_ClaIn_TaskMain(ContactId));

    UtAssert_EQ(size_t,
                BPNode_AppData.ClaInData[ContactId].BitsIngressed,
                OrigBitsIngressed - BPNode_AppData.ClaInData[ContactId].RateLimit);

    UtAssert_STUB_COUNT(BPNode_ClaIn_ProcessBundleInput, 0);
}

void Test_BPNode_ClaIn_TaskMain_RateLimitedUnder(void)
{
    uint32 ContactId = 0;

    /* Test setup */
    UT_SetDefaultReturnValue(UT_KEY(BPLib_CLA_GetContactRunState), BPLIB_CLA_STARTED);
    BPNode_AppData.ClaInData[ContactId].BitsIngressed = 1010;
    BPNode_AppData.ClaInData[ContactId].RateLimit     = 1000;

    UtAssert_VOIDCALL(BPNode_ClaIn_TaskMain(ContactId));

    UtAssert_EQ(size_t,
                BPNode_AppData.ClaInData[ContactId].BitsIngressed,
                0);

    UtAssert_STUB_COUNT(BPNode_ClaIn_ProcessBundleInput, 0);
}

void Test_BPNode_ClaIn_ProcessBundleInput_UdpNom(void)
{
    uint8 ContactId;
    size_t BundleSize;

    /* UDP case */
    ContactId = 0;
    BPNode_AppData.ClaInData[ContactId].ClaType = BPLib_UDP_CLA;

    UtAssert_UINT32_EQ(BPNode_ClaIn_ProcessBundleInput(ContactId, &BundleSize), CFE_SUCCESS);

    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 0);
}

void Test_BPNode_ClaIn_ProcessBundleInput_SbNom(void)
{
    uint8  ContactId;
    size_t MsgSize;
    size_t InputMsgSize;
    CFE_SB_Buffer_t Buf;
    CFE_SB_Buffer_t* BufPtr;

    BufPtr    = &Buf;
    ContactId = 0;
    MsgSize   = 42;
    BPNode_AppData.ClaInData[ContactId].ClaType = BPLib_SB_CLA;

    UT_SetDataBuffer(UT_KEY(CFE_MSG_GetSize), &MsgSize, sizeof(size_t), false);
    UT_SetDataBuffer(UT_KEY(CFE_SB_ReceiveBuffer), &BufPtr, sizeof(BufPtr), false);

    /* Run function under test */
    UtAssert_EQ(CFE_Status_t, BPNode_ClaIn_ProcessBundleInput(ContactId, &InputMsgSize), CFE_SUCCESS);

    /* Verify that the function ran as expected */
    UtAssert_STUB_COUNT(BPLib_CLA_Ingress, 1);
}

void Test_BPNode_ClaIn_ProcessBundleInput_LtpNom(void)
{
    uint8 ContactId;
    size_t BundleSize;

    /* LTP case */
    ContactId = 0;
    BPNode_AppData.ClaInData[ContactId].ClaType = BPLib_LTP_CLA;

    UtAssert_UINT32_EQ(BPNode_ClaIn_ProcessBundleInput(ContactId, &BundleSize), BPLIB_TIMEOUT);
    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 0);
}

void Test_BPNode_ClaIn_ProcessBundleInput_EppNom(void)
{
    uint8 ContactId;
    size_t BundleSize;

    /* EPP case */
    ContactId = 0;
    BPNode_AppData.ClaInData[ContactId].ClaType = BPLib_EPP_CLA;

    UtAssert_UINT32_EQ(BPNode_ClaIn_ProcessBundleInput(ContactId, &BundleSize), BPLIB_TIMEOUT);
    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 0);
}

void Test_BPNode_ClaIn_ProcessBundleInput_TcpNom(void)
{
    uint8 ContactId;
    size_t BundleSize;

    /* TCP case */
    ContactId = 0;
    BPNode_AppData.ClaInData[ContactId].ClaType = BPLib_TCP_CLA;

    UtAssert_UINT32_EQ(BPNode_ClaIn_ProcessBundleInput(ContactId, &BundleSize), BPLIB_TIMEOUT);
    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 0);
}

void Test_BPNode_ClaIn_ProcessBundleInput_Default(void)
{
    uint8 ContactId;
    size_t BundleSize;

    /* TCP case */
    ContactId = 0;
    BPNode_AppData.ClaInData[ContactId].ClaType = 0xff;

    UtAssert_UINT32_EQ(BPNode_ClaIn_ProcessBundleInput(ContactId, &BundleSize), BPLIB_TIMEOUT);
    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 0);
}

void Test_BPNode_ClaIn_ProcessBundleInput_ReceiveBufferErr(void)
{
    uint8 ContactId;
    size_t MsgSize;

    MsgSize   = 42;
    ContactId = 0;
    BPNode_AppData.ClaInData[ContactId].ClaType = BPLib_SB_CLA;

    UT_SetDefaultReturnValue(UT_KEY(CFE_SB_ReceiveBuffer), CFE_SB_BAD_ARGUMENT);
    UT_SetDataBuffer(UT_KEY(CFE_MSG_GetSize), &MsgSize, sizeof(size_t), false);

    UtAssert_EQ(CFE_Status_t, BPNode_ClaIn_ProcessBundleInput(ContactId, &MsgSize), BPLIB_TIMEOUT);

    UtAssert_STUB_COUNT(BPLib_CLA_Ingress, 0);
    BPNode_Test_Verify_Event(0, BPNODE_CLA_IN_RECV_BUFF_ERR_EID,
                                "[CLA In #%d]: Failed to receive from the SB buffer. Error = %d");
}

void Test_BPNode_ClaIn_ProcessBundleInput_ReceiveBufferTimeout(void)
{
    uint8 ContactId;
    size_t MsgSize;

    ContactId = 0;
    MsgSize   = 42;
    BPNode_AppData.ClaInData[ContactId].ClaType = BPLib_SB_CLA;

    UT_SetDataBuffer(UT_KEY(CFE_MSG_GetSize), &MsgSize, sizeof(size_t), false);
    UT_SetDefaultReturnValue(UT_KEY(CFE_SB_ReceiveBuffer), CFE_SB_TIME_OUT);

    UtAssert_EQ(CFE_Status_t, BPNode_ClaIn_ProcessBundleInput(ContactId, &MsgSize), BPLIB_TIMEOUT);

    UtAssert_STUB_COUNT(BPLib_CLA_Ingress, 0);
}

void Test_BPNode_ClaIn_ProcessBundleInput_FailedIODCommand(void)
{
    uint8 ContactId = 0;
    size_t BundleSize;

    UT_SetDeferredRetcode(UT_KEY(CFE_PSP_IODriver_Command), 1, CFE_PSP_ERROR);
    UtAssert_INT32_EQ(BPNode_ClaIn_ProcessBundleInput(ContactId, &BundleSize), BPLIB_TIMEOUT);

    BPNode_Test_Verify_Event(0, BPNODE_CLA_IN_IO_READ_ERR_EID,
                            "[CLA In #%d]: Failed to read packet from UDP socket, RC = %d");
}

void Test_BPNode_ClaIn_ProcessBundleInput_SB_MsgSizeZero(void)
{
    uint8 ContactId;
    size_t MsgSize;
    CFE_SB_Buffer_t  Buf;
    CFE_SB_Buffer_t* BufPtr;

    BufPtr    = &Buf;
    ContactId = 0;
    MsgSize   = 0;
    BPNode_AppData.ClaInData[ContactId].ClaType = BPLib_SB_CLA;

    UT_SetDataBuffer(UT_KEY(CFE_MSG_GetSize), &MsgSize, sizeof(size_t), false);
    UT_SetDataBuffer(UT_KEY(CFE_SB_ReceiveBuffer), &BufPtr, sizeof(BufPtr), false);

    UtAssert_EQ(CFE_Status_t, BPNode_ClaIn_ProcessBundleInput(ContactId, &MsgSize), BPLIB_TIMEOUT);
    UtAssert_STUB_COUNT(BPLib_CLA_Ingress, 0);
}

void Test_BPNode_ClaIn_ProcessBundleInput_FailedBPLibIngress(void)
{
    uint8 ContactId;
    size_t MsgSize;
    CFE_SB_Buffer_t  Buf;
    CFE_SB_Buffer_t* BufPtr;

    BufPtr    = &Buf;
    ContactId = 0;
    MsgSize   = 42;

    UT_SetDataBuffer(UT_KEY(CFE_MSG_GetSize), &MsgSize, sizeof(size_t), false);
    UT_SetDataBuffer(UT_KEY(CFE_SB_ReceiveBuffer), &BufPtr, sizeof(BufPtr), false);
    UT_SetDeferredRetcode(UT_KEY(BPLib_CLA_Ingress), 1, BPLIB_ERROR);

    UtAssert_UINT32_EQ(BPNode_ClaIn_ProcessBundleInput(ContactId, &MsgSize), BPLIB_ERROR);
}

void Test_BPNode_ClaIn_ProcessBundleInput_CLA_IngressTimeout(void)
{
    uint8  ContactId;
    size_t MsgSize;
    CFE_SB_Buffer_t  Buf;
    CFE_SB_Buffer_t* BufPtr;

    BufPtr    = &Buf;
    ContactId = 0;
    MsgSize   = 42;

    UT_SetDeferredRetcode(UT_KEY(BPLib_CLA_Ingress), 1, BPLIB_CLA_TIMEOUT);
    UT_SetDataBuffer(UT_KEY(CFE_MSG_GetSize), &MsgSize, sizeof(size_t), false);
    UT_SetDataBuffer(UT_KEY(CFE_SB_ReceiveBuffer), &BufPtr, sizeof(BufPtr), false);

    UtAssert_INT32_EQ(BPNode_ClaIn_ProcessBundleInput(ContactId, &MsgSize), BPLIB_CLA_TIMEOUT);

    UtAssert_STUB_COUNT(BPLib_CLA_Ingress, 1);
}

void Test_BPNode_ClaIn_Start_UdpNom(void)
{
    BPLib_Status_t Status;
    uint32 ContactId = 0;

    BPNode_AppData.ClaInData[ContactId].ClaType = BPLib_UDP_CLA;

    Status = BPNode_ClaIn_Start(ContactId);

    UtAssert_INT32_EQ(Status, BPLIB_SUCCESS);
    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 0);
}

void Test_BPNode_ClaIn_Start_PspErr(void)
{
    uint32 ContId = 0;

    BPNode_AppData.ConfigPtrs.ContactsConfigPtr->ContactSet[ContId].CLAType = BPLib_UDP_CLA;

    UT_SetDeferredRetcode(UT_KEY(CFE_PSP_IODriver_Command), 1, CFE_PSP_ERROR);

    UtAssert_INT32_EQ(BPNode_ClaIn_Start(ContId), BPLIB_CLA_IO_ERROR);

    UtAssert_STUB_COUNT(CFE_PSP_IODriver_Command, 1);
    BPNode_Test_Verify_Event(0, BPNODE_CLA_IN_CFG_SET_RUN_ERR_EID,
                            "Couldn't set I/O state for CLA In #%d to running. Error = %d");
}

void Test_BPNode_ClaIn_Start_SbNom(void)
{
    uint32 ContactId = 0;

    BPNode_AppData.ClaInData[ContactId].ClaType = BPLib_SB_CLA;

    UtAssert_EQ(BPLib_Status_t, BPNode_ClaIn_Start(ContactId), BPLIB_SUCCESS);
    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 0);
}

void Test_BPNode_ClaIn_Start_SbErr(void)
{
    uint32 ContactId = 0;

    UT_SetDefaultReturnValue(UT_KEY(CFE_SB_SubscribeEx), CFE_SB_MAX_MSGS_MET);

    BPNode_AppData.ClaInData[ContactId].ClaType = BPLib_SB_CLA;
    UtAssert_EQ(BPLib_Status_t, BPNode_ClaIn_Start(ContactId), BPLIB_CLA_IO_ERROR);

    BPNode_Test_Verify_Event(0, BPNODE_CLA_IN_SUB_ERR_EID,
                                "Error subscribing to CLA In %d task messages, RC = 0x%08lX");
}

void Test_BPNode_ClaIn_Start_LtpNom(void)
{
    uint32 ContactId = 0;

    BPNode_AppData.ClaInData[ContactId].ClaType = BPLib_LTP_CLA;

    UtAssert_EQ(BPLib_Status_t, BPNode_ClaIn_Start(ContactId), BPLIB_SUCCESS);
    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 0);
}

void Test_BPNode_ClaIn_Start_EppNom(void)
{
    uint32 ContactId = 0;

    BPNode_AppData.ClaInData[ContactId].ClaType = BPLib_EPP_CLA;

    UtAssert_EQ(BPLib_Status_t, BPNode_ClaIn_Start(ContactId), BPLIB_SUCCESS);
    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 0);
}

void Test_BPNode_ClaIn_Start_TcpNom(void)
{
    uint32 ContactId = 0;

    BPNode_AppData.ClaInData[ContactId].ClaType = BPLib_TCP_CLA;

    UtAssert_EQ(BPLib_Status_t, BPNode_ClaIn_Start(ContactId), BPLIB_SUCCESS);
    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 0);
}


void Test_BPNode_ClaIn_Start_Default(void)
{
    uint32 ContactId = 0;

    BPNode_AppData.ClaInData[ContactId].ClaType = 0xff;

    UtAssert_EQ(BPLib_Status_t, BPNode_ClaIn_Start(ContactId), BPLIB_SUCCESS);
    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 0);
}

void Test_BPNode_ClaIn_Stop_UdpNom(void)
{
    BPLib_Status_t Status;
    uint32 ContactId = 0;

    BPNode_AppData.ClaInData[ContactId].ClaType = BPLib_UDP_CLA;

    Status = BPNode_ClaIn_Stop(ContactId);

    UtAssert_INT32_EQ(Status, BPLIB_SUCCESS);
    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 0);
}

void Test_BPNode_ClaIn_Stop_PspErr(void)
{
    uint32 ContId = 0;

    BPNode_AppData.ConfigPtrs.ContactsConfigPtr->ContactSet[ContId].CLAType = BPLib_UDP_CLA;

    UT_SetDeferredRetcode(UT_KEY(CFE_PSP_IODriver_Command), 1, CFE_PSP_ERROR);

    UtAssert_INT32_EQ(BPNode_ClaIn_Stop(ContId), BPLIB_CLA_IO_ERROR);

    UtAssert_STUB_COUNT(CFE_PSP_IODriver_Command, 1);
    BPNode_Test_Verify_Event(0, BPNODE_CLA_IN_CFG_STOP_ERR_EID,
                            "Couldn't set I/O state to stop for CLA In #%d. Error = %d");
}

void Test_BPNode_ClaIn_Stop_SbNom(void)
{
    uint32 ContactId = 0;

    BPNode_AppData.ClaInData[ContactId].ClaType = BPLib_SB_CLA;

    UtAssert_EQ(BPLib_Status_t, BPNode_ClaIn_Stop(ContactId), BPLIB_SUCCESS);
    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 0);
}

void Test_BPNode_ClaIn_Stop_SbErr(void)
{
    uint32 ContactId = 0;

    UT_SetDefaultReturnValue(UT_KEY(CFE_SB_Unsubscribe), CFE_SB_BAD_ARGUMENT);

    BPNode_AppData.ClaInData[ContactId].ClaType = BPLib_SB_CLA;
    UtAssert_EQ(BPLib_Status_t, BPNode_ClaIn_Stop(ContactId), BPLIB_CLA_IO_ERROR);

    BPNode_Test_Verify_Event(0, BPNODE_CLA_IN_UNSUB_ERR_EID,
                                "Error unsubscribing from CLA In %d task messages, RC = 0x%08lX");
}

void Test_BPNode_ClaIn_Stop_LtpNom(void)
{
    uint32 ContactId = 0;

    BPNode_AppData.ClaInData[ContactId].ClaType = BPLib_LTP_CLA;

    UtAssert_EQ(BPLib_Status_t, BPNode_ClaIn_Stop(ContactId), BPLIB_SUCCESS);
    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 0);
}

void Test_BPNode_ClaIn_Stop_EppNom(void)
{
    uint32 ContactId = 0;

    BPNode_AppData.ClaInData[ContactId].ClaType = BPLib_EPP_CLA;

    UtAssert_EQ(BPLib_Status_t, BPNode_ClaIn_Stop(ContactId), BPLIB_SUCCESS);
    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 0);
}

void Test_BPNode_ClaIn_Stop_TcpNom(void)
{
    uint32 ContactId = 0;

    BPNode_AppData.ClaInData[ContactId].ClaType = BPLib_TCP_CLA;

    UtAssert_EQ(BPLib_Status_t, BPNode_ClaIn_Stop(ContactId), BPLIB_SUCCESS);
    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 0);
}

void Test_BPNode_ClaIn_Stop_Default(void)
{
    uint32 ContactId = 0;

    BPNode_AppData.ClaInData[ContactId].ClaType = 0xff;

    UtAssert_EQ(BPLib_Status_t, BPNode_ClaIn_Stop(ContactId), BPLIB_SUCCESS);
    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 0);
}

void Test_BPNode_ClaIn_Teardown_UdpNom(void)
{
    uint32 ContactId = 0;

    BPNode_AppData.ClaInData[ContactId].ClaType = BPLib_UDP_CLA;

    UtAssert_VOIDCALL(BPNode_ClaIn_Teardown(ContactId));
}

/* Register the test cases to execute with the unit test tool */
void UtTest_Setup(void)
{
    ADD_TEST(Test_BPNode_ClaInCreateTasks_Nominal);
    ADD_TEST(Test_BPNode_ClaInCreateTasks_TaskCrErr);

    ADD_TEST(Test_BPNode_ClaIn_TaskInit_FindByNameErr);
    ADD_TEST(Test_BPNode_ClaIn_TaskInit_DirErr);
    ADD_TEST(Test_BPNode_ClaIn_TaskInit_CreatePipeErr);
    ADD_TEST(Test_BPNode_ClaIn_TaskInit_IdErr);
    ADD_TEST(Test_BPNode_ClaIn_TaskInit_UdpNom);
    ADD_TEST(Test_BPNode_ClaIn_TaskInit_SbNom);
    ADD_TEST(Test_BPNode_ClaIn_TaskInit_LtpNom);
    ADD_TEST(Test_BPNode_ClaIn_TaskInit_EppNom);
    ADD_TEST(Test_BPNode_ClaIn_TaskInit_TcpNom);
    ADD_TEST(Test_BPNode_ClaIn_TaskInit_Default);

    ADD_TEST(Test_BPNode_ClaIn_Setup_UdpNom);
    ADD_TEST(Test_BPNode_ClaIn_Setup_SbNom);
    ADD_TEST(Test_BPNode_ClaIn_Setup_LtpNom);
    ADD_TEST(Test_BPNode_ClaIn_Setup_EppNom);
    ADD_TEST(Test_BPNode_ClaIn_Setup_TcpNom);
    ADD_TEST(Test_BPNode_ClaIn_Setup_Default);
    ADD_TEST(Test_BPNode_ClaIn_Setup_PortErr);
    ADD_TEST(Test_BPNode_ClaIn_Setup_IpErr);

    ADD_TEST(Test_BPNode_ClaIn_TaskMain_Nominal);
    ADD_TEST(Test_BPNode_ClaIn_TaskMain_ClearPipe);
    ADD_TEST(Test_BPNode_ClaIn_TaskMain_NoClearPipe);
    ADD_TEST(Test_BPNode_ClaIn_TaskMain_IdErr);
    ADD_TEST(Test_BPNode_ClaIn_TaskMain_NoIngress);
    ADD_TEST(Test_BPNode_ClaIn_TaskMain_StateErr);
    ADD_TEST(Test_BPNode_ClaIn_TaskMain_FailedProcBundle);
    ADD_TEST(Test_BPNode_ClaIn_TaskMain_OneBundle);
    ADD_TEST(Test_BPNode_ClaIn_TaskMain_MaxLimit);
    ADD_TEST(Test_BPNode_ClaIn_TaskMain_RateLimitedOver);
    ADD_TEST(Test_BPNode_ClaIn_TaskMain_RateLimitedUnder);

    ADD_TEST(Test_BPNode_ClaIn_ProcessBundleInput_UdpNom);
    ADD_TEST(Test_BPNode_ClaIn_ProcessBundleInput_SbNom);
    ADD_TEST(Test_BPNode_ClaIn_ProcessBundleInput_LtpNom);
    ADD_TEST(Test_BPNode_ClaIn_ProcessBundleInput_EppNom);
    ADD_TEST(Test_BPNode_ClaIn_ProcessBundleInput_TcpNom);
    ADD_TEST(Test_BPNode_ClaIn_ProcessBundleInput_Default);
    ADD_TEST(Test_BPNode_ClaIn_ProcessBundleInput_ReceiveBufferErr);
    ADD_TEST(Test_BPNode_ClaIn_ProcessBundleInput_ReceiveBufferTimeout);
    ADD_TEST(Test_BPNode_ClaIn_ProcessBundleInput_FailedIODCommand);
    ADD_TEST(Test_BPNode_ClaIn_ProcessBundleInput_SB_MsgSizeZero);
    ADD_TEST(Test_BPNode_ClaIn_ProcessBundleInput_FailedBPLibIngress);
    ADD_TEST(Test_BPNode_ClaIn_ProcessBundleInput_CLA_IngressTimeout);

    ADD_TEST(Test_BPNode_ClaIn_Start_UdpNom);
    ADD_TEST(Test_BPNode_ClaIn_Start_PspErr);
    ADD_TEST(Test_BPNode_ClaIn_Start_SbNom);
    ADD_TEST(Test_BPNode_ClaIn_Start_SbErr);
    ADD_TEST(Test_BPNode_ClaIn_Start_LtpNom);
    ADD_TEST(Test_BPNode_ClaIn_Start_EppNom);
    ADD_TEST(Test_BPNode_ClaIn_Start_TcpNom);
    ADD_TEST(Test_BPNode_ClaIn_Start_Default);

    ADD_TEST(Test_BPNode_ClaIn_Stop_UdpNom);
    ADD_TEST(Test_BPNode_ClaIn_Stop_PspErr);
    ADD_TEST(Test_BPNode_ClaIn_Stop_SbNom);
    ADD_TEST(Test_BPNode_ClaIn_Stop_SbErr);
    ADD_TEST(Test_BPNode_ClaIn_Stop_LtpNom);
    ADD_TEST(Test_BPNode_ClaIn_Stop_EppNom);
    ADD_TEST(Test_BPNode_ClaIn_Stop_TcpNom);
    ADD_TEST(Test_BPNode_ClaIn_Stop_Default);

    ADD_TEST(Test_BPNode_ClaIn_Teardown_UdpNom);
}