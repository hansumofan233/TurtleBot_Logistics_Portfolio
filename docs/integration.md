# Integration Checklist (not yet validated)

## Node I/O
| Direction | ROS topic | Type | Purpose |
|---|---|---|---|
| Publish | `/TURTLEBOT1/move_base_simple/goal` | `geometry_msgs/PoseStamped` | target pose |
| Subscribe | `/TURTLEBOT1/move_base/result` | `move_base_msgs/MoveBaseActionResult` | goal result |
| Subscribe | `/turtlebot_start` | `std_msgs/Bool` | stage 1 trigger |
| Subscribe | `/turtlebot/notification` | `std_msgs/Bool` | stage 2 trigger |
| Publish | `/camera_signal` | `std_msgs/String` | camera trigger |
| Publish | `/TURTLEBOT1/nav_dock` | `std_msgs/Bool` | docking signal |
| Publish | `/cmd_vel` | `geometry_msgs/Twist` | timed velocity |

## Still to verify against `automation_system.launch`
- Is navigation launched under `/TURTLEBOT1` or remapped? Is `/cmd_vel` routed to the correct robot?
- Do the upstream uArm topics publish `Bool` and only once per stage?
- Is the map frame `map` and does the installed `move_base` expose these topic names?
- Does the original system already provide the navigation node start command?

## Historical development
The `history/` scripts are preliminary versions; they differ in waiting strategy, goal list and message contracts. They are retained to document iteration, **not** intended to be launched simultaneously.
