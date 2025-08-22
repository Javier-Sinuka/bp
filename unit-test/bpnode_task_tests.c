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
 *  Unit tests for bpnode_task.c
 */

/*
** Include Files
*/

#include "bplib.h"
#include "bpnode_test_utils.h"

/*
** Function Definitions
*/

/* Test BPNode_TaskInit in nominal case */
void Test_BPNode_TaskInit_Nominal(void)
{
    BPNode_TaskData_t TaskData;

    TaskData.TaskInitFunc = BPNode_AduIn_TaskInit;
    TaskData.InitEid = BPNODE_ADU_IN_INIT_INF_EID;

    UtAssert_INT32_EQ(BPNode_TaskInit(&TaskData), CFE_SUCCESS);

    UtAssert_STUB_COUNT(BPLib_PL_PerfLogEntry, 1);
    UtAssert_STUB_COUNT(BPNode_NotifSet, 1);
    UtAssert_UINT32_EQ(TaskData.RunStatus, CFE_ES_RunStatus_APP_RUN);
    BPNode_Test_Verify_Event(0, BPNODE_ADU_IN_INIT_INF_EID, 
                                "[%s #%d]: Child Task Initialized.");
}

/* Test BPNode_TaskInit when the initialization function pointer returns an error */
void Test_BPNode_TaskInit_FuncErr(void)
{
    BPNode_TaskData_t TaskData;

    TaskData.TaskInitFunc = BPNode_AduIn_TaskInit;
    TaskData.RunStatus = CFE_ES_RunStatus_APP_ERROR;

    UT_SetDefaultReturnValue(UT_KEY(BPNode_AduIn_TaskInit), CFE_STATUS_EXTERNAL_RESOURCE_FAIL);

    UtAssert_INT32_EQ(BPNode_TaskInit(&TaskData), CFE_STATUS_EXTERNAL_RESOURCE_FAIL);

    UtAssert_STUB_COUNT(BPLib_PL_PerfLogEntry, 1);
    UtAssert_STUB_COUNT(BPNode_NotifSet, 0);
    UtAssert_UINT32_EQ(TaskData.RunStatus, CFE_ES_RunStatus_APP_ERROR);
    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 0);
}

/* Test BPNode_TaskExit in nominal shutdown */
void Test_BPNode_TaskExit_Nominal(void)
{
    BPNode_TaskData_t TaskData;

    TaskData.ExitEid = BPNODE_ADU_IN_EXIT_CRT_EID;

    UtAssert_VOIDCALL(BPNode_TaskExit(&TaskData));

    BPNode_Test_Verify_Event(0, BPNODE_ADU_IN_EXIT_CRT_EID, 
                                "[%s #%d]: Terminating Task. RunStatus = %d.");    
    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 1);
    UtAssert_STUB_COUNT(CFE_ES_WriteToSysLog, 1);
    UtAssert_STUB_COUNT(BPLib_PL_PerfLogExit, 1);
    UtAssert_STUB_COUNT(BPNode_NotifSet, 1);
    UtAssert_STUB_COUNT(CFE_ES_ExitChildTask, 1);
}

/* Test that BPNode_GetTaskData returns the right task data pointer in nominal ADU In case */
void Test_BPNode_GetTaskData_AduIn(void)
{
    CFE_ES_TaskId_t CfeTaskId  = 1234;
    uint32 ChanId = 0;

    BPNode_AppData.AduInData[ChanId].TaskData.CfeTaskId = CfeTaskId;

    UT_SetDataBuffer(UT_KEY(CFE_ES_GetTaskID), &CfeTaskId, sizeof(CfeTaskId), false);

    UtAssert_ADDRESS_EQ(BPNode_GetTaskData(), &(BPNode_AppData.AduInData[ChanId].TaskData));
}

/* Test that BPNode_GetTaskData returns null when no match is found */
void Test_BPNode_GetTaskData_NoMatch(void)
{
    CFE_ES_TaskId_t CfeTaskId  = 1234;

    /* All task IDs in app data should default to 0 */

    UT_SetDataBuffer(UT_KEY(CFE_ES_GetTaskID), &CfeTaskId, sizeof(CfeTaskId), false);

    UtAssert_NULL(BPNode_GetTaskData());
}

/* Test that BPNode_GetTaskData returns null when getting the task ID returns an error */
void Test_BPNode_GetTaskData_GetIdErr(void)
{
    UT_SetDefaultReturnValue(UT_KEY(CFE_ES_GetTaskID), CFE_ES_ERR_RESOURCEID_NOT_VALID);
    
    UtAssert_NULL(BPNode_GetTaskData());
    BPNode_Test_Verify_Event(0, BPNODE_TASK_NO_ID_ERR_EID, 
                                "[Child task #?]: Failed to get task ID. Error = %d.");  
}

