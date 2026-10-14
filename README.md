# TurtleBot Logistics Navigation | ROS 1

**Personal navigation module developed during a group laboratory course at Karlsruhe Institute of Technology (KIT), WS 2024/25.**  
**Scope:** My code is the TurtleBot navigation-control node and experimental revisions in this repository. The surrounding logistics system, robot models, maps and launch infrastructure belonged to the group / course and are **not redistributed** here.

## Overview

The node coordinates a TurtleBot in a multi-station logistics workflow. A task trigger from an upstream uArm controller starts navigation, the ROS `move_base` status feedback advances the waypoint sequence, and the node signals image capture and docking steps.

**Stack:** ROS 1 (`rospy`), `geometry_msgs`, `std_msgs`, `move_base_msgs`; integrated with a course setup using Gazebo, Gmapping / AMCL and `move_base`.

## Architecture

```text
                 KIT Logistics Automation System
                            │
                  automation_system.launch
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
  Order Generator     Robot Stations      Box Detection
                            │                   │
                            ▼                   │
                    Navigation Node ◄───────────┘
                            │
                 ROS move_base interface
                            │
                            ▼
                    TurtleBot Navigation
                            │
                            ▼
                      Docking Node
```

## Files

- [`src/navigation_node.py`](src/navigation_node.py) — snapshot of the latest navigation node copied from the user's `dev/navigation` working tree (`f2f2093`). Kept faithful to that snapshot, including known limitations.
- [`history/`](history/) — four **independently written** standalone prototypes that preceded integration into the course ROS package.
- [`docs/integration.md`](docs/integration.md) — expected ROS topics and pending integration checks.

## What I implemented

- Publishes 2D waypoints (`PoseStamped`, map frame) with orientation converted to quaternion.
- Subscribes to `/TURTLEBOT1/move_base/result` and uses `SUCCEEDED` navigation feedback to progress through parts of the workflow, in place of fixed sleeps in earlier prototypes.
- Coordinates with uArm control signals, triggers a camera request and signals docking; publishes timed short-range velocity commands.
- Iterated the navigation node on Git branch `dev/navigation` (seven latest commits observed: `70f28c6` … `f2f2093`).

## Limitations / reproducibility

This is a **portfolio source-code extract**, not a standalone complete ROS application. `automation_system.launch`, the upstream message publishers, navigation stack, robot models, maps and hardware are **not included or verified**. No end-to-end reproduction or hardware safety claim is made.

The snapshot has edge cases that need attention before re-use: repeated `uArm` notifications could skip waypoint indices; arrival result messages are not matched to specific requested goals; lack of navigation failure / timeout handling; topic namespaces for velocity commands may require remapping. Do not run unchanged on physical robots.

## Reuse

To integrate, place the node in a properly configured ROS 1 Catkin package, inspect namespace remappings and message types, configure executable permissions, and launch it only after `move_base` and the course-specific components are available. See `docs/integration.md`.

## Attribution

Course group project: KIT Seamless Engineering (WS 2024/25), Group 03. **Only individually authored navigation-node and prototype scripts are shared here.** All course and teammates’ materials are excluded pending permission.
