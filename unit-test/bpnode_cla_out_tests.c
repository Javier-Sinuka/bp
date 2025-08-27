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
 *  Unit tests for bpnode_cla_out.c
 */

/*
** Include Files
*/

#include "bpnode_cla_out.h"
#include "bpnode_test_utils.h"

/*
** Function Definitions
*/

/* Test BPNode_ClaOutCreateTasks when everything succeeds */
void Test_BPNode_ClaOutCreateTasks_Nominal(void)
{
    UtAssert_INT32_EQ(BPNode_ClaOutCreateTasks(), CFE_SUCCESS);

    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 0);
    UtAssert_STUB_COUNT(CFE_ES_CreateChildTask, BPLIB_MAX_NUM_CONTACTS);
}

/* Test BPNode_ClaOutCreateTasks when the child task creation fails */
void Test_BPNode_ClaOutCreateTasks_TaskCrErr(void)
{
    UT_SetDeferredRetcode(UT_KEY(CFE_ES_CreateChildTask), 1, CFE_ES_ERR_CHILD_TASK_CREATE);

    UtAssert_INT32_EQ(BPNode_ClaOutCreateTasks(), CFE_ES_ERR_CHILD_TASK_CREATE);

    UtAssert_INT32_EQ(context_BPLib_EM_SendEvent[0].EventID, BPNODE_CLA_OUT_CREATE_ERR_EID);
    UtAssert_STRINGBUF_EQ("Failed to create child task for CLA Out #%d. Error = %d", BPLIB_EM_EXPANDED_EVENT_SIZE,
                            context_BPLib_EM_SendEvent[0].Spec, BPLIB_EM_EXPANDED_EVENT_SIZE);
    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 1);
    UtAssert_STUB_COUNT(CFE_ES_CreateChildTask, 1);
}

/* Test BPNode_ClaOut_TaskInit when everything succeeds */
void Test_BPNode_ClaOut_TaskInit_Nominal(void)
{
    uint32 ContactId = 0;

    /* Test setup */
    UT_SetDefaultReturnValue(UT_KEY(CFE_PSP_IODriver_FindByName), CFE_PSP_SUCCESS);
    UT_SetDefaultReturnValue(UT_KEY(CFE_PSP_IODriver_Command), CFE_PSP_SUCCESS);

    UtAssert_INT32_EQ(BPNode_ClaOut_TaskInit(ContactId), CFE_PSP_SUCCESS);

    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 0);
    UtAssert_STUB_COUNT(CFE_PSP_IODriver_FindByName, 1);
    UtAssert_STUB_COUNT(CFE_PSP_IODriver_Command, 1);
}

/* Test BPNode_ClaOut_TaskInit when the channel ID is invalid */
void Test_BPNode_ClaOut_TaskInit_IdErr(void)
{
    uint32 ContactId = BPLIB_MAX_NUM_CONTACTS;

    UtAssert_INT32_EQ(BPNode_ClaOut_TaskInit(ContactId), CFE_STATUS_RANGE_ERROR);

    BPNode_Test_Verify_Event(0, BPNODE_CLA_OUT_INIT_PTR_CRT_EID, 
                                "Invalid contact ID %d passed into BPNode_ClaOut_TaskInit function pointer.");
    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 1);
    UtAssert_STUB_COUNT(CFE_PSP_IODriver_FindByName, 0);
}

/* Test BPNode_ClaOut_TaskInit when the PSP module can't be found */
void Test_BPNode_ClaOut_TaskInit_FindByNameErr(void)
{
    uint32 ContactId       = BPLIB_MAX_NUM_CONTACTS - 1;

    UT_SetDeferredRetcode(UT_KEY(CFE_PSP_IODriver_FindByName), 1, CFE_PSP_ERROR);

    UtAssert_INT32_EQ(BPNode_ClaOut_TaskInit(ContactId), CFE_PSP_ERROR);

    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 1);
    UtAssert_INT32_EQ(context_BPLib_EM_SendEvent[0].EventID, BPNODE_CLA_OUT_FIND_NAME_ERR_EID);
    UtAssert_STRINGBUF_EQ("[CLA Out #%d]: Couldn't find I/O driver. Error = %d", BPLIB_EM_EXPANDED_EVENT_SIZE,
                            context_BPLib_EM_SendEvent[0].Spec, BPLIB_EM_EXPANDED_EVENT_SIZE);
    UtAssert_STUB_COUNT(CFE_PSP_IODriver_FindByName, 1);
    UtAssert_STUB_COUNT(CFE_PSP_IODriver_Command, 0);
}

