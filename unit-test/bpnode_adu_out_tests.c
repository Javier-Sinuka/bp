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
    UtAssert_STRINGBUF_EQ("Failed to create ADU Out #%d child task. Error = 0x%08X.", BPLIB_EM_EXPANDED_EVENT_SIZE,
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
    UtAssert_STUB_COUNT(CFE_MSG_Init, 1);
}

/* Test BPNode_AduOut_TaskInit when the channel ID is invalid */
void Test_BPNode_AduOut_TaskInit_IdErr(void)
{
    uint32 ChanId = BPLIB_MAX_NUM_CHANNELS;

    UtAssert_INT32_EQ(BPNode_AduOut_TaskInit(ChanId), CFE_STATUS_RANGE_ERROR);

    BPNode_Test_Verify_Event(0, BPNODE_ADU_OUT_INIT_PTR_CRT_EID,
                                "Invalid channel ID %d passed into BPNode_AduOut_TaskInit function pointer.");
    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 1);
    UtAssert_STUB_COUNT(CFE_MSG_Init, 0);
}

/* Test BPNode_AduOut_TaskMain when app state is started */
void Test_BPNode_AduOut_TaskMain_Nominal(void)
{
    uint32 ChanId = 0;
    uint32 i;
    size_t AduSize = 10;
    size_t RateLimit = 100;
    size_t NumProcessedAdus = RateLimit / AduSize;
    size_t NumSentAdus = NumProcessedAdus + 1;

    /* Test setup */
    UT_SetDefaultReturnValue(UT_KEY(BPLib_NC_GetAppState), BPLIB_NC_APP_STATE_STARTED);
    for (i = 0; i < NumSentAdus; i++)
    {
        UT_SetDataBuffer(UT_KEY(BPA_ADUP_Out), &AduSize, sizeof(AduSize), false);
    }

    BPNode_AppData.AduOutData[ChanId].RateLimit = RateLimit * 8;

    UtAssert_VOIDCALL(BPNode_AduOut_TaskMain(ChanId));

    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 0);
    UtAssert_STUB_COUNT(BPLib_NC_GetAppState, 1);
    UtAssert_STUB_COUNT(BPA_ADUP_Out, NumProcessedAdus);
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

/* Test BPNode_AduOut_TaskMain when app state is started but an error occurs on ADU out */
void Test_BPNode_AduOut_TaskMain_OutErr(void)
{
    uint32 ChanId = 0;

    /* Test setup */
    UT_SetDefaultReturnValue(UT_KEY(BPLib_NC_GetAppState), BPLIB_NC_APP_STATE_STARTED);
    UT_SetDefaultReturnValue(UT_KEY(BPA_ADUP_Out), BPLIB_TIMEOUT);
    BPNode_AppData.AduOutData[ChanId].BitsEgressed = 0;
    BPNode_AppData.AduOutData[ChanId].RateLimit    = 1000;

    UtAssert_VOIDCALL(BPNode_AduOut_TaskMain(ChanId));

    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 0);
    UtAssert_STUB_COUNT(BPA_ADUP_Out, 1);
}

void Test_BPNode_AduOut_TaskMain_RateLimitedOver(void)
{
    uint32 ChanId           = 0;
    size_t OrigBitsEgressed = 5000;

    /* Test setup */
    UT_SetDefaultReturnValue(UT_KEY(BPLib_NC_GetAppState), BPLIB_NC_APP_STATE_STARTED);
    BPNode_AppData.AduOutData[ChanId].BitsEgressed = OrigBitsEgressed;
    BPNode_AppData.AduOutData[ChanId].RateLimit    = 1000;

    UtAssert_VOIDCALL(BPNode_AduOut_TaskMain(ChanId));

    UtAssert_EQ(size_t,
                BPNode_AppData.AduOutData[ChanId].BitsEgressed,
                OrigBitsEgressed - BPNode_AppData.AduOutData[ChanId].RateLimit);

    UtAssert_STUB_COUNT(BPA_ADUP_Out, 0);
}

void Test_BPNode_AduOut_TaskMain_RateLimitedUnder(void)
{
    uint32 ChanId = 0;

    /* Test setup */
    UT_SetDefaultReturnValue(UT_KEY(BPLib_NC_GetAppState), BPLIB_NC_APP_STATE_STARTED);
    UT_SetDefaultReturnValue(UT_KEY(BPA_ADUP_Out), BPLIB_TIMEOUT);
    BPNode_AppData.AduOutData[ChanId].BitsEgressed = 900;
    BPNode_AppData.AduOutData[ChanId].RateLimit    = 1000;

    UtAssert_VOIDCALL(BPNode_AduOut_TaskMain(ChanId));

    UtAssert_EQ(size_t,
                BPNode_AppData.AduOutData[ChanId].BitsEgressed,
                0);

    UtAssert_STUB_COUNT(BPA_ADUP_Out, 1);
}

/* Test BPNode_AduOut_TaskMain when the channel ID is invalid */
void Test_BPNode_AduOut_TaskMain_IdErr(void)
{
    uint32 ChanId = BPLIB_MAX_NUM_CHANNELS;

    UtAssert_VOIDCALL(BPNode_AduOut_TaskMain(ChanId));

    BPNode_Test_Verify_Event(0, BPNODE_ADU_OUT_MAIN_PTR_CRT_EID,
                                "Invalid channel ID %d passed into BPNode_AduOut_TaskMain function pointer.");
    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 1);
    UtAssert_STUB_COUNT(BPLib_NC_GetAppState, 0);
}

/* Register the test cases to execute with the unit test tool */
void UtTest_Setup(void)
{
    ADD_TEST(Test_BPNode_AduOutCreateTasks_Nominal);
    ADD_TEST(Test_BPNode_AduOutCreateTasks_TaskCrErr);

    ADD_TEST(Test_BPNode_AduOut_TaskInit_Nominal);
    ADD_TEST(Test_BPNode_AduOut_TaskInit_IdErr);

    ADD_TEST(Test_BPNode_AduOut_TaskMain_Nominal);
    ADD_TEST(Test_BPNode_AduOut_TaskMain_AppStopped);
    ADD_TEST(Test_BPNode_AduOut_TaskMain_OutErr);
    ADD_TEST(Test_BPNode_AduOut_TaskMain_RateLimitedOver);
    ADD_TEST(Test_BPNode_AduOut_TaskMain_RateLimitedUnder);
    ADD_TEST(Test_BPNode_AduOut_TaskMain_IdErr);
}
