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
 *  Unit tests for bpnode_gen_worker.c
 */

/*
** Include Files
*/

#include "bpnode_gen_worker.h"
#include "bpnode_test_utils.h"


/*
** Function Definitions
*/

/* Test BPNode_GenWorkerCreateTasks when everything succeeds */
void Test_BPNode_GenWorkerCreateTasks_Nominal(void)
{
    UtAssert_INT32_EQ(BPNode_GenWorkerCreateTasks(), CFE_SUCCESS);

    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 0);
    UtAssert_STUB_COUNT(CFE_ES_CreateChildTask, BPNODE_NUM_GEN_WRKR_TASKS);
}

/* Test BPNode_GenWorkerCreateTasks when the child task creation fails */
void Test_BPNode_GenWorkerCreateTasks_TaskCrErr(void)
{
    UT_SetDeferredRetcode(UT_KEY(CFE_ES_CreateChildTask), 1, CFE_ES_ERR_CHILD_TASK_CREATE);

    UtAssert_INT32_EQ(BPNode_GenWorkerCreateTasks(), CFE_ES_ERR_CHILD_TASK_CREATE);

    UtAssert_INT32_EQ(context_BPLib_EM_SendEvent[0].EventID, BPNODE_GEN_WRKR_CREATE_ERR_EID);
    UtAssert_STRINGBUF_EQ("Failed to create Generic Worker #%d child task. Error = 0x%08X.", BPLIB_EM_EXPANDED_EVENT_SIZE,
                            context_BPLib_EM_SendEvent[0].Spec, BPLIB_EM_EXPANDED_EVENT_SIZE);
    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 1);
    UtAssert_STUB_COUNT(CFE_ES_CreateChildTask, 1);
}

/* Test BPNode_GenWorker_TaskInit when everything succeeds */
void Test_BPNode_GenWorker_TaskInit_Nominal(void)
{
    uint32 WorkerId = 0;

    UtAssert_INT32_EQ(BPNode_GenWorker_TaskInit(WorkerId), CFE_SUCCESS);

    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 0);
    UtAssert_STUB_COUNT(BPLib_QM_RegisterWorker, 1);
}


/* Test BPNode_GenWorker_TaskInit when the contact ID is invalid */
void Test_BPNode_GenWorker_TaskInit_IdErr(void)
{
    uint32 WorkerId = BPNODE_NUM_GEN_WRKR_TASKS;

    UtAssert_INT32_EQ(BPNode_GenWorker_TaskInit(WorkerId), CFE_STATUS_RANGE_ERROR);

    BPNode_Test_Verify_Event(0, BPNODE_GEN_WRKR_INIT_PTR_CRT_EID, 
                                "Invalid worker ID %d passed into BPNode_GenWorker_TaskInit function pointer.");
    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 1);
    UtAssert_STUB_COUNT(BPLib_QM_RegisterWorker, 0);
}

/* Test BPNode_GenWorker_TaskInit when registering the worker fails */
void Test_BPNode_GenWorker_TaskInit_RegErr(void)
{
    uint32 WorkerId = 0;

    UT_SetDeferredRetcode(UT_KEY(BPLib_QM_RegisterWorker), 1, BPLIB_ERROR);

    UtAssert_INT32_EQ(BPNode_GenWorker_TaskInit(WorkerId), CFE_STATUS_EXTERNAL_RESOURCE_FAIL);

    BPNode_Test_Verify_Event(0, BPNODE_GEN_WRKR_REGISTER_ERR_EID, 
                                "[Generic Worker #%d]: Failed to register worker with BPLib. Status = %d");
    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 1);
    UtAssert_STUB_COUNT(BPLib_QM_RegisterWorker, 1);
}

/* Test BPNode_GenWorker_TaskMain when max num jobs are run */
void Test_BPNode_GenWorker_TaskMain_Nominal(void)
{
    uint32 WorkerId = 0;

    UtAssert_VOIDCALL(BPNode_GenWorker_TaskMain(WorkerId));

    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 0);
    UtAssert_STUB_COUNT(BPLib_QM_WorkerRunJob, BPNODE_NUM_JOBS_PER_CYCLE);
}

/* Test BPNode_GenWorker_TaskMain when a timeout occurs */
void Test_BPNode_GenWorker_TaskMain_Timeout(void)
{
    uint32 WorkerId = 0;

    UT_SetDeferredRetcode(UT_KEY(BPLib_QM_WorkerRunJob), 1, BPLIB_TIMEOUT);

    UtAssert_VOIDCALL(BPNode_GenWorker_TaskMain(WorkerId));

    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 0);
    UtAssert_STUB_COUNT(BPLib_QM_WorkerRunJob, 1);
}

/* Test BPNode_GenWorker_TaskMain when another error occurs when trying to run a job */
void Test_BPNode_GenWorker_TaskMain_JobErr(void)
{
    uint32 WorkerId = 0;

    UT_SetDeferredRetcode(UT_KEY(BPLib_QM_WorkerRunJob), 1, BPLIB_ERROR);

    UtAssert_VOIDCALL(BPNode_GenWorker_TaskMain(WorkerId));

    BPNode_Test_Verify_Event(0, BPNODE_GEN_WRKR_TASKRUN_ERR_EID, 
                            "[Generic Worker #%d]: Failed to run job, BPLib RC = %d");
    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 1);
    UtAssert_STUB_COUNT(BPLib_QM_WorkerRunJob, 1);
}

/* Test BPNode_GenWorker_TaskMain when the worker ID is invalid */
void Test_BPNode_GenWorker_TaskMain_IdErr(void)
{
    uint32 ChanId = BPLIB_MAX_NUM_CHANNELS;

    UtAssert_VOIDCALL(BPNode_GenWorker_TaskMain(ChanId));

    BPNode_Test_Verify_Event(0, BPNODE_GEN_WRKR_MAIN_PTR_CRT_EID, 
                                "Invalid worker ID %d passed into BPNode_GenWorker_TaskMain function pointer.");
    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 1);
    UtAssert_STUB_COUNT(BPLib_QM_WorkerRunJob, 0);
}

/* Register the test cases to execute with the unit test tool */
void UtTest_Setup(void)
{
    ADD_TEST(Test_BPNode_GenWorkerCreateTasks_Nominal);
    ADD_TEST(Test_BPNode_GenWorkerCreateTasks_TaskCrErr);

    ADD_TEST(Test_BPNode_GenWorker_TaskInit_Nominal);
    ADD_TEST(Test_BPNode_GenWorker_TaskInit_IdErr);
    ADD_TEST(Test_BPNode_GenWorker_TaskInit_RegErr);

    ADD_TEST(Test_BPNode_GenWorker_TaskMain_Nominal);
    ADD_TEST(Test_BPNode_GenWorker_TaskMain_JobErr);
    ADD_TEST(Test_BPNode_GenWorker_TaskMain_Timeout);
    ADD_TEST(Test_BPNode_GenWorker_TaskMain_IdErr);
}
