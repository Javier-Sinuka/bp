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
 * @file
 *
 * Auto-Generated stub implementations for functions defined in bpnode_task header
 */

#include "bpnode_task.h"
#include "utgenstub.h"

/*
 * ----------------------------------------------------
 * Generated stub function for BPNode_GetTaskData()
 * ----------------------------------------------------
 */
BPNode_TaskData_t *BPNode_GetTaskData(void)
{
    UT_GenStub_SetupReturnBuffer(BPNode_GetTaskData, BPNode_TaskData_t *);

    UT_GenStub_Execute(BPNode_GetTaskData, Basic, NULL);

    return UT_GenStub_GetReturnValue(BPNode_GetTaskData, BPNode_TaskData_t *);
}

/*
 * ----------------------------------------------------
 * Generated stub function for BPNode_TaskExit()
 * ----------------------------------------------------
 */
void BPNode_TaskExit(BPNode_TaskData_t *TaskData)
{
    UT_GenStub_AddParam(BPNode_TaskExit, BPNode_TaskData_t *, TaskData);

    UT_GenStub_Execute(BPNode_TaskExit, Basic, NULL);
}

/*
 * ----------------------------------------------------
 * Generated stub function for BPNode_TaskInit()
 * ----------------------------------------------------
 */
CFE_Status_t BPNode_TaskInit(BPNode_TaskData_t *TaskData)
{
    UT_GenStub_SetupReturnBuffer(BPNode_TaskInit, CFE_Status_t);

    UT_GenStub_AddParam(BPNode_TaskInit, BPNode_TaskData_t *, TaskData);

    UT_GenStub_Execute(BPNode_TaskInit, Basic, NULL);

    return UT_GenStub_GetReturnValue(BPNode_TaskInit, CFE_Status_t);
}

/*
 * ----------------------------------------------------
 * Generated stub function for BPNode_TaskMain()
 * ----------------------------------------------------
 */
void BPNode_TaskMain(void)
{

    UT_GenStub_Execute(BPNode_TaskMain, Basic, NULL);
}
