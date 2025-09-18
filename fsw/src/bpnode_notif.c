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
#include "bpnode_notif.h"
#include "osapi.h"

/* Initialize notification */
int32 BPNode_NotifInit(BPNode_Notif_t* Notif, const char* NotifName)
{
    Notif->Count = 0;
    return OS_CondVarCreate(&Notif->CondVar, NotifName, 0);
}

/* Destroy notification */
void BPNode_NotifDestroy(BPNode_Notif_t* Notif)
{
    OS_CondVarDelete(Notif->CondVar);
}

/* Get notification count */
uint32 BPNode_NotifGetCount(BPNode_Notif_t* Notif)
{
    uint32 Count;

    if (Notif == NULL)
    {
        return 0;
    }

    OS_CondVarLock(Notif->CondVar);
    Count = Notif->Count;
    OS_CondVarUnlock(Notif->CondVar);
    return Count;
}

/* Set notification by incrementing its count */
void BPNode_NotifSet(BPNode_Notif_t* Notif)
{
    if (Notif == NULL)
    {
        return;
    }

    OS_CondVarLock(Notif->CondVar);
    Notif->Count++;
    OS_CondVarBroadcast(Notif->CondVar);
    OS_CondVarUnlock(Notif->CondVar);
}

/* Set notification by decrementing its count */
void BPNode_NotifUnset(BPNode_Notif_t* Notif)
{
    if (Notif == NULL)
    {
        return;
    }

    OS_CondVarLock(Notif->CondVar);
    Notif->Count--;
    OS_CondVarBroadcast(Notif->CondVar);
    OS_CondVarUnlock(Notif->CondVar);
}

#ifdef CAPSTONE_BUILD
/*
 * @brief Gets an absolute time value relative to the current time
 *
 * This function adds the given interval, expressed in milliseconds, to the
 * current clock and returns the result.
 *
 * @note This is intended to ease transitioning from a relative timeout value to
 * and absolute timeout value.  The result can be passed to any function
 * that accepts an absolute timeout, to mimic the behavior of a relative timeout.
 *
 * @param[in]  relative_msec A relative time interval, in milliseconds
 *
 * @returns Absolute time value after adding interval
 */
OS_time_t OS_TimeFromRelativeMilliseconds(int32 relative_msec)
{
    OS_time_t abs_time;

    if (relative_msec == OS_CHECK)
    {
        abs_time = ((OS_time_t) {0});
    }
    else if (relative_msec > 0)
    {
        OS_GetLocalTime(&abs_time);
        abs_time = OS_TimeAdd(abs_time, OS_TimeFromTotalMilliseconds(relative_msec));
    }
    else
    {
        abs_time = ((OS_time_t) {INT64_MAX});
    }

    return abs_time;
}
#endif

/* Wait until notif is incremented */
int32 BPNode_NotifWait(BPNode_Notif_t* Notif, uint32 OldCount, int32 TimeoutMs)
{
    OS_time_t AbsWaitTime;
    int32 OsStatus = OS_SUCCESS;

    /* Perform wait on the Notif availability */
    AbsWaitTime = OS_TimeFromRelativeMilliseconds(TimeoutMs);
    OS_CondVarLock(Notif->CondVar);
    while (Notif->Count == OldCount)
    {
        OsStatus = OS_CondVarTimedWait(Notif->CondVar, &AbsWaitTime);
        if (OsStatus == OS_SUCCESS)
        {
            /* Note: No break here incase there's a spurious wakeup */
        }
        else if (OsStatus == OS_ERROR_TIMEOUT)
        {
            break;
        }
        else
        {
            /* Case is separate in case event message needed */
            break;
        }
    }
    OS_CondVarUnlock(Notif->CondVar);

    return OsStatus;
}

/* Wait until notif is exactly the value provided */
int32 BPNode_NotifWaitExact(BPNode_Notif_t* Notif, uint32 ValueExpected, int32 TimeoutMs)
{
    OS_time_t AbsWaitTime;
    int32 OsStatus = OS_SUCCESS;

    /* Perform wait on the Notif availability */
    AbsWaitTime = OS_TimeFromRelativeMilliseconds(TimeoutMs);
    OS_CondVarLock(Notif->CondVar);
    while (Notif->Count != ValueExpected)
    {
        OsStatus = OS_CondVarTimedWait(Notif->CondVar, &AbsWaitTime);
        if (OsStatus == OS_SUCCESS)
        {
            /* No break here since each child task should wake parent task up */
        }
        else if (OsStatus == OS_ERROR_TIMEOUT)
        {
            break;
        }
        else
        {
            /* Case is separate in case event message needed */
            break;
        }
    }
    OS_CondVarUnlock(Notif->CondVar);

    return OsStatus;
}