/* Test BPNode_ClaOut_TaskInit when the direction can't be set */
void Test_BPNode_ClaOut_TaskInit_DirErr(void)
{
    uint32 ContactId       = BPLIB_MAX_NUM_CONTACTS - 1;

    UT_SetDefaultReturnValue(UT_KEY(CFE_PSP_IODriver_FindByName), CFE_PSP_SUCCESS);
    UT_SetDefaultReturnValue(UT_KEY(CFE_PSP_IODriver_Command), CFE_PSP_ERROR);

    UtAssert_INT32_EQ(BPNode_ClaOut_TaskInit(ContactId), CFE_PSP_ERROR);

    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 1);
    UtAssert_INT32_EQ(context_BPLib_EM_SendEvent[0].EventID, BPNODE_CLA_OUT_CFG_DIR_ERR_EID);
    UtAssert_STRINGBUF_EQ("[CLA Out #%d]: Couldn't set I/O direction to output. Error = %d", BPLIB_EM_EXPANDED_EVENT_SIZE,
                            context_BPLib_EM_SendEvent[0].Spec, BPLIB_EM_EXPANDED_EVENT_SIZE);
}

/* Test BPNode_ClaOut_TaskMain when the contact ID is invalid */
void Test_BPNode_ClaOut_TaskMain_IdErr(void)
{
    uint32 ContactId = BPLIB_MAX_NUM_CONTACTS;

    UtAssert_VOIDCALL(BPNode_ClaOut_TaskMain(ContactId));

    BPNode_Test_Verify_Event(0, BPNODE_CLA_OUT_MAIN_PTR_CRT_EID, 
                                "Invalid contact ID %d passed into BPNode_ClaOut_TaskMain function pointer.");
    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 1);
    UtAssert_STUB_COUNT(BPLib_CLA_GetContactRunState, 0);
}

/* Test BPNode_ClaOut_TaskMain when app state is started */
void Test_BPNode_ClaOut_TaskMain_NoBundleAvailable(void)
{
    uint32                      ContactId;
    BPLib_CLA_ContactRunState_t RunState;

    ContactId = BPLIB_MAX_NUM_CONTACTS - 1;
    RunState = BPLIB_CLA_STARTED;

    BPNode_AppData.ClaOutData[ContactId].RateLimit = 100000;

    /* Test setup */
    UT_SetDataBuffer(UT_KEY(BPLib_CLA_GetContactRunState), &RunState, sizeof(BPLib_CLA_ContactRunState_t), false);
    UT_SetDeferredRetcode(UT_KEY(BPLib_CLA_Egress), 1, BPLIB_CLA_TIMEOUT);

    UtAssert_VOIDCALL(BPNode_ClaOut_TaskMain(ContactId));

    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 0);
    UtAssert_STUB_COUNT(BPLib_AS_Increment, 0);
}

/* Test BPNode_ClaOut_TaskMain when max number of bundles are egressed */
void Test_BPNode_ClaOut_TaskMain_MaxBundles(void)
{
    uint32                      ContactId = BPLIB_MAX_NUM_CONTACTS - 1;
    BPLib_CLA_ContactRunState_t RunState = BPLIB_CLA_STARTED;
    size_t BundleSize = 10;
    size_t RateLimit = 100;
    size_t NumProcessedBundles = RateLimit / BundleSize;
    size_t NumSentBundles = NumProcessedBundles + 1;
    uint32 i;

    /* Test setup */
    UT_SetDataBuffer(UT_KEY(BPLib_CLA_GetContactRunState), &RunState, sizeof(BPLib_CLA_ContactRunState_t), false);
    UT_SetDefaultReturnValue(UT_KEY(BPLib_CLA_Egress), BPLIB_SUCCESS);

    BPNode_AppData.ClaOutData[ContactId].RateLimit = RateLimit * 8;

    for (i = 0; i < NumSentBundles; i++)
    {
        UT_SetDataBuffer(UT_KEY(BPLib_CLA_Egress), &BundleSize, sizeof(BundleSize), false);
    }

    UtAssert_VOIDCALL(BPNode_ClaOut_TaskMain(ContactId));

    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 0);
    UtAssert_STUB_COUNT(BPLib_CLA_Egress, NumProcessedBundles);
}

