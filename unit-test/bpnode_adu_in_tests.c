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
 *  Unit tests for bpnode_adu_in.c
 */

/*
** Include Files
*/

#include "bpnode_adu_in.h"
#include "bpnode_test_utils.h"


/*
** Function Definitions
*/

/* Test BPNode_AduInCreateTasks when everything succeeds */
void Test_BPNode_AduInCreateTasks_Nominal(void)
{
    UtAssert_INT32_EQ(BPNode_AduInCreateTasks(), CFE_SUCCESS);

    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 0);
    UtAssert_STUB_COUNT(CFE_ES_CreateChildTask, BPLIB_MAX_NUM_CHANNELS);
}

/* Test BPNode_AduInCreateTasks when the child task creation fails */
void Test_BPNode_AduInCreateTasks_TaskCrErr(void)
{
    UT_SetDeferredRetcode(UT_KEY(CFE_ES_CreateChildTask), 1, CFE_ES_ERR_CHILD_TASK_CREATE);

    UtAssert_INT32_EQ(BPNode_AduInCreateTasks(), CFE_ES_ERR_CHILD_TASK_CREATE);

    /* Verify event was issued */
    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 1);
    BPNode_Test_Verify_Event(0, BPNODE_ADU_IN_CREATE_ERR_EID, 
                                "Failed to create ADU In #%d child task. Error = 0x%08X.");

    UtAssert_STUB_COUNT(CFE_ES_CreateChildTask, 1);
}

/* Test BPNode_AduIn_TaskInit when everything succeeds */
void Test_BPNode_AduIn_TaskInit_Nominal(void)
{
    uint32 ChanId = 0;

    UtAssert_INT32_EQ(BPNode_AduIn_TaskInit(ChanId), CFE_SUCCESS);

    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 0);
    UtAssert_STUB_COUNT(CFE_SB_CreatePipe, 1);
}

/* Test BPNode_AduIn_TaskInit when the channel ID is invalid */
void Test_BPNode_AduIn_TaskInit_IdErr(void)
{
    uint32 ChanId = BPLIB_MAX_NUM_CHANNELS;

    UtAssert_INT32_EQ(BPNode_AduIn_TaskInit(ChanId), CFE_STATUS_RANGE_ERROR);

    BPNode_Test_Verify_Event(0, BPNODE_ADU_IN_INIT_PTR_CRT_EID, 
                                "Invalid channel ID %d passed into BPNode_AduIn_TaskInit function pointer.");
    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 1);
    UtAssert_STUB_COUNT(CFE_SB_CreatePipe, 0);
}

/* Test BPNode_AduIn_TaskInit when pipe creation fails */
void Test_BPNode_AduIn_TaskInit_PipeErr(void)
{
    uint32 ChanId = 0;

    UT_SetDeferredRetcode(UT_KEY(CFE_SB_CreatePipe), 1, CFE_SB_PIPE_CR_ERR);

    UtAssert_INT32_EQ(BPNode_AduIn_TaskInit(ChanId), CFE_SB_PIPE_CR_ERR);

    BPNode_Test_Verify_Event(0, BPNODE_ADU_IN_CR_PIPE_ERR_EID, 
                                "[ADU In #%d]: Error creating SB ADU Pipe, Error = %d");
    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 1);
    UtAssert_STUB_COUNT(CFE_SB_CreatePipe, 1);
}


/* Test BPNode_AduIn_TaskMain when app state is started and one ADU is received */
void Test_BPNode_AduIn_TaskMain_Nominal(void)
{
    CFE_SB_Buffer_t  Buf;
    CFE_SB_Buffer_t *BufPtr = &Buf;
    uint32 ChanId = 0;
    size_t AduSize = 10;

    /* Test setup */
    UT_SetDataBuffer(UT_KEY(CFE_SB_ReceiveBuffer), &BufPtr, sizeof(BufPtr), false);
    UT_SetDeferredRetcode(UT_KEY(CFE_SB_ReceiveBuffer), 1, CFE_SUCCESS);
    UT_SetDeferredRetcode(UT_KEY(CFE_SB_ReceiveBuffer), 1, CFE_SB_TIME_OUT);
    UT_SetDefaultReturnValue(UT_KEY(BPLib_NC_GetAppState), BPLIB_NC_APP_STATE_STARTED);
    UT_SetDataBuffer(UT_KEY(BPA_ADUP_In), &AduSize, sizeof(AduSize), false);

    BPNode_AppData.BplibInst.ChanCtxt[ChanId].Config.IngressBitsPerCycle = 10000000000;

    UtAssert_VOIDCALL(BPNode_AduIn_TaskMain(ChanId));

    UtAssert_STUB_COUNT(CFE_SB_ReceiveBuffer, 2);
    UtAssert_STUB_COUNT(BPA_ADUP_In, 1);
}