/* Test BPNode_TaskMain for a nominal single run loop */
void Test_BPNode_TaskMain_Nominal(void)
{
    CFE_ES_TaskId_t CfeTaskId  = 1234;
    uint32 ChanId = 0;

    BPNode_AppData.AduInData[ChanId].TaskData.CfeTaskId = CfeTaskId;
    BPNode_AppData.AduInData[ChanId].TaskData.TaskInitFunc = BPNode_AduIn_TaskInit;
    BPNode_AppData.AduInData[ChanId].TaskData.TaskMainFunc = BPNode_AduIn_TaskMain;

    UT_SetDataBuffer(UT_KEY(CFE_ES_GetTaskID), &CfeTaskId, sizeof(CfeTaskId), false);
    UT_SetDeferredRetcode(UT_KEY(CFE_ES_RunLoop), 1, true);     /* Run once */

    UtAssert_VOIDCALL(BPNode_TaskMain());

    UtAssert_STUB_COUNT(BPNode_NotifWait, 1);
    UtAssert_STUB_COUNT(BPNode_AduIn_TaskMain, 1);
    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 2);
}

/* Test BPNode_TaskMain when task data cannot be determined */
void Test_BPNode_TaskMain_NoTaskData(void)
{
    uint32 ChanId = 0;

    BPNode_AppData.AduInData[ChanId].TaskData.TaskInitFunc = BPNode_AduIn_TaskInit;
    BPNode_AppData.AduInData[ChanId].TaskData.TaskMainFunc = BPNode_AduIn_TaskMain;

    UT_SetDefaultReturnValue(UT_KEY(CFE_ES_GetTaskID), CFE_STATUS_EXTERNAL_RESOURCE_FAIL);

    UtAssert_VOIDCALL(BPNode_TaskMain());

    UtAssert_STUB_COUNT(CFE_ES_RunLoop, 0);
    UtAssert_STUB_COUNT(BPNode_NotifWait, 0);
    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 2);
    UtAssert_STUB_COUNT(CFE_ES_WriteToSysLog, 1);
    UtAssert_STUB_COUNT(CFE_ES_ExitChildTask, 1);
    BPNode_Test_Verify_Event(1, BPNODE_TASK_UNK_EXIT_CRIT_EID, 
                                "Terminating unknown child task.");  
}

/* Test BPNode_TaskMain when the task's specific init function is null */
void Test_BPNode_TaskMain_NoMainFunc(void)
{
    CFE_ES_TaskId_t CfeTaskId  = 1234;
    uint32 ChanId = 0;

    BPNode_AppData.AduInData[ChanId].TaskData.CfeTaskId = CfeTaskId;
    BPNode_AppData.AduInData[ChanId].TaskData.TaskInitFunc = BPNode_AduIn_TaskInit;
    BPNode_AppData.AduInData[ChanId].TaskData.TaskMainFunc = NULL;

    UT_SetDataBuffer(UT_KEY(CFE_ES_GetTaskID), &CfeTaskId, sizeof(CfeTaskId), false);

    UtAssert_VOIDCALL(BPNode_TaskMain());

    UtAssert_STUB_COUNT(CFE_ES_RunLoop, 0);
    UtAssert_STUB_COUNT(BPNode_NotifWait, 0);
    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 1);
    UtAssert_STUB_COUNT(CFE_ES_WriteToSysLog, 1);
    UtAssert_STUB_COUNT(CFE_ES_ExitChildTask, 1);
    BPNode_Test_Verify_Event(0, BPNODE_TASK_UNK_EXIT_CRIT_EID, 
                                "Terminating unknown child task.");  
}

/* Test BPNode_TaskMain when task initialization fails */
void Test_BPNode_TaskMain_InitErr(void)
{
    CFE_ES_TaskId_t CfeTaskId  = 1234;
    uint32 ChanId = 0;

    BPNode_AppData.AduInData[ChanId].TaskData.CfeTaskId = CfeTaskId;
    BPNode_AppData.AduInData[ChanId].TaskData.TaskInitFunc = BPNode_AduIn_TaskInit;
    BPNode_AppData.AduInData[ChanId].TaskData.TaskMainFunc = BPNode_AduIn_TaskMain;

    UT_SetDataBuffer(UT_KEY(CFE_ES_GetTaskID), &CfeTaskId, sizeof(CfeTaskId), false);
    UT_SetDefaultReturnValue(UT_KEY(BPNode_AduIn_TaskInit), CFE_STATUS_EXTERNAL_RESOURCE_FAIL);
    UT_SetDeferredRetcode(UT_KEY(CFE_ES_RunLoop), 1, false);
    
    UtAssert_VOIDCALL(BPNode_TaskMain());

    UtAssert_STUB_COUNT(BPNode_NotifWait, 0);
    UtAssert_STUB_COUNT(BPNode_AduIn_TaskMain, 0);
    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 1);
}

