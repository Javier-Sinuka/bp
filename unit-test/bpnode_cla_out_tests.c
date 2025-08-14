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

/* Test BPNode_ClaOut_TaskMain when app state is started */
void Test_BPNode_ClaOut_TaskMain_NoBundleAvailable(void)
{
    uint32                      ContactId;
    BPLib_CLA_ContactRunState_t RunState;

    ContactId = BPLIB_MAX_NUM_CONTACTS - 1;
    RunState = BPLIB_CLA_STARTED;

    BPNode_AppData.ConfigPtrs.ContactsConfigPtr->ContactSet[ContactId].EgressBitsPerCycle = 100000;

    /* Test setup */
    UT_SetDataBuffer(UT_KEY(BPLib_CLA_GetContactRunState), &RunState, sizeof(BPLib_CLA_ContactRunState_t), false);
    UT_SetDeferredRetcode(UT_KEY(BPLib_CLA_Egress), 1, BPLIB_CLA_TIMEOUT);

    UtAssert_VOIDCALL(BPNode_ClaOut_TaskMain(ContactId));

    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 0);
    UtAssert_STUB_COUNT(BPLib_AS_Increment, 0);
}

/* Test BPNode_ClaOut_TaskMain when max number of bundles are egressed */
void Test_BPNode_ClaOut_TaskMain_SingleBundle(void)
{
    uint32                      ContactId;
    BPLib_CLA_ContactRunState_t RunState;

    ContactId = BPLIB_MAX_NUM_CONTACTS - 1;
    RunState  = BPLIB_CLA_STARTED;

    /* Test setup */
    UT_SetDataBuffer(UT_KEY(BPLib_CLA_GetContactRunState), &RunState, sizeof(BPLib_CLA_ContactRunState_t), false);
    UT_SetDeferredRetcode(UT_KEY(BPLib_CLA_Egress), 1, BPLIB_SUCCESS);
    UT_SetDeferredRetcode(UT_KEY(BPLib_CLA_Egress), 1, BPLIB_CLA_TIMEOUT);

    BPNode_AppData.ConfigPtrs.ContactsConfigPtr->ContactSet[ContactId].EgressBitsPerCycle = 100000;

    // TODO How to add more bundles?

    UtAssert_VOIDCALL(BPNode_ClaOut_TaskMain(ContactId));

    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 0);
}

/* Test BPNode_ClaOut_TaskMain when bundle egress is disabled */
void Test_BPNode_ClaOut_TaskMain_NoEgress(void)
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

    UtAssert_VOIDCALL(BPNode_ClaOut_TaskMain(ContactId));

    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 0);
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

void Test_BPNode_ClaOut_ProcessBundleOutput_SB_Nominal(void)
{
    uint32 ContactId;
    size_t BundleSize;

    ContactId = 0;
    BPNode_AppData.ConfigPtrs.ContactsConfigPtr->ContactSet[ContactId].CLAType = BPLib_SB_CLA;

    UtAssert_UINT32_EQ(BPNode_ClaOut_ProcessBundleOutput(ContactId, &BundleSize), CFE_SUCCESS);

    UtAssert_STUB_COUNT(CFE_SB_TransmitMsg, 1);
    UtAssert_STUB_COUNT(CFE_PSP_IODriver_Command, 0);
}

void Test_BPNode_ClaOut_ProcessBundleOutput_PSP_Nominal(void)
{
    uint32 ContactId;
    size_t BundleSize;

    ContactId = 0;

    UtAssert_UINT32_EQ(BPNode_ClaOut_ProcessBundleOutput(ContactId, &BundleSize), CFE_SUCCESS);

    UtAssert_STUB_COUNT(CFE_SB_TransmitMsg, 0);
    UtAssert_STUB_COUNT(CFE_PSP_IODriver_Command, 1);
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

void Test_BPNode_ClaOut_Setup_Nominal(void)
{
    BPLib_Status_t Status;
    uint32 ContId = 0;

    strcpy(BPNode_AppData.ConfigPtrs.ContactsConfigPtr->ContactSet[ContId].ClaOutAddr, "127.0.0.1");
    BPNode_AppData.ConfigPtrs.ContactsConfigPtr->ContactSet[ContId].ClaOutPort = 100;

    Status = BPNode_ClaOut_Setup(ContId);

    UtAssert_INT32_EQ(Status, BPLIB_SUCCESS);
    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 0);
}

void Test_BPNode_ClaOut_Start_Nominal(void)
{
    BPLib_Status_t Status;
    uint32 ContId = 0;

    Status = BPNode_ClaOut_Start(ContId);

    UtAssert_INT32_EQ(Status, BPLIB_SUCCESS);
    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 0);
}

void Test_BPNode_ClaOut_Stop_Nominal(void)
{
    BPLib_Status_t Status;
    uint32 ContId = 0;

    Status = BPNode_ClaOut_Stop(ContId);

    UtAssert_INT32_EQ(Status, BPLIB_SUCCESS);
    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 0);
}


/* Register the test cases to execute with the unit test tool */
void UtTest_Setup(void)
{
    ADD_TEST(Test_BPNode_ClaOutCreateTasks_Nominal);
    ADD_TEST(Test_BPNode_ClaOutCreateTasks_TaskCrErr);

    ADD_TEST(Test_BPNode_ClaOut_TaskInit_Nominal);
    ADD_TEST(Test_BPNode_ClaOut_TaskInit_FindByNameErr);
    ADD_TEST(Test_BPNode_ClaOut_TaskInit_DirErr);

    ADD_TEST(Test_BPNode_ClaOut_TaskMain_NoBundleAvailable);
    ADD_TEST(Test_BPNode_ClaOut_TaskMain_SingleBundle);
    ADD_TEST(Test_BPNode_ClaOut_TaskMain_NoEgress);
    ADD_TEST(Test_BPNode_ClaOut_TaskMain_FailedProcBundle);

    ADD_TEST(Test_BPNode_ClaOut_ProcessBundleOutput_SB_Nominal);
    ADD_TEST(Test_BPNode_ClaOut_ProcessBundleOutput_PSP_Nominal);
    ADD_TEST(Test_BPNode_ClaOut_ProcessBundleOutput_FailedBPLibEgress);
    ADD_TEST(Test_BPNode_ClaOut_ProcessBundleOutput_CLATimeout);

    ADD_TEST(Test_BPNode_ClaOut_Setup_Nominal);

    ADD_TEST(Test_BPNode_ClaOut_Start_Nominal);

    ADD_TEST(Test_BPNode_ClaOut_Stop_Nominal);
}
