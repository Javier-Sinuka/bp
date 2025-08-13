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
 *   This file contains the implementation for generic child task architecture functions.
 *   The ADU In/Out, CLA In/Out, and Generic Worker child tasks all use these functions
 *   for their general task architecture logic.
 */

#ifndef BPNODE_TASK_H
#define BPNODE_TASK_H

#include "cfe.h"

/*
** Macro Definitions
*/

#define BPNODE_TASK_INVALID_ID 0xFFFFFFFF       /** \brief Invalid task ID */


/*
** Type Definitions
*/

/**
** \brief General child task initialization function pointer type
*/
typedef CFE_Status_t (*BPNode_TaskInitFunc_t)(uint32 TaskId);

/**
** \brief General child task main operations function pointer type
*/
typedef void (*BPNode_TaskMainFunc_t)(uint32 TaskId);


/**
** \brief General child task data
*/
typedef struct
{
    CFE_ES_TaskId_t CfeTaskId;                  /** \brief cFE-assigned task ID */
    char            Type[OS_MAX_API_NAME];      /** \brief Human-readable type of task (ADU In/Out, CLA In/Out or Gen Worker) */
    uint32          PerfId;                     /** \brief Performance ID for child task */
    uint32          RunStatus;                  /** \brief cFE run status */
    uint32          TaskId;                     /** \brief BPNode identifier of task, unique within each task type but not globally */
    uint16          InitEid;                    /** \brief Initialization event ID */
    uint16          NotifErrEid;                /** \brief Notification error event ID */
    uint16          ExitEid;                    /** \brief Exit event ID */

    BPNode_TaskInitFunc_t TaskInitFunc;         /** \brief Child task type-specific initialization function */
    BPNode_TaskMainFunc_t TaskMainFunc;         /** \brief Child task type-specific main operations function */

} BPNode_TaskData_t;

/*
** Exported Functions
*/

/** \brief Initialize task
 *
 *  \par Description
 *       Initialize a child task by entering the performance log, calling its type-specific
 *       initialization function, setting the initialization notification, and issuing
 *       a successful initialization event message
 *
 *  \par Assumptions, External Events, and Notes:
 *       None
 * 
 *  \param[in] TaskData Pointer to task-specific data
 *
 *  \return Execution status, see \ref CFEReturnCodes
 *  \retval #CFE_SUCCESS \copybrief CFE_SUCCESS
 */
CFE_Status_t BPNode_TaskInit(BPNode_TaskData_t *TaskData);

/** \brief Get task data
 *
 *  \par Description
 *       Get task data for calling child task
 *
 *  \par Assumptions, External Events, and Notes:
 *       None
 *
 *  \return Pointer to task data location in BPNode_AppData struct
 */
BPNode_TaskData_t* BPNode_GetTaskData(void);

/** \brief Exit provided task
 *
 *  \par Description
 *       Exit provided task gracefully
 *
 *  \par Assumptions, External Events, and Notes:
 *       None
 *
 *  \param[in] TaskData Pointer to task-specific data
 */
void BPNode_TaskExit(BPNode_TaskData_t *TaskData);

/** \brief Main task
 *
 *  \par Description
 *       Main task runner for all child tasks. It initializes the child task, starts the
 *       general notification-driven run loop, and calls the task-specific main task 
 *       function to perform the child task operations.
 *
 *  \par Assumptions, External Events, and Notes:
 *       None
 */
void BPNode_TaskMain(void);

#endif /* BPNODE_TASK_H */