/* Test BPNode_ClaOut_TaskMain when bundle egress is disabled */
void Test_BPNode_ClaOut_TaskMain_NoEgress(void)
{
    uint32                      ContactId;
    BPLib_CLA_ContactRunState_t RunState;

    ContactId = 0;
    RunState = BPLIB_CLA_STOPPED;

    /* Test setup */
    UT_SetDataBuffer(UT_KEY(BPLib_CLA_GetContactRunState), &RunState, sizeof(BPLib_CLA_ContactRunState_t), false);

    UtAssert_VOIDCALL(BPNode_ClaOut_TaskMain(ContactId));

    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 0);
}

/* Test BPNode_ClaOut_TaskMain when getting the contact state fails */
void Test_BPNode_ClaOut_TaskMain_StateErr(void)
{
    uint32                      ContactId;
    BPLib_CLA_ContactRunState_t RunState;

    ContactId = 0;
    RunState = BPLIB_CLA_STARTED;

    /* Test setup */
    UT_SetDataBuffer(UT_KEY(BPLib_CLA_GetContactRunState), &RunState, sizeof(BPLib_CLA_ContactRunState_t), false);
    UT_SetDefaultReturnValue(UT_KEY(BPLib_CLA_GetContactRunState), BPLIB_ERROR);

    UtAssert_VOIDCALL(BPNode_ClaOut_TaskMain(ContactId));

    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 0);
    UtAssert_STUB_COUNT(BPLib_CLA_Egress, 0);    
}

void Test_BPNode_ClaOut_TaskMain_FailedProcBundle(void)
{
    uint32                      ContactId;
    BPLib_CLA_ContactRunState_t RunState1;
    BPLib_CLA_ContactRunState_t RunState2;

    ContactId = 0;
    RunState1 = BPLIB_CLA_STARTED;
    RunState2 = BPLIB_CLA_EXITED;

    /* Test setup */
    UT_SetDataBuffer(UT_KEY(BPLib_CLA_GetContactRunState), &RunState1, sizeof(BPLib_CLA_ContactRunState_t), false);
    UT_SetDataBuffer(UT_KEY(BPLib_CLA_GetContactRunState), &RunState2, sizeof(BPLib_CLA_ContactRunState_t), false);
    UT_SetDeferredRetcode(UT_KEY(BPNode_ClaOut_ProcessBundleOutput), 1, CFE_STATUS_EXTERNAL_RESOURCE_FAIL);

    UT_SetDeferredRetcode(UT_KEY(BPLib_CLA_Egress), 1, BPLIB_ERROR);
    UtAssert_VOIDCALL(BPNode_ClaOut_TaskMain(ContactId));

    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 1);
}

void Test_BPNode_ClaOut_ProcessBundleOutput_SbNom(void)
{
    uint32 ContactId;
    size_t BundleSize;

    ContactId = 0;
    BPNode_AppData.ConfigPtrs.ContactsConfigPtr->ContactSet[ContactId].CLAType = BPLib_SB_CLA;

    UtAssert_UINT32_EQ(BPNode_ClaOut_ProcessBundleOutput(ContactId, &BundleSize), BPLIB_SUCCESS);

    UtAssert_STUB_COUNT(CFE_SB_TransmitMsg, 1);
    UtAssert_STUB_COUNT(CFE_PSP_IODriver_Command, 0);
}

