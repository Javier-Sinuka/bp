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
 *   This file contains the implementation for generic child task functions
 */

#ifndef BPNODE_TASK_H
#define BPNODE_TASK_H

#include "cfe.h"

/*
** Macro Definitions
*/

#define BPNODE_TASK_INVALID_ID 0xFFFFFFFF


/*
** Type Definitions
*/

typedef CFE_Status_t (*BPNode_TaskInitFunc_t)(uint32 TaskId);
typedef void (*BPNode_TaskMainFunc_t)(uint32 TaskId);


/**
** \brief Task Data
*/
typedef struct
{
    CFE_ES_TaskId_t CfeTaskId;
    char            Name[OS_MAX_API_NAME];
    char            Type[OS_MAX_API_NAME];
    uint32          PerfId;
    uint32          RunStatus;
    uint32          TaskId;

    BPNode_TaskInitFunc_t TaskInitFunc;
    BPNode_TaskMainFunc_t TaskMainFunc;

} BPNode_TaskData_t;

/*
** Exported Functions
*/

CFE_Status_t BPNode_TaskInit(BPNode_TaskData_t *TaskData);

BPNode_TaskData_t* BPNode_GetTaskData(void);

/** \brief Exit provided task
 *
 *  \par Description
 *       Exit task gracefully
 *
 *  \par Assumptions, External Events, and Notes:
 *       None
 *
 *  \param[in] ID Identification for task
 */
void BPNode_TaskExit(BPNode_TaskData_t *TaskData);

void BPNode_TaskMain(void);

#endif /* BPNODE_TASK_H */