/* Test BPNode_TaskMain when the task's specific main function is null */
void Test_BPNode_TaskMain_NoInitFunc(void)
{
    CFE_ES_TaskId_t CfeTaskId  = 1234;
    uint32 ChanId = 0;

    BPNode_AppData.AduInData[ChanId].TaskData.CfeTaskId = CfeTaskId;
    BPNode_AppData.AduInData[ChanId].TaskData.TaskInitFunc = NULL;
    BPNode_AppData.AduInData[ChanId].TaskData.TaskMainFunc = BPNode_AduIn_TaskMain;

    UT_SetDataBuffer(UT_KEY(CFE_ES_GetTaskID), &CfeTaskId, sizeof(CfeTaskId), false);

    UtAssert_VOIDCALL(BPNode_TaskMain());

    UtAssert_STUB_COUNT(CFE_ES_RunLoop, 0);
    UtAssert_STUB_COUNT(BPNode_NotifWait, 0);
    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 1);
    UtAssert_STUB_COUNT(CFE_ES_WriteToSysLog, 1);
    UtAssert_STUB_COUNT(CFE_ES_ExitChildTask, 1);
    BPNode_Test_Verify_Event(0, BPNODE_TASK_UNK_EXIT_CRIT_EID, 
                                "Terminating unknown child task.");  
}

/* Test BPNode_TaskMain when the notif times out */
void Test_BPNode_TaskMain_Timeout(void)
{
    CFE_ES_TaskId_t CfeTaskId  = 1234;
    uint32 ChanId = 0;

    BPNode_AppData.AduInData[ChanId].TaskData.CfeTaskId = CfeTaskId;
    BPNode_AppData.AduInData[ChanId].TaskData.TaskInitFunc = BPNode_AduIn_TaskInit;
    BPNode_AppData.AduInData[ChanId].TaskData.TaskMainFunc = BPNode_AduIn_TaskMain;

    UT_SetDataBuffer(UT_KEY(CFE_ES_GetTaskID), &CfeTaskId, sizeof(CfeTaskId), false);
    UT_SetDeferredRetcode(UT_KEY(CFE_ES_RunLoop), 1, true);     /* Run once */
    UT_SetDefaultReturnValue(UT_KEY(BPNode_NotifWait), OS_ERROR_TIMEOUT);

    UtAssert_VOIDCALL(BPNode_TaskMain());

    UtAssert_STUB_COUNT(BPNode_NotifWait, 1);
    UtAssert_STUB_COUNT(BPNode_AduIn_TaskMain, 0);
    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 2);
}

/* Test BPNode_TaskMain when the notif returns an error */
void Test_BPNode_TaskMain_NotifErr(void)
{
    CFE_ES_TaskId_t CfeTaskId  = 1234;
    uint32 ChanId = 0;

    BPNode_AppData.AduInData[ChanId].TaskData.CfeTaskId = CfeTaskId;
    BPNode_AppData.AduInData[ChanId].TaskData.TaskInitFunc = BPNode_AduIn_TaskInit;
    BPNode_AppData.AduInData[ChanId].TaskData.TaskMainFunc = BPNode_AduIn_TaskMain;
    BPNode_AppData.AduInData[ChanId].TaskData.NotifErrEid = BPNODE_ADU_IN_NOTIF_ERR_EID;
    
    UT_SetDataBuffer(UT_KEY(CFE_ES_GetTaskID), &CfeTaskId, sizeof(CfeTaskId), false);
    UT_SetDeferredRetcode(UT_KEY(CFE_ES_RunLoop), 1, true);     /* Run once */
    UT_SetDefaultReturnValue(UT_KEY(BPNode_NotifWait), OS_ERROR);

    UtAssert_VOIDCALL(BPNode_TaskMain());

    UtAssert_STUB_COUNT(BPNode_NotifWait, 1);
    UtAssert_STUB_COUNT(BPNode_AduIn_TaskMain, 0);
    UtAssert_STUB_COUNT(BPLib_EM_SendEvent, 3);
    BPNode_Test_Verify_Event(1, BPNODE_ADU_IN_NOTIF_ERR_EID, 
                                "[%s #%d]: Error pending on notification, RC = %d");      
}

void UtTest_Setup(void)
{
    ADD_TEST(Test_BPNode_TaskInit_Nominal);
    ADD_TEST(Test_BPNode_TaskInit_FuncErr);

    ADD_TEST(Test_BPNode_TaskExit_Nominal);

    ADD_TEST(Test_BPNode_GetTaskData_AduIn);
    ADD_TEST(Test_BPNode_GetTaskData_NoMatch);
    ADD_TEST(Test_BPNode_GetTaskData_GetIdErr);

    ADD_TEST(Test_BPNode_TaskMain_Nominal);
    ADD_TEST(Test_BPNode_TaskMain_NoTaskData);
    ADD_TEST(Test_BPNode_TaskMain_NoInitFunc);
    ADD_TEST(Test_BPNode_TaskMain_NoMainFunc);
    ADD_TEST(Test_BPNode_TaskMain_InitErr);
    ADD_TEST(Test_BPNode_TaskMain_Timeout);
    ADD_TEST(Test_BPNode_TaskMain_NotifErr);
}