void Test_BPNode_ClaOut_ProcessBundleOutput_UdpNom(void)
{
    uint32 ContactId;
    size_t BundleSize;

    ContactId = 0;
    BPNode_AppData.ConfigPtrs.ContactsConfigPtr->ContactSet[ContactId].CLAType = BPLib_UDP_CLA;

    UtAssert_UINT32_EQ(BPNode_ClaOut_ProcessBundleOutput(ContactId, &BundleSize), BPLIB_SUCCESS);

    UtAssert_STUB_COUNT(CFE_SB_TransmitMsg, 0);
    UtAssert_STUB_COUNT(CFE_PSP_IODriver_Command, 1);
}

void Test_BPNode_ClaOut_ProcessBundleOutput_LtpNom(void)
{
    size_t BundleSize;
    uint32 ContactId = 0;

    BPNode_AppData.ConfigPtrs.ContactsConfigPtr->ContactSet[ContactId].CLAType = BPLib_LTP_CLA;

    UtAssert_UINT32_EQ(BPNode_ClaOut_ProcessBundleOutput(ContactId, &BundleSize), BPLIB_SUCCESS);

    UtAssert_STUB_COUNT(CFE_SB_TransmitMsg, 0);
    UtAssert_STUB_COUNT(CFE_PSP_IODriver_Command, 0);
}

void Test_BPNode_ClaOut_ProcessBundleOutput_EppNom(void)
{
    size_t BundleSize;
    uint32 ContactId = 0;

    BPNode_AppData.ConfigPtrs.ContactsConfigPtr->ContactSet[ContactId].CLAType = BPLib_EPP_CLA;

    UtAssert_UINT32_EQ(BPNode_ClaOut_ProcessBundleOutput(ContactId, &BundleSize), BPLIB_SUCCESS);

    UtAssert_STUB_COUNT(CFE_SB_TransmitMsg, 0);
    UtAssert_STUB_COUNT(CFE_PSP_IODriver_Command, 0);
}

void Test_BPNode_ClaOut_ProcessBundleOutput_TcpNom(void)
{
    size_t BundleSize;
    uint32 ContactId = 0;

    BPNode_AppData.ConfigPtrs.ContactsConfigPtr->ContactSet[ContactId].CLAType = BPLib_TCP_CLA;

    UtAssert_UINT32_EQ(BPNode_ClaOut_ProcessBundleOutput(ContactId, &BundleSize), BPLIB_SUCCESS);

    UtAssert_STUB_COUNT(CFE_SB_TransmitMsg, 0);
    UtAssert_STUB_COUNT(CFE_PSP_IODriver_Command, 0);
}

void Test_BPNode_ClaOut_ProcessBundleOutput_Default(void)
{
    size_t BundleSize;
    uint32 ContactId = 0;

    BPNode_AppData.ConfigPtrs.ContactsConfigPtr->ContactSet[ContactId].CLAType = 0xff;

    UtAssert_UINT32_EQ(BPNode_ClaOut_ProcessBundleOutput(ContactId, &BundleSize), BPLIB_SUCCESS);

    UtAssert_STUB_COUNT(CFE_SB_TransmitMsg, 0);
    UtAssert_STUB_COUNT(CFE_PSP_IODriver_Command, 0);
}

void Test_BPNode_ClaOut_ProcessBundleOutput_FailedBPLibEgress(void)
{
    uint32 ContactId = 0;
    size_t BundleSize;

    UT_SetDeferredRetcode(UT_KEY(BPLib_CLA_Egress), 1, BPLIB_ERROR);
    UtAssert_INT32_EQ(BPNode_ClaOut_ProcessBundleOutput(ContactId, &BundleSize), BPLIB_ERROR);

    UtAssert_INT32_EQ(context_BPLib_EM_SendEvent[0].EventID, BPNODE_CLA_OUT_LIB_LOAD_ERR_EID);
    UtAssert_STRINGBUF_EQ("[CLA Out #%d]: Failed to get bundle for egress. Error = %d", BPLIB_EM_EXPANDED_EVENT_SIZE,
                            context_BPLib_EM_SendEvent[0].Spec, BPLIB_EM_EXPANDED_EVENT_SIZE);
}