/* Test BPNode_AduIn_TaskMain when app state is started and max ADU rate is received */
void Test_BPNode_AduIn_TaskMain_MaxAdus(void)
{
    CFE_SB_Buffer_t  Buf;
    CFE_SB_Buffer_t *BufPtr = &Buf;
    uint32 ChanId = 0;
    uint32 i;
    size_t AduSize = 10;
    size_t RateLimit = 100;
    size_t NumProcessedAdus = RateLimit / AduSize;
    size_t NumSentAdus = NumProcessedAdus + 1;

    /* Test setup */
    UT_SetDefaultReturnValue(UT_KEY(CFE_SB_ReceiveBuffer), CFE_SUCCESS);
    UT_SetDefaultReturnValue(UT_KEY(BPLib_NC_GetAppState), BPLIB_NC_APP_STATE_STARTED);

    for (i = 0; i < NumSentAdus; i++)
    {
        UT_SetDataBuffer(UT_KEY(CFE_SB_ReceiveBuffer), &BufPtr, sizeof(BufPtr), false);
        UT_SetDataBuffer(UT_KEY(BPA_ADUP_In), &AduSize, sizeof(AduSize), false);
    }

    BPNode_AppData.BplibInst.ChanCtxt[ChanId].Config.IngressBitsPerCycle = RateLimit * 8;

    UtAssert_VOIDCALL(BPNode_AduIn_TaskMain(ChanId));

    UtAssert_STUB_COUNT(CFE_SB_ReceiveBuffer, NumProcessedAdus);
    UtAssert_STUB_COUNT(BPA_ADUP_In, NumProcessedAdus);
}

/* Test BPNode_AduIn_TaskMain when app state is started and a null ADU is received */
void Test_BPNode_AduIn_TaskMain_NullBuf(void)
{
    CFE_SB_Buffer_t *BufPtr = NULL;
    uint32 ChanId = 0;

    /* Test setup */
    UT_SetDataBuffer(UT_KEY(CFE_SB_ReceiveBuffer), &BufPtr, sizeof(BufPtr), false);
    UT_SetDeferredRetcode(UT_KEY(CFE_SB_ReceiveBuffer), 1, CFE_SUCCESS);
    UT_SetDeferredRetcode(UT_KEY(CFE_SB_ReceiveBuffer), 1, CFE_SB_TIME_OUT);
    UT_SetDefaultReturnValue(UT_KEY(BPLib_NC_GetAppState), BPLIB_NC_APP_STATE_STARTED);

    BPNode_AppData.BplibInst.ChanCtxt[ChanId].Config.IngressBitsPerCycle = 100000;

    UtAssert_VOIDCALL(BPNode_AduIn_TaskMain(ChanId));
    
    UtAssert_STUB_COUNT(CFE_SB_ReceiveBuffer, 2);
    UtAssert_STUB_COUNT(BPA_ADUP_In, 0);
}

/* Test BPNode_AduIn_TaskMain when app state is stopped */
void Test_BPNode_AduIn_TaskMain_AppStopped(void)
{
    uint32 ChanId = 0;

    /* Test setup */
    UT_SetDefaultReturnValue(UT_KEY(BPLib_NC_GetAppState), BPLIB_NC_APP_STATE_STOPPED);

    UtAssert_VOIDCALL(BPNode_AduIn_TaskMain(ChanId));
    
    UtAssert_STUB_COUNT(CFE_SB_ReceiveBuffer, 0);
}

/* Test BPNode_AduIn_TaskMain when the app was just stopped and the pipe needs to be cleared */
void Test_BPNode_AduIn_TaskMain_ClearPipe(void)
{
    CFE_SB_Buffer_t  Buf;
    CFE_SB_Buffer_t *BufPtr = &Buf;
    uint32 ChanId = 0;

    /* Clear one message from pipe */
    UT_SetDeferredRetcode(UT_KEY(CFE_SB_ReceiveBuffer), 1, CFE_SUCCESS);
    UT_SetDeferredRetcode(UT_KEY(CFE_SB_ReceiveBuffer), 1, CFE_SB_NO_MESSAGE);
    UT_SetDataBuffer(UT_KEY(CFE_SB_ReceiveBuffer), &BufPtr, sizeof(BufPtr), false);
    UT_SetDataBuffer(UT_KEY(CFE_SB_ReceiveBuffer), &BufPtr, sizeof(BufPtr), false);
    UT_SetDefaultReturnValue(UT_KEY(BPLib_NC_GetAppState), BPLIB_NC_APP_STATE_STOPPED);

    BPNode_AppData.AduInData[ChanId].ClearPipe = true;

    UtAssert_VOIDCALL(BPNode_AduIn_TaskMain(ChanId));

    UtAssert_STUB_COUNT(CFE_SB_ReceiveBuffer, 2);
    UtAssert_STUB_COUNT(BPA_ADUP_In, 0);
    UtAssert_BOOL_FALSE(BPNode_AppData.AduInData[ChanId].ClearPipe);
}

