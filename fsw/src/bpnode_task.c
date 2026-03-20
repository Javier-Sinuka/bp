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

#include "bpnode_app.h"
#include "bpnode_task.h"

/* Generic child task initialization function */
CFE_Status_t BPNode_TaskInit(BPNode_TaskData_t *TaskData)
{
    CFE_Status_t Status;

    /* Start performance log */
    BPLib_PL_PerfLogEntry(TaskData->PerfId);

    Status = TaskData->TaskInitFunc(TaskData->TaskId);

    if (Status == CFE_SUCCESS)
    {
        /* Notify main task that this task has initialized */
        BPNode_NotifSet(&BPNode_AppData.ChildTaskInitNotif);
        
        TaskData->RunStatus = CFE_ES_RunStatus_APP_RUN;

        BPLib_EM_SendEvent(TaskData->InitEid, BPLib_EM_EventType_INFORMATION,
                      "[%s]: Child Task Initialized.", TaskData->Name);        
    }

    return Status;
}

/* Exit child task */
void BPNode_TaskExit(BPNode_TaskData_t *TaskData)
{
    BPLib_EM_SendEvent(TaskData->ExitEid, BPLib_EM_EventType_CRITICAL,
                      "[%s]: Terminating Task. RunStatus = %d.",
                      TaskData->Name, TaskData->RunStatus);

    /* In case event services is not working, add a message to the system log */
    CFE_ES_WriteToSysLog("[%s]: Terminating Task. RunStatus = %d.\n",
                      TaskData->Name, TaskData->RunStatus);

    /* Exit the perf log */
    BPLib_PL_PerfLogExit(TaskData->PerfId);

    /* Notify main task that this task has exited */
    BPNode_NotifSet(&BPNode_AppData.ChildTaskExitNotif);

    /* Stop execution */
    CFE_ES_ExitChildTask();
}

/* Get task data of this child task */
BPNode_TaskData_t* BPNode_GetTaskData(void)
{
    BPNode_TaskData_t *TaskData = NULL;
    CFE_ES_TaskId_t    CfeTaskId;
    CFE_Status_t       Status;
    uint32             i;

    /* Get the task ID of currently running child task */
    Status = CFE_ES_GetTaskID(&CfeTaskId);
    if (Status != CFE_SUCCESS)
    {
        BPLib_EM_SendEvent(BPNODE_TASK_NO_ID_ERR_EID, BPLib_EM_EventType_ERROR,
                          "[Child task #?]: Failed to get task ID. Error = %d.", Status);
        return NULL;
    }

    /* Find the task data that contains this cFE task ID */

    if (CfeTaskId == BPNode_AppData.MaintData.TaskData.CfeTaskId)
    {
        TaskData = &(BPNode_AppData.MaintData.TaskData);
        return TaskData;
    }

    for (i = 0; i < BPLIB_MAX_NUM_CHANNELS; i++)
    {
        if (CfeTaskId == BPNode_AppData.AduInData[i].TaskData.CfeTaskId)
        {
            TaskData = &(BPNode_AppData.AduInData[i].TaskData);
            return TaskData;
        }
        else if (CfeTaskId == BPNode_AppData.AduOutData[i].TaskData.CfeTaskId)
        {
            TaskData = &(BPNode_AppData.AduOutData[i].TaskData);
            return TaskData;
        }
    }

    for (i = 0; i < BPLIB_MAX_NUM_CONTACTS; i++)
    {
        if (CfeTaskId == BPNode_AppData.ClaInData[i].TaskData.CfeTaskId)
        {
            TaskData = &(BPNode_AppData.ClaInData[i].TaskData);
            return TaskData;
        }
        else if (CfeTaskId == BPNode_AppData.ClaOutData[i].TaskData.CfeTaskId)
        {
            TaskData = &(BPNode_AppData.ClaOutData[i].TaskData);
            return TaskData;
        }
    }

    for (i = 0; i < BPNODE_NUM_GEN_WRKR_TASKS; i++)
    {
        if (CfeTaskId == BPNode_AppData.GenWorkerData[i].TaskData.CfeTaskId)
        {
            TaskData = &(BPNode_AppData.GenWorkerData[i].TaskData);
            return TaskData;
        }        
    }

    return TaskData;
}

/* Generic child task main function */
void BPNode_TaskMain(void)
{
    int32 Status;
    BPNode_TaskData_t *TaskData;
    uint32 RunCount = 0;

    /* Get the relevant task data for this calling task */
    TaskData = BPNode_GetTaskData();
    if (TaskData == NULL || TaskData->TaskInitFunc == NULL || TaskData->TaskMainFunc == NULL)
    {
        /* Task data could not be determined, immediately shut down */
        BPLib_EM_SendEvent(BPNODE_TASK_UNK_EXIT_CRIT_EID, BPLib_EM_EventType_CRITICAL,
                    "Terminating unknown child task.");

        /* In case event services is not working, add a message to the system log */
        CFE_ES_WriteToSysLog("Terminating unknown child task.\n");

        CFE_ES_ExitChildTask();

        return;
    }

    /* Once task data has been obtained, continue remaining task initialization */
    Status = BPNode_TaskInit(TaskData);
    if (Status != CFE_SUCCESS)
    {
        TaskData->RunStatus = CFE_ES_RunStatus_APP_ERROR;
    }

    /* General task runloop */
    while(CFE_ES_RunLoop(&TaskData->RunStatus))
    {
        /* Wait for the main task to notify child tasks that it's time to start work */
        BPLib_PL_PerfLogExit(TaskData->PerfId);
        Status = BPNode_NotifWait(&BPNode_AppData.ChildStartWorkNotif, 
                                                    RunCount, BPNODE_WAKEUP_WAIT_MSEC);
        BPLib_PL_PerfLogEntry(TaskData->PerfId);

        if (Status == OS_SUCCESS)
        {
            /* Save notification's run count for use in the next wakeup */
            RunCount = BPNode_NotifGetCount(&BPNode_AppData.ChildStartWorkNotif);

            /* Call task type-specific main function */
            TaskData->TaskMainFunc(TaskData->TaskId);
        }
        else if (Status != OS_ERROR_TIMEOUT)
        {
            BPLib_EM_SendEvent(TaskData->NotifErrEid, BPLib_EM_EventType_ERROR,
                                "[%s]: Error pending on notification, RC = %d",
                                TaskData->Name, Status);
        }
    }

    /* Exit gracefully */
    BPNode_TaskExit(TaskData);

    return;
}