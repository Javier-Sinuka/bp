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
 *   This file contains the function definitions for the CLA Out Task(s)
 */


#ifndef BPNODE_CLA_OUT_H
#define BPNODE_CLA_OUT_H

/*
** Include Files
*/

#include "cfe.h"
#include "iodriver_base.h"
#include "iodriver_packet_io.h"
#include "bplib.h"
#include "bpnode_platform_cfg.h"
#include "bpnode_task.h"

/*
** Macro Definitions
*/

#define BPNODE_CLA_OUT_BASE_NAME              "BPNODE.CLA_OUT"       /** \brief Task base name */
#define BPNODE_CLA_PSP_OUTPUT_BUFFER_SIZE     (BPLIB_MAX_BUNDLE_LEN) /** \brief IODriver output buffer size*/


/*
** Type Definitions
*/

/**
 * \brief CLA Out bundle packet
 */
typedef struct
{
    CFE_MSG_TelemetryHeader_t TelemetryHeader; /** \brief Telemtry header for space packet wrapped around bundle */
    uint8                     Payload[BPNODE_CLA_PSP_OUTPUT_BUFFER_SIZE];
} BPNode_ClaOut_Buffer_t;

/**
** \brief CLA Out Task Data
*/
typedef struct
{
    BPNode_TaskData_t TaskData;

    /* IODriver usock_intf related*/
    CFE_PSP_IODriver_Direction_t Dir;
    CFE_PSP_IODriver_Location_t  PspLocation;

    /* CLA Out bundle/packet */
    BPNode_ClaOut_Buffer_t OutBuffer;

    size_t            RateLimit;
} BPNode_ClaOutData_t;


/*
** Exported Functions
*/

/**
  * \brief     Create all CLA Out task(s)
  * \return    Execution status
  * \retval    CFE_SUCCESS: Successful execution
  * \retval    CFE errors from CFE_ES_CreateChildTask
  */
CFE_Status_t BPNode_ClaOutCreateTasks(void);

/**
 * \brief     Initialize a CLA Out task
 * \par       Description
 *            Initialize provided CLA Out task. This function is called as a function pointer from
 *            BPNode_TaskInit
 * \param[in] ContactId (uint32) Index into the various contact info tracking
 *                                 arrays that corresponds to that contact's info
 * \return    Execution status
 * \retval    CFE_SUCCESS: Successful execution
 * \retval    PSP errors from CFE_PSP_IODriver_FindByName
 * \retval    PSP errors from CFE_PSP_IODriver_Command
 */
CFE_Status_t BPNode_ClaOut_TaskInit(uint32 ContactId);

/**
 * \brief CLA Out Main Task
 *
 *  \par Description
 *       CLA Out main task operations. This function is called as a function pointer from
 *       BPNode_TaskMain
 *
 *  \par Assumptions, External Events, and Notes:
 *       None
 */
void BPNode_ClaOut_TaskMain(uint32 ContactId);

/**
 * \brief Process Bundle Output to CLA
 *
 *  \par Description
 *       Receive the bundle from Bundle Interface and send the bundle to CL.
 *
 *  \par Assumptions, External Events, and Notes:
 *       None
 *
 *  \param[in] ContId Contact ID
 *  \param[out] MsgSize Size of bundle to output
 *
 *  \return Execution status, see \ref CFEReturnCodes
 *  \retval #CFE_SUCCESS \copybrief CFE_SUCCESS
 */
int32 BPNode_ClaOut_ProcessBundleOutput(uint32 ContId, size_t *MsgSize);

/**
  * \brief     Set up a CLA out task
  * \param[in] ContactId Index into the various contact info tracking arrays that
  *                      corresponds to that contact's info
  * \return    Execution status
  * \retval    BPLIB_SUCCESS: Successful execution
  * \retval    BPLIB_CLA_IO_ERROR: A I/O driver API call failed operation
  */
 BPLib_Status_t BPNode_ClaOut_Setup(uint32 ContactId);

/**
  * \brief     Start up a CLA Out task
  * \note      Create a CLA Out child tasks and signal to the main task that
  *            the task is running
  * \param[in] ContactId (uint32) Index into the various contact info tracking
  *                               arrays that corresponds to that contact's info
  * \return    Execution status
  * \retval    BPLIB_SUCCESS: Successful execution
  * \retval    BPLIB_CLA_IO_ERROR: UDP conntection couldn't be set to running
  */
BPLib_Status_t BPNode_ClaOut_Start(uint32 ContactId);

/**
  * \brief     Stop a CLA Out task
  * \param[in] ContactId (uint32) Index into the various contact info tracking
  *                                 arrays that corresponds to that contact's info
  * \return    Execution status
  * \retval    PSP errors from CFE_PSP_IODriver_Command
  */
BPLib_Status_t BPNode_ClaOut_Stop(uint32 ContactId);

/**
  * \brief     Teardown a CLA Out task
  * \note      Nothing is implemented as of right now
  * \param[in] ContactId (uint32) Index into the various contact info tracking
  *                                 arrays that corresponds to that contact's info
  * \return    void
  */
void BPNode_ClaOut_Teardown(uint32 ContactId);

#endif /* BPNODE_CLA_OUT_H */
