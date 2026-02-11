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

/**
 * @file
 *
 * BPNode Application Mission Configuration Header File
 *
 * This is a compatibility header for the "mission_cfg.h" file that has
 * traditionally provided public config definitions for each cFS app.
 *
 * @note This file may be overridden/superceded by mission-provided definitions
 * either by overriding this header or by generating definitions from a command/data
 * dictionary tool.
 */

#ifndef BPNODE_MISSION_CFG_H
#define BPNODE_MISSION_CFG_H

#include "bpnode_interface_cfg.h"

// #define CAPSTONE_BUILD

/**
 * \brief Determines whether the UDP CLAs are built. Building without the UDP CLA,
 *        in the current form of the code, will cause an error and the software
 *        will crash
 */
#define DEFAULT_UDP_CLA

/**
 * \brief IODriver udpsock_intf driver name
 */
#define BPNODE_CLA_PSP_DRIVER_NAME "udpsock_intf"

/**
 * \brief Default EID Service Number to egress bundles over channel 0
 */
#define BPNODE_EID_SERVICE_NUM_FOR_CHANNEL_0 42

/**
 * \brief Default EID Service Number to egress bundles over channel 1
 */
#define BPNODE_EID_SERVICE_NUM_FOR_CHANNEL_1 53

/**
 * \brief Default EID Node Number to egress bundles to contact 0
 */
#define BPNODE_EID_NODE_NUM_FOR_CONTACT_0 200

/**
 * \brief Default EID Service Number to egress bundles to contact 0
 */
#define BPNODE_EID_SERVICE_NUM_FOR_CONTACT_0 64

/**
 * \brief Default EID Node Number to egress bundles to contact 1
 */
#define BPNODE_EID_NODE_NUM_FOR_CONTACT_1 400

/**
 * \brief Default EID Service Number to egress bundles to contact 1
 */
#define BPNODE_EID_SERVICE_NUM_FOR_CONTACT_1 42

/**
 * \brief Default EID Node Number to egress bundles to contact 2
 */
#define BPNODE_EID_NODE_NUM_FOR_CONTACT_2 600

/**
 * \brief Default EID Service Number to egress bundles to contact 2
 */
#define BPNODE_EID_SERVICE_NUM_FOR_CONTACT_2 12

#endif /* BPNODE_MISSION_CFG_H */
