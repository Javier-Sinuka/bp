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
    UtAssert_STRINGBUF_EQ("[Generic Worker #%d]: Failed to create child task. Error = %d.", BPLIB_EM_EXPANDED_EVENT_SIZE,
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

/* Test BPNode_GenWorker_TaskMain when semaphore take succeeds and max num jobs are run */
void Test_BPNode_GenWorker_TaskMain_Nominal(void)
{
    uint32 WorkerId = 0;

    UtAssert_VOIDCALL(BPNode_GenWorker_TaskMain(WorkerId));

    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 0);
    UtAssert_STUB_COUNT(BPLib_QM_WorkerRunJob, BPNODE_NUM_JOBS_PER_CYCLE);
}

/* Register the test cases to execute with the unit test tool */
void UtTest_Setup(void)
{
    ADD_TEST(Test_BPNode_GenWorkerCreateTasks_Nominal);
    ADD_TEST(Test_BPNode_GenWorkerCreateTasks_TaskCrErr);

    ADD_TEST(Test_BPNode_GenWorker_TaskInit_Nominal);

    ADD_TEST(Test_BPNode_GenWorker_TaskMain_Nominal);
}
