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
 *  Unit tests for bpnode_maint.c
 */

/*
** Include Files
*/

#include "bpnode_maint.h"
#include "bpnode_test_utils.h"


/*
** Function Definitions
*/

/* Test nominal task creation */
void Test_BPNode_MaintCreateTask_Nominal(void)
{
    UtAssert_INT32_EQ(BPNode_MaintCreateTask(), CFE_SUCCESS);

    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 0);
    UtAssert_STUB_COUNT(CFE_ES_CreateChildTask, 1);
}

/* Test task creation when child task creation fails */
void Test_BPNode_MaintCreateTask_CrErr(void)
{
    UT_SetDefaultReturnValue(UT_KEY(CFE_ES_CreateChildTask), CFE_ES_BAD_ARGUMENT);

    UtAssert_INT32_EQ(BPNode_MaintCreateTask(), CFE_ES_BAD_ARGUMENT);

    UtAssert_STUB_COUNT(CFE_ES_CreateChildTask, 1);
    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 1);
    BPNode_Test_Verify_Event(0, BPNODE_MAINT_CREATE_ERR_EID, 
                "Failed to create Maintenance Task. Error = 0x%08X.");    
}

/* Test nominal task initialization */
void Test_BPNode_Maint_TaskInit_Nominal(void)
{
    uint32 TaskId = 0;

    UtAssert_INT32_EQ(BPNode_Maint_TaskInit(TaskId), CFE_SUCCESS);
}

/* Test maintenace main loop runs nominal tasks once per second */
void Test_BPNode_Maint_TaskMain_Nominal(void)
{
    uint32 TaskId = 0;

    UtAssert_VOIDCALL(BPNode_Maint_TaskMain(TaskId));

    UtAssert_STUB_COUNT(BPLib_TIME_MaintenanceActivities, 1);
    UtAssert_STUB_COUNT(BPLib_STOR_FlushPending, 1);
    UtAssert_STUB_COUNT(BPLib_STOR_GarbageCollect, 1);
    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 0);
}

/* Test maintenace main loop does nothing when woken up outside of the 1hz rate */
void Test_BPNode_Maint_TaskMain_QuietWakeup(void)
{
    #if BPNODE_MAX_EXP_WAKEUP_RATE != 0
    uint32 TaskId = 0;

    UT_SetDeferredRetcode(UT_KEY(BPNode_NotifGetCount), 1, BPNODE_MAX_EXP_WAKEUP_RATE - 1);

    UtAssert_VOIDCALL(BPNode_Maint_TaskMain(TaskId));

    UtAssert_STUB_COUNT(BPLib_TIME_MaintenanceActivities, 0);
    UtAssert_STUB_COUNT(BPLib_STOR_FlushPending, 0);
    UtAssert_STUB_COUNT(BPLib_STOR_GarbageCollect, 0);
    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 0);
    #endif
}

/* Test main task after failing time maintenance activities */
void Test_BPNode_Maint_TaskMain_TimeErr(void)
{
    uint32 TaskId = 0;

    /* Fail Time activities */
    UT_SetDeferredRetcode(UT_KEY(BPLib_TIME_MaintenanceActivities), 1, BPLIB_TIME_WRITE_ERROR);

    UtAssert_VOIDCALL(BPNode_Maint_TaskMain(TaskId));

    UtAssert_STUB_COUNT(BPLib_TIME_MaintenanceActivities, 1);
    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 1);
    BPNode_Test_Verify_Event(0, BPNODE_TIME_WKP_ERR_EID, 
                "[Maintenance Task]: Error doing time maintenance activities, RC = %d");
}

/* Register the test cases to execute with the unit test tool */
void UtTest_Setup(void)
{
    ADD_TEST(Test_BPNode_MaintCreateTask_Nominal);
    ADD_TEST(Test_BPNode_MaintCreateTask_CrErr);
    
    ADD_TEST(Test_BPNode_Maint_TaskInit_Nominal);

    ADD_TEST(Test_BPNode_Maint_TaskMain_Nominal);
    ADD_TEST(Test_BPNode_Maint_TaskMain_QuietWakeup);
    ADD_TEST(Test_BPNode_Maint_TaskMain_TimeErr);
}
