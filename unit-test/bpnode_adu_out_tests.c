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
 *  Unit tests for bpnode_adu_out.c
 */

/*
** Include Files
*/

#include "bpnode_adu_out.h"
#include "bpnode_test_utils.h"


/*
** Function Definitions
*/

/* Test BPNode_AduOutCreateTasks when everything succeeds */
void Test_BPNode_AduOutCreateTasks_Nominal(void)
{
    UtAssert_INT32_EQ(BPNode_AduOutCreateTasks(), CFE_SUCCESS);

    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 0);
    UtAssert_STUB_COUNT(CFE_ES_CreateChildTask, BPLIB_MAX_NUM_CHANNELS);
}

/* Test BPNode_AduOutCreateTasks when the child task creation fails */
void Test_BPNode_AduOutCreateTasks_TaskCrErr(void)
{
    UT_SetDeferredRetcode(UT_KEY(CFE_ES_CreateChildTask), 1, CFE_ES_ERR_CHILD_TASK_CREATE);

    UtAssert_INT32_EQ(BPNode_AduOutCreateTasks(), CFE_ES_ERR_CHILD_TASK_CREATE);

    UtAssert_INT32_EQ(context_BPLib_EM_SendEvent[0].EventID, BPNODE_ADU_OUT_CREATE_ERR_EID);
    UtAssert_STRINGBUF_EQ("[ADU Out #%d]: Failed to create child task. Error = %d.", BPLIB_EM_EXPANDED_EVENT_SIZE,
                            context_BPLib_EM_SendEvent[0].Spec, BPLIB_EM_EXPANDED_EVENT_SIZE);
    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 1);
    UtAssert_STUB_COUNT(CFE_ES_CreateChildTask, 1);
}

/* Test BPNode_AduOut_TaskInit when everything succeeds */
void Test_BPNode_AduOut_TaskInit_Nominal(void)
{
    uint32 ChanId = 0;

    UtAssert_INT32_EQ(BPNode_AduOut_TaskInit(ChanId), CFE_SUCCESS);

    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 0);
}

/* Test BPNode_AduOut_TaskMain when app state is started */
void Test_BPNode_AduOut_TaskMain_Nominal(void)
{
    uint32 ChanId = 0;
    // size_t AduSize = 10;
    // uint16 i;

    /* Test setup */
    UT_SetDefaultReturnValue(UT_KEY(BPLib_NC_GetAppState), BPLIB_NC_APP_STATE_STARTED);
    // BPNode_UT_BundleProcessLoops(BPNODE_ADU_OUT_MAX_ADUS_PER_CYCLE);

    // for (i = 0; i < BPNODE_ADU_OUT_MAX_ADUS_PER_CYCLE; i++)
    // {
    //     UT_SetDataBuffer(UT_KEY(BPA_ADUP_Out), &AduSize, sizeof(AduSize), false);
    // }

    BPNode_AppData.ConfigPtrs.ChanConfigPtr->Configs[ChanId].EgressBitsPerCycle = 10000000000;

    UtAssert_VOIDCALL(BPNode_AduOut_TaskMain(ChanId));

    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 0);
    UtAssert_STUB_COUNT(BPLib_NC_GetAppState, 1);
}

/* Test BPNode_AduOut_TaskMain when app state is stopped */
void Test_BPNode_AduOut_TaskMain_AppStopped(void)
{
    uint32 ChanId = 0;

    /* Test setup */
    UT_SetDefaultReturnValue(UT_KEY(BPLib_NC_GetAppState), BPLIB_NC_APP_STATE_STOPPED);

    UtAssert_VOIDCALL(BPNode_AduOut_TaskMain(ChanId));

    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 0);
}

/* Register the test cases to execute with the unit test tool */
void UtTest_Setup(void)
{
    ADD_TEST(Test_BPNode_AduOutCreateTasks_Nominal);
    ADD_TEST(Test_BPNode_AduOutCreateTasks_TaskCrErr);

    ADD_TEST(Test_BPNode_AduOut_TaskInit_Nominal);

    ADD_TEST(Test_BPNode_AduOut_TaskMain_Nominal);
    ADD_TEST(Test_BPNode_AduOut_TaskMain_AppStopped);
}
