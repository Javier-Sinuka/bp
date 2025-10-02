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
 *   This file contains the function definitions for the ADU Out Task(s)
 */

#ifndef BPNODE_ADU_OUT_H
#define BPNODE_ADU_OUT_H

/*
** Include Files
*/

#include "cfe.h"
#include "bpnode_task.h"
#include "bplib.h"

/*
** Macro Definitions
*/

#define BPNODE_ADU_OUT_BASE_NAME            "BPNODE.ADU_TX" /** \brief Task base name */


/*
** Type Definitions
*/

/** 
** \brief Generic buffer for outgoing ADUs
*/
typedef struct 
{
    CFE_MSG_TelemetryHeader_t TelemetryHeader;
    uint8 Payload[BPLIB_MAX_PAYLOAD_SIZE];
} BPNode_AduOutBuf_t;


/** 
** \brief ADU Out Task Data
*/
typedef struct
{
    BPNode_TaskData_t  TaskData;
    bool               AduWrapping;
    CFE_SB_MsgId_t     SendToMsgId;
    BPNode_AduOutBuf_t OutBuf;
    size_t             RateLimit;
    size_t             BitsEgressed;
} BPNode_AduOutData_t;


/*
** Exported Functions
*/

/**
 * \brief Create ADU Out Task(s)
 *
 *  \par Description
 *       Initialize the task data and spawn all ADU Out child task(s)
 *
 *  \par Assumptions, External Events, and Notes:
 *       - Note: This is the only function in this file called by the main task, all other
 *         functions are called by the child task(s)
 *
 *  \return Validation status
 *  \retval #CFE_SUCCESS \copybrief CFE_SUCCESS
 *  \retval OSAL or cFE error code
 */
CFE_Status_t BPNode_AduOutCreateTasks(void);

/**
 * \brief Initialize provided ADU Out task
 *
 *  \par Description
 *       Initialize provided ADU Out task. This function is called as a function pointer
 *       from BPNode_TaskInit
 *
 *  \par Assumptions, External Events, and Notes:
 *       None
 *
 *  \param[in] ChanId Pointer to channel ID to set
 *
 *  \return Validation status
 *  \retval #CFE_SUCCESS \copybrief CFE_SUCCESS
 *  \retval OSAL or cFE error code
 */
CFE_Status_t BPNode_AduOut_TaskInit(uint32 ChanId);

/**
 * \brief ADU Out Main Task
 *
 *  \par Description
 *       ADU Out main task operations. This function is called as a function pointer from
 *       BPNode_TaskMain
 *
 *  \par Assumptions, External Events, and Notes:
 *       None
 */
void BPNode_AduOut_TaskMain(uint32 ChanId);

#endif /* BPNODE_ADU_OUT_H */