/* Test BPNode_AduIn_TaskMain when the channel ID is invalid */
void Test_BPNode_AduIn_TaskMain_IdErr(void)
{
    uint32 ChanId = BPLIB_MAX_NUM_CHANNELS;

    UtAssert_VOIDCALL(BPNode_AduIn_TaskMain(ChanId));

    BPNode_Test_Verify_Event(0, BPNODE_ADU_IN_MAIN_PTR_CRT_EID, 
                                "Invalid channel ID %d passed into BPNode_AduIn_TaskMain function pointer.");
    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 1);
    UtAssert_STUB_COUNT(BPLib_NC_GetAppState, 0);
}

void Test_BPNode_AduIn_TaskMain_RateLimitedOver(void)
{
    uint32 ChanId            = 0;
    size_t OrigBitsIngressed = 5000;

    /* Test setup */
    UT_SetDefaultReturnValue(UT_KEY(BPLib_NC_GetAppState), BPLIB_NC_APP_STATE_STARTED);
    BPNode_AppData.AduInData[ChanId].BitsIngressed = OrigBitsIngressed;
    BPNode_AppData.BplibInst.ChanCtxt[ChanId].Config.IngressBitsPerCycle     = 1000;

    UtAssert_VOIDCALL(BPNode_AduIn_TaskMain(ChanId));

    UtAssert_EQ(size_t,
                BPNode_AppData.AduInData[ChanId].BitsIngressed,
                OrigBitsIngressed - BPNode_AppData.BplibInst.ChanCtxt[ChanId].Config.IngressBitsPerCycle);

    UtAssert_STUB_COUNT(BPA_ADUP_In, 0);
}

void Test_BPNode_AduIn_TaskMain_RateLimitedUnder(void)
{
    uint32 ChanId = 0;

    /* Test setup */
    UT_SetDefaultReturnValue(UT_KEY(BPLib_NC_GetAppState), BPLIB_NC_APP_STATE_STARTED);
    UT_SetDefaultReturnValue(UT_KEY(CFE_SB_ReceiveBuffer), CFE_SB_BAD_ARGUMENT);
    BPNode_AppData.AduOutData[ChanId].BitsEgressed = 900;
    BPNode_AppData.BplibInst.ChanCtxt[ChanId].Config.IngressBitsPerCycle     = 1000;

    UtAssert_VOIDCALL(BPNode_AduIn_TaskMain(ChanId));

    UtAssert_EQ(size_t,
                BPNode_AppData.AduInData[ChanId].BitsIngressed,
                0);

    UtAssert_STUB_COUNT(BPA_ADUP_In, 0);
}

/* Register the test cases to execute with the unit test tool */
void UtTest_Setup(void)
{
    ADD_TEST(Test_BPNode_AduInCreateTasks_Nominal);
    ADD_TEST(Test_BPNode_AduInCreateTasks_TaskCrErr);

    ADD_TEST(Test_BPNode_AduIn_TaskInit_Nominal);
    ADD_TEST(Test_BPNode_AduIn_TaskInit_IdErr);
    ADD_TEST(Test_BPNode_AduIn_TaskInit_PipeErr);

    ADD_TEST(Test_BPNode_AduIn_TaskMain_Nominal);
    ADD_TEST(Test_BPNode_AduIn_TaskMain_MaxAdus);
    ADD_TEST(Test_BPNode_AduIn_TaskMain_NullBuf);
    ADD_TEST(Test_BPNode_AduIn_TaskMain_AppStopped);
    ADD_TEST(Test_BPNode_AduIn_TaskMain_ClearPipe);
    ADD_TEST(Test_BPNode_AduIn_TaskMain_IdErr);
    ADD_TEST(Test_BPNode_AduIn_TaskMain_RateLimitedOver);
    ADD_TEST(Test_BPNode_AduIn_TaskMain_RateLimitedUnder);
}
