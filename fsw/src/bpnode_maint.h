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
 *   This file contains the function definitions for the Maintenance Task
 */

#ifndef BPNODE_MAINT_H
#define BPNODE_MAINT_H

/*
** Include Files
*/

#include "cfe.h"
#include "bpnode_task.h"

/*
** Macro Definitions
*/

#define BPNODE_MAINT_BASE_NAME            "BPNODE.MAINT"  /** \brief Task base name */

/*
** Type Definitions
*/

/**
** \brief Maintenance Task Data
*/
typedef struct
{
    BPNode_TaskData_t TaskData;
} BPNode_MaintData_t;


/*
** Exported Functions
*/

/**
 * \brief Create Maintenance Task(s)
 *
 *  \par Description
 *       Initialize the task data and spawn the maintenance task
 *
 *  \par Assumptions, External Events, and Notes:
 *       - Note: This is the only function in this file called by the main task, all other
 *         functions are called by the child task
 *
 *  \return Validation status
 *  \retval #CFE_SUCCESS \copybrief CFE_SUCCESS
 *  \retval OSAL or cFE error code
 */
CFE_Status_t BPNode_MaintCreateTask(void);

/**
 * \brief Initialize provided Maintenance task
 *
 *  \par Description
 *       Initialize provided Maintenance task. This function is called as a 
 *       function pointer from BPNode_TaskInit
 *
 *  \par Assumptions, External Events, and Notes:
 *       None
 *
 *  \return Validation status
 *  \retval #CFE_SUCCESS \copybrief CFE_SUCCESS
 *  \retval OSAL or cFE error code
 */
CFE_Status_t BPNode_Maint_TaskInit(uint32 TaskId);

/**
 * \brief Maintenance Main Task
 *
 *  \par Description
 *       Maintenance main task operations. This function is called as a function 
 *       pointer from BPNode_TaskMain
 *
 *  \par Assumptions, External Events, and Notes:
 *       None
 */
void BPNode_Maint_TaskMain(uint32 TaskId);

#endif /* BPNODE_MAINT_H */