void Test_BPNode_ClaOut_ProcessBundleOutput_CLATimeout(void)
{
    uint32 ContactId = 0;
    size_t BundleSize;

    UT_SetDeferredRetcode(UT_KEY(BPLib_CLA_Egress), 1, BPLIB_CLA_TIMEOUT);
    UtAssert_INT32_EQ(BPNode_ClaOut_ProcessBundleOutput(ContactId, &BundleSize), BPLIB_CLA_TIMEOUT);
}

void Test_BPNode_ClaOut_Setup_UdpNom(void)
{
    BPLib_Status_t Status;
    uint32 ContId = 0;

    strcpy(BPNode_AppData.ConfigPtrs.ContactsConfigPtr->ContactSet[ContId].ClaOutAddr, "127.0.0.1");
    BPNode_AppData.ConfigPtrs.ContactsConfigPtr->ContactSet[ContId].ClaOutPort = 100;
    BPNode_AppData.ConfigPtrs.ContactsConfigPtr->ContactSet[ContId].CLAType = BPLib_UDP_CLA;

    Status = BPNode_ClaOut_Setup(ContId);

    UtAssert_INT32_EQ(Status, BPLIB_SUCCESS);
    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 0);
}

void Test_BPNode_ClaOut_Setup_PortErr(void)
{
    uint32 ContId = 0;

    strcpy(BPNode_AppData.ConfigPtrs.ContactsConfigPtr->ContactSet[ContId].ClaOutAddr, "127.0.0.1");
    BPNode_AppData.ConfigPtrs.ContactsConfigPtr->ContactSet[ContId].ClaOutPort = 100;
    BPNode_AppData.ConfigPtrs.ContactsConfigPtr->ContactSet[ContId].CLAType = BPLib_UDP_CLA;

    UT_SetDeferredRetcode(UT_KEY(CFE_PSP_IODriver_Command), 1, CFE_PSP_ERROR);

    UtAssert_INT32_EQ(BPNode_ClaOut_Setup(ContId), BPLIB_CLA_IO_ERROR);

    UtAssert_STUB_COUNT(CFE_PSP_IODriver_Command, 1);
    BPNode_Test_Verify_Event(0, BPNODE_CLA_OUT_CFG_PORT_ERR_EID, 
                            "Couldn't configure port number for CLA Out #%d. Error = %d");
}

void Test_BPNode_ClaOut_Setup_IpErr(void)
{
    uint32 ContId = 0;

    strcpy(BPNode_AppData.ConfigPtrs.ContactsConfigPtr->ContactSet[ContId].ClaOutAddr, "127.0.0.1");
    BPNode_AppData.ConfigPtrs.ContactsConfigPtr->ContactSet[ContId].ClaOutPort = 100;
    BPNode_AppData.ConfigPtrs.ContactsConfigPtr->ContactSet[ContId].CLAType = BPLib_UDP_CLA;

    UT_SetDeferredRetcode(UT_KEY(CFE_PSP_IODriver_Command), 1, CFE_PSP_SUCCESS);
    UT_SetDeferredRetcode(UT_KEY(CFE_PSP_IODriver_Command), 1, CFE_PSP_ERROR);

    UtAssert_INT32_EQ(BPNode_ClaOut_Setup(ContId), BPLIB_CLA_IO_ERROR);

    UtAssert_STUB_COUNT(CFE_PSP_IODriver_Command, 2);
    BPNode_Test_Verify_Event(0, BPNODE_CLA_OUT_CFG_IP_ERR_EID, 
                            "Couldn't configure IP address for CLA Out #%d. Error = %d");
}

void Test_BPNode_ClaOut_Setup_SbNom(void)
{
    uint32 ContId = 0;

    BPNode_AppData.ConfigPtrs.ContactsConfigPtr->ContactSet[ContId].CLAType = BPLib_SB_CLA;

    UtAssert_INT32_EQ(BPNode_ClaOut_Setup(ContId), BPLIB_SUCCESS);
    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 0);
}

