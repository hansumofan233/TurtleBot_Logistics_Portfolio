#!/usr/bin/env python3
import rospy
from geometry_msgs.msg import PoseStamped, Twist
from move_base_msgs.msg import MoveBaseActionResult
from std_msgs.msg import String, Bool
import math

waypoints = [
    (1.12, 0.75, -1.57),
    (0.55, 0.45, 0.1),
    (1.2, 0.45, 0.1),
    (1.2, 0.5, 1.57),
    (1.1, 0.8, 3.3),
]
move_point_counter = 0

def result_callback(msg):
    global move_point_counter
    if msg.status.status == 3:
        rospy.loginfo("Goal reached successfully.")
        if move_point_counter == 1:
            notify_camera()
        elif move_point_counter == len(waypoints)-1:
            move_forward(0.2, 0.2)
            notify_docking_station()
            rospy.loginfo("All waypoints reached. Resetting for next oder.")
            move_point_counter = 0
        else:
            move_point_counter += 1
            x, y, yaw = waypoints[move_point_counter]
            send_goal(x, y, yaw)

def move_backward(distance, speed=0.2):
    velocity_pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
    rospy.sleep(1)
    move_cmd = Twist()
    move_cmd.linear.x = -speed
    start_time = rospy.Time.now()
    rospy.loginfo("Moving backward...")
    while rospy.Time.now() - start_time < rospy.Duration(distance / speed):
        velocity_pub.publish(move_cmd)
        rospy.sleep(0.1)
    move_cmd.linear.x = 0
    velocity_pub.publish(move_cmd)
    rospy.loginfo("Stopped moving backward.")

def send_goal(x, y, yaw):
    pub = rospy.Publisher('/TURTLEBOT1/move_base_simple/goal', PoseStamped, queue_size=10)
    rospy.sleep(1)
    goal = PoseStamped()
    goal.header.frame_id = "map"
    goal.header.stamp = rospy.Time.now()
    goal.pose.position.x = x
    goal.pose.position.y = y
    goal.pose.orientation.z = math.sin(yaw / 2.0)
    goal.pose.orientation.w = math.cos(yaw / 2.0)
    pub.publish(goal)
    rospy.loginfo(f"Goal sent: x={x}, y={y}, yaw={yaw}")

def move_forward(duration, speed=0.3):
    velocity_pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
    rospy.sleep(1)
    move_cmd = Twist()
    move_cmd.linear.x = speed
    start_time = rospy.Time.now()
    rospy.loginfo("Moving forward...")
    while rospy.Time.now() - start_time < rospy.Duration(duration):
        rospy.loginfo(f"Publishing linear velocity: {move_cmd.linear.x}")
        velocity_pub.publish(move_cmd)
        rospy.sleep(0.1)
    move_cmd.linear.x = 0
    velocity_pub.publish(move_cmd)
    rospy.loginfo("Stopped moving forward.")

def notify_camera():
    camera_pub = rospy.Publisher('/camera_signal', String, queue_size=10)
    rospy.sleep(1)
    camera_pub.publish("capture")
    rospy.loginfo("Signal sent to camera: capture")

def notify_docking_station():
    docking_pub = rospy.Publisher('/TURTLEBOT1/nav_dock', Bool, queue_size=10)
    rospy.sleep(1)
    docking_pub.publish(True)
    rospy.loginfo("Signal sent to docking station: dock")

def uarm1_callback(msg):
    global move_point_counter
    if msg.data == 1:
        rospy.loginfo("Processing command from uarm1.")
        move_backward(0.2, 0.2)
        rospy.loginfo("Turtlebot leaved docking station.")
        x, y, yaw = waypoints[move_point_counter]
        send_goal(x, y, yaw)
    else:
        rospy.logwarn("uarm1 command received as False. No action taken.")

def uarm2_callback(msg):
    if msg.data == 1:
        global move_point_counter
        move_point_counter += 1
        x, y, yaw = waypoints[move_point_counter]
        send_goal(x, y, yaw)
    else:
        rospy.logwarn("uarm2 command received as False. No action taken.")

if __name__ == "__main__":
    rospy.init_node('turtlebot_navigation_waiting')
    rospy.Subscriber('/TURTLEBOT1/move_base/result', MoveBaseActionResult, result_callback)
    rospy.Subscriber('/turtlebot_start', Bool, uarm1_callback)
    rospy.Subscriber('/turtlebot/notification', Bool, uarm2_callback)
    rospy.loginfo("TurtleBot is ready to receive commands from uarm1 and uarm2.")
    rospy.spin()
