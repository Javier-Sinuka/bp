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
 *   This file contains the implementation for a thread-safe signaling event
 */

#ifndef BPNODE_NOTIF_H
#define BPNODE_NOTIF_H


/*
** Include Files
*/

#include "cfe.h"


/*
** Type Definitions
*/

/**
** \brief Notification variable
*/
typedef struct BPNode_Notif
{
    uint32    Count;
    osal_id_t CondVar;
} BPNode_Notif_t;

/*
** Exported Functions
*/

/**
 * \brief Initialize notification
 *
 *  \par Description
 *       Create condition variable and set notification count to 0
 *
 *  \par Assumptions, External Events, and Notes:
 *       None
 *
 *  \param[in] Notif Pointer to new notification variable
 *  \param[in] NotifName Name of notification
 *
 *  \return Execution status, see \ref OSReturnCodes
 *  \retval #OS_SUCCESS \copybrief OS_SUCCESS
 */
int32 BPNode_NotifInit(BPNode_Notif_t* Notif, const char* NotifName);

/**
 * \brief Destroy notification
 *
 *  \par Description
 *       Destroy condition variable
 *
 *  \par Assumptions, External Events, and Notes:
 *       None
 *
 *  \param[in] Notif Pointer to notification variable
 */
void BPNode_NotifDestroy(BPNode_Notif_t* Notif);

/**
 * \brief Set notification
 *
 *  \par Description
 *       Set notification variable by incrementing its count
 *
 *  \par Assumptions, External Events, and Notes:
 *       None
 *
 *  \param[in] Notif Pointer to notification variable
 */
void BPNode_NotifSet(BPNode_Notif_t* Notif);

/**
 * \brief Get notification count
 *
 *  \par Description
 *       Get notification count
 *
 *  \par Assumptions, External Events, and Notes:
 *       None
 *
 *  \param[in] Notif Pointer to notification variable
 *
 *  \return Value of notification count
 */
uint32 BPNode_NotifGetCount(BPNode_Notif_t* Notif);

/**
 * \brief Wait for notification
 *
 *  \par Description
 *       Wait until notification that the notification count no longer matches its old
 *       value
 *
 *  \par Assumptions, External Events, and Notes:
 *       None
 *
 *  \param[in] Notif Pointer to new notification variable
 *  \param[in] OldCount Old value of notification value
 *  \param[in] TimeoutMs How long to wait before timing out (in milliseconds)
 *
 *  \return Execution status, see \ref OSReturnCodes
 *  \retval #OS_SUCCESS \copybrief OS_SUCCESS
 */
int32 BPNode_NotifWait(BPNode_Notif_t* Notif, uint32 OldCount, int32 TimeoutMs);

/**
 * \brief Wait for exact notification
 *
 *  \par Description
 *       Wait until notification that the notification count matches a certain expected
 *       value
 *
 *  \par Assumptions, External Events, and Notes:
 *       None
 *
 *  \param[in] Notif Pointer to new notification variable
 *  \param[in] ValueExpected Expected value of notification count
 *  \param[in] TimeoutMs How long to wait before timing out (in milliseconds)
 *
 *  \return Execution status, see \ref OSReturnCodes
 *  \retval #OS_SUCCESS \copybrief OS_SUCCESS
 */
int32 BPNode_NotifWaitExact(BPNode_Notif_t* Notif, uint32 ValueExpected, int32 TimeoutMs);

#endif /* BPNODE_NOTIF_H */