void Test_BPNode_ClaOut_Setup_LtpNom(void)
{
    uint32 ContId = 0;

    BPNode_AppData.ConfigPtrs.ContactsConfigPtr->ContactSet[ContId].CLAType = BPLib_LTP_CLA;

    UtAssert_INT32_EQ(BPNode_ClaOut_Setup(ContId), BPLIB_SUCCESS);
    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 0);
}

void Test_BPNode_ClaOut_Setup_EppNom(void)
{
    uint32 ContId = 0;

    BPNode_AppData.ConfigPtrs.ContactsConfigPtr->ContactSet[ContId].CLAType = BPLib_EPP_CLA;

    UtAssert_INT32_EQ(BPNode_ClaOut_Setup(ContId), BPLIB_SUCCESS);
    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 0);
}

void Test_BPNode_ClaOut_Setup_TcpNom(void)
{
    uint32 ContId = 0;

    BPNode_AppData.ConfigPtrs.ContactsConfigPtr->ContactSet[ContId].CLAType = BPLib_TCP_CLA;

    UtAssert_INT32_EQ(BPNode_ClaOut_Setup(ContId), BPLIB_SUCCESS);
    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 0);
}

void Test_BPNode_ClaOut_Setup_Default(void)
{
    uint32 ContId = 0;

    BPNode_AppData.ConfigPtrs.ContactsConfigPtr->ContactSet[ContId].CLAType = 0xff;

    UtAssert_INT32_EQ(BPNode_ClaOut_Setup(ContId), BPLIB_SUCCESS);
    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 0);
}

void Test_BPNode_ClaOut_Start_UdpNom(void)
{
    BPLib_Status_t Status;
    uint32 ContId = 0;

    BPNode_AppData.ConfigPtrs.ContactsConfigPtr->ContactSet[ContId].CLAType = BPLib_UDP_CLA;

    Status = BPNode_ClaOut_Start(ContId);

    UtAssert_INT32_EQ(Status, BPLIB_SUCCESS);
    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 0);
}

void Test_BPNode_ClaOut_Start_PspErr(void)
{
    uint32 ContId = 0;

    BPNode_AppData.ConfigPtrs.ContactsConfigPtr->ContactSet[ContId].CLAType = BPLib_UDP_CLA;

    UT_SetDeferredRetcode(UT_KEY(CFE_PSP_IODriver_Command), 1, CFE_PSP_ERROR);

    UtAssert_INT32_EQ(BPNode_ClaOut_Start(ContId), BPLIB_CLA_IO_ERROR);

    UtAssert_STUB_COUNT(CFE_PSP_IODriver_Command, 1);
    BPNode_Test_Verify_Event(0, BPNODE_CLA_OUT_CFG_SET_RUN_ERR_EID, 
                            "Couldn't set I/O state for CLA Out #%d to running. Error = %d");
}

void Test_BPNode_ClaOut_Start_SbNom(void)
{
    uint32 ContId = 0;

    BPNode_AppData.ConfigPtrs.ContactsConfigPtr->ContactSet[ContId].CLAType = BPLib_SB_CLA;

    UtAssert_INT32_EQ(BPNode_ClaOut_Start(ContId), BPLIB_SUCCESS);
    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 0);
}

void Test_BPNode_ClaOut_Start_LtpNom(void)
{
    uint32 ContId = 0;

    BPNode_AppData.ConfigPtrs.ContactsConfigPtr->ContactSet[ContId].CLAType = BPLib_LTP_CLA;

    UtAssert_INT32_EQ(BPNode_ClaOut_Start(ContId), BPLIB_SUCCESS);
    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 0);
}

void Test_BPNode_ClaOut_Start_EppNom(void)
{
    uint32 ContId = 0;

    BPNode_AppData.ConfigPtrs.ContactsConfigPtr->ContactSet[ContId].CLAType = BPLib_EPP_CLA;

    UtAssert_INT32_EQ(BPNode_ClaOut_Start(ContId), BPLIB_SUCCESS);
    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 0);
}

