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
 *   This file contains the function definitions for the Generic Worker Task(s)
 */

#ifndef BPNODE_GEN_WORKER_H
#define BPNODE_GEN_WORKER_H

/*
** Include Files
*/

#include "cfe.h"
#include "bpnode_task.h"

/*
** Macro Definitions
*/

#define BPNODE_GEN_WRKR_BASE_NAME            "BPNODE.WRKR"  /** \brief Task base name */

/*
** Type Definitions
*/

/**
** \brief Generic Worker Task Data
*/
typedef struct
{
    BPNode_TaskData_t TaskData;
    int32             BPLibWorkerId;
} BPNode_GenWorkerData_t;


/*
** Exported Functions
*/

/**
 * \brief Create Generic Worker Task(s)
 *
 *  \par Description
 *       Initialize the task data and spawn all generic worker child task(s)
 *
 *  \par Assumptions, External Events, and Notes:
 *       - Note: This is the only function in this file called by the main task, all other
 *         functions are called by the child task(s)
 *
 *  \return Validation status
 *  \retval #CFE_SUCCESS \copybrief CFE_SUCCESS
 *  \retval OSAL or cFE error code
 */
CFE_Status_t BPNode_GenWorkerCreateTasks(void);

/**
 * \brief Initialize provided Generic Worker task
 *
 *  \par Description
 *       Initialize provided Generic Worker task. This function is called as a 
 *       function pointer from BPNode_TaskInit
 *
 *  \par Assumptions, External Events, and Notes:
 *       None
 *
 *  \param[in] WorkerId Pointer to worker ID to set
 *
 *  \return Validation status
 *  \retval #CFE_SUCCESS \copybrief CFE_SUCCESS
 *  \retval OSAL or cFE error code
 */
CFE_Status_t BPNode_GenWorker_TaskInit(uint32 WorkerId);

/**
 * \brief Generic Worker Main Task
 *
 *  \par Description
 *       Generic Worker main task operations. This function is called as a function 
 *       pointer from BPNode_TaskMain
 *
 *  \par Assumptions, External Events, and Notes:
 *       None
 */
void BPNode_GenWorker_TaskMain(uint32 WorkerId);

#endif /* BPNODE_GEN_WORKER_H */