void Test_BPNode_ClaOut_Start_TcpNom(void)
{
    uint32 ContId = 0;

    BPNode_AppData.ConfigPtrs.ContactsConfigPtr->ContactSet[ContId].CLAType = BPLib_TCP_CLA;

    UtAssert_INT32_EQ(BPNode_ClaOut_Start(ContId), BPLIB_SUCCESS);
    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 0);
}

void Test_BPNode_ClaOut_Start_Default(void)
{
    uint32 ContId = 0;

    BPNode_AppData.ConfigPtrs.ContactsConfigPtr->ContactSet[ContId].CLAType = 0xff;

    UtAssert_INT32_EQ(BPNode_ClaOut_Start(ContId), BPLIB_SUCCESS);
    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 0);
}

void Test_BPNode_ClaOut_Stop_UdpNom(void)
{
    BPLib_Status_t Status;
    uint32 ContId = 0;

    BPNode_AppData.ConfigPtrs.ContactsConfigPtr->ContactSet[ContId].CLAType = BPLib_UDP_CLA;

    Status = BPNode_ClaOut_Stop(ContId);

    UtAssert_INT32_EQ(Status, BPLIB_SUCCESS);
    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 0);
}

void Test_BPNode_ClaOut_Stop_PspErr(void)
{
    uint32 ContId = 0;

    BPNode_AppData.ConfigPtrs.ContactsConfigPtr->ContactSet[ContId].CLAType = BPLib_UDP_CLA;

    UT_SetDeferredRetcode(UT_KEY(CFE_PSP_IODriver_Command), 1, CFE_PSP_ERROR);

    UtAssert_INT32_EQ(BPNode_ClaOut_Stop(ContId), BPLIB_CLA_IO_ERROR);

    UtAssert_STUB_COUNT(CFE_PSP_IODriver_Command, 1);
    BPNode_Test_Verify_Event(0, BPNODE_CLA_OUT_CFG_STOP_ERR_EID, 
                            "Couldn't set I/O state to stop for CLA Out #%d. Error = %d");
}

void Test_BPNode_ClaOut_Stop_SbNom(void)
{
    uint32 ContId = 0;

    BPNode_AppData.ConfigPtrs.ContactsConfigPtr->ContactSet[ContId].CLAType = BPLib_SB_CLA;

    UtAssert_INT32_EQ(BPNode_ClaOut_Stop(ContId), BPLIB_SUCCESS);
    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 0);
}

void Test_BPNode_ClaOut_Stop_LtpNom(void)
{
    uint32 ContId = 0;

    BPNode_AppData.ConfigPtrs.ContactsConfigPtr->ContactSet[ContId].CLAType = BPLib_LTP_CLA;

    UtAssert_INT32_EQ(BPNode_ClaOut_Stop(ContId), BPLIB_SUCCESS);
    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 0);
}

void Test_BPNode_ClaOut_Stop_EppNom(void)
{
    uint32 ContId = 0;

    BPNode_AppData.ConfigPtrs.ContactsConfigPtr->ContactSet[ContId].CLAType = BPLib_EPP_CLA;

    UtAssert_INT32_EQ(BPNode_ClaOut_Stop(ContId), BPLIB_SUCCESS);
    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 0);
}

void Test_BPNode_ClaOut_Stop_TcpNom(void)
{
    uint32 ContId = 0;

    BPNode_AppData.ConfigPtrs.ContactsConfigPtr->ContactSet[ContId].CLAType = BPLib_TCP_CLA;

    UtAssert_INT32_EQ(BPNode_ClaOut_Stop(ContId), BPLIB_SUCCESS);
    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 0);
}

void Test_BPNode_ClaOut_Stop_Default(void)
{
    uint32 ContId = 0;

    BPNode_AppData.ConfigPtrs.ContactsConfigPtr->ContactSet[ContId].CLAType = 0xff;

    UtAssert_INT32_EQ(BPNode_ClaOut_Stop(ContId), BPLIB_SUCCESS);
    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 0);
}

void Test_BPNode_ClaOut_Teardown_UdpNom(void)
{
    uint32 ContId = 0;

    BPNode_AppData.ConfigPtrs.ContactsConfigPtr->ContactSet[ContId].CLAType = BPLib_TCP_CLA;

    UtAssert_VOIDCALL(BPNode_ClaOut_Teardown(ContId));
}


/* Register the test cases to execute with the unit test tool */
void UtTest_Setup(void)
{
    ADD_TEST(Test_BPNode_ClaOutCreateTasks_Nominal);
    ADD_TEST(Test_BPNode_ClaOutCreateTasks_TaskCrErr);

    ADD_TEST(Test_BPNode_ClaOut_TaskInit_Nominal);
    ADD_TEST(Test_BPNode_ClaOut_TaskInit_IdErr);
    ADD_TEST(Test_BPNode_ClaOut_TaskInit_FindByNameErr);
    ADD_TEST(Test_BPNode_ClaOut_TaskInit_DirErr);

    ADD_TEST(Test_BPNode_ClaOut_TaskMain_NoBundleAvailable);
    ADD_TEST(Test_BPNode_ClaOut_TaskMain_MaxBundles);
    ADD_TEST(Test_BPNode_ClaOut_TaskMain_NoEgress);
    ADD_TEST(Test_BPNode_ClaOut_TaskMain_FailedProcBundle);
    ADD_TEST(Test_BPNode_ClaOut_TaskMain_IdErr);
    ADD_TEST(Test_BPNode_ClaOut_TaskMain_StateErr);

    ADD_TEST(Test_BPNode_ClaOut_ProcessBundleOutput_SbNom);
    ADD_TEST(Test_BPNode_ClaOut_ProcessBundleOutput_UdpNom);
    ADD_TEST(Test_BPNode_ClaOut_ProcessBundleOutput_LtpNom);
    ADD_TEST(Test_BPNode_ClaOut_ProcessBundleOutput_EppNom);
    ADD_TEST(Test_BPNode_ClaOut_ProcessBundleOutput_TcpNom);
    ADD_TEST(Test_BPNode_ClaOut_ProcessBundleOutput_Default);
    ADD_TEST(Test_BPNode_ClaOut_ProcessBundleOutput_FailedBPLibEgress);
    ADD_TEST(Test_BPNode_ClaOut_ProcessBundleOutput_CLATimeout);

    ADD_TEST(Test_BPNode_ClaOut_Setup_UdpNom);
    ADD_TEST(Test_BPNode_ClaOut_Setup_PortErr);
    ADD_TEST(Test_BPNode_ClaOut_Setup_IpErr);
    ADD_TEST(Test_BPNode_ClaOut_Setup_SbNom);
    ADD_TEST(Test_BPNode_ClaOut_Setup_LtpNom);
    ADD_TEST(Test_BPNode_ClaOut_Setup_EppNom);
    ADD_TEST(Test_BPNode_ClaOut_Setup_TcpNom);
    ADD_TEST(Test_BPNode_ClaOut_Setup_Default);

    ADD_TEST(Test_BPNode_ClaOut_Start_UdpNom);
    ADD_TEST(Test_BPNode_ClaOut_Start_PspErr);
    ADD_TEST(Test_BPNode_ClaOut_Start_SbNom);
    ADD_TEST(Test_BPNode_ClaOut_Start_LtpNom);
    ADD_TEST(Test_BPNode_ClaOut_Start_EppNom);
    ADD_TEST(Test_BPNode_ClaOut_Start_TcpNom);
    ADD_TEST(Test_BPNode_ClaOut_Start_Default);

    ADD_TEST(Test_BPNode_ClaOut_Stop_UdpNom);
    ADD_TEST(Test_BPNode_ClaOut_Stop_PspErr);
    ADD_TEST(Test_BPNode_ClaOut_Stop_SbNom);
    ADD_TEST(Test_BPNode_ClaOut_Stop_LtpNom);
    ADD_TEST(Test_BPNode_ClaOut_Stop_EppNom);
    ADD_TEST(Test_BPNode_ClaOut_Stop_TcpNom);
    ADD_TEST(Test_BPNode_ClaOut_Stop_Default);
    
    ADD_TEST(Test_BPNode_ClaOut_Teardown_UdpNom);
}
