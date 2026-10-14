#!/usr/bin/env python3

import rospy
from geometry_msgs.msg import PoseStamped, Twist
from move_base_msgs.msg import MoveBaseActionResult
from std_msgs.msg import String, Bool
import math

# 定义目标点序列
waypoints = [
    (1.12, 0.75, -1.57),   # 第一个目标点
    (0.55, 0.45, 0.1),     # 第二个目标点
    (1.3, 0.45, 0),        # 第三个目标点
    (1.3, 0.55, 1.57),     # 第四个目标点
    (1.1, 0.8, 3.2),       # 第五个目标点
]

goal_reached = False  # 全局变量，用于记录目标点到达状态

def result_callback(msg):
    """
    处理 /move_base/result 消息，更新目标点到达状态
    """
    global goal_reached
    if msg.status.status == 3:  # 3 表示目标点到达
        rospy.loginfo("Goal reached successfully.")
        goal_reached = True
    else:
        rospy.logwarn(f"Goal failed with status: {msg.status.status}")
        goal_reached = False

def send_goal(x, y, yaw):
    """
    发布目标点
    """
    pub = rospy.Publisher('/TURTLEBOT1/move_base_simple/goal', PoseStamped, queue_size=10)
    rospy.sleep(1)  # 等待发布器初始化

    goal = PoseStamped()
    goal.header.frame_id = "map"
    goal.header.stamp = rospy.Time.now()

    # 设置目标点位置
    goal.pose.position.x = x
    goal.pose.position.y = y

    # 设置目标点方向（四元数）
    goal.pose.orientation.z = math.sin(yaw / 2.0)
    goal.pose.orientation.w = math.cos(yaw / 2.0)

    pub.publish(goal)
    rospy.loginfo(f"Goal sent: x={x}, y={y}, yaw={yaw}")

def wait_for_goal_reach(timeout=10):
    """
    等待目标点到达或超时
    """
    global goal_reached
    goal_reached = False  # 重置状态
    start_time = rospy.Time.now()
    while not rospy.is_shutdown():
        if goal_reached:
            rospy.loginfo("Goal confirmed as reached.")
            break
        if (rospy.Time.now() - start_time).to_sec() > timeout:
            rospy.logwarn("Timeout waiting for goal to be reached.")
            break
        rospy.sleep(0.5)

def move_forward(distance, speed=0.2):
    """
    让小车向前移动指定距离
    :param distance: 移动的距离（米）
    :param speed: 向前移动的速度（默认 0.2 m/s）
    """
    velocity_pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
    rospy.sleep(1)  # 等待发布器初始化

    move_cmd = Twist()
    move_cmd.linear.x = speed  # 设置线速度

    start_time = rospy.Time.now()
    duration = distance / speed

    rospy.loginfo(f"Moving forward: distance={distance}, speed={speed}")

    while rospy.Time.now() - start_time < rospy.Duration(duration):
        rospy.loginfo(f"Publishing linear velocity: {move_cmd.linear.x}")
        velocity_pub.publish(move_cmd)
        rospy.sleep(0.1)

    # 停止移动
    move_cmd.linear.x = 0
    velocity_pub.publish(move_cmd)
    rospy.loginfo("Stopped moving forward.")

def notify_camera():
    """
    向摄像头发送信号
    """
    camera_pub = rospy.Publisher('/camera_signal', String, queue_size=10)
    rospy.sleep(1)  # 等待发布器初始化
    camera_pub.publish("capture")
    rospy.loginfo("Signal sent to camera: capture")

def notify_docking_station():
    """
    向对接站发送信号
    """
    docking_pub = rospy.Publisher('/TURTLEBOT1/nav_dock', Bool, queue_size=10)
    rospy.sleep(1)  # 等待发布器初始化
    docking_pub.publish(True)
    rospy.loginfo("Signal sent to docking station: dock")

def uarm1_callback(msg):
    """
    处理 uarm1 指令
    """
    if msg.data == 1:  
        rospy.loginfo("Processing command from uarm1.")
        for i in range(2):  # 遍历第一个和第二个目标点
             x, y, yaw = waypoints[i]
             send_goal(x, y, yaw)
             wait_for_goal_reach()  # 等待目标点到达
             if i == 1:  # 在第二个目标点发送摄像头信号
                notify_camera()
    else:
        rospy.logwarn("uarm1 command received as False. No action taken.")

def uarm2_callback(msg):
    """
    处理 uarm2 指令
    """
    if msg.data == 1: 
        rospy.logwarn("uarm2 command is already active. Ignoring new command.")

        # 遍历第3到第5个目标点
        for i in range(2, 5):
                x, y, yaw = waypoints[i]
                send_goal(x, y, yaw)
                if i == 5:  # 在第二个目标点发送摄像头信号
                    wait_for_goal_reach()  # 等待目标点到达
        rospy.sleep(3)

        # 按指定速度和距离向前移动
        move_forward(0.5, 0.2)

        # 移动到对接站
        notify_docking_station()
    else:
        rospy.logwarn("uarm2 command received as False. No action taken.")

if __name__ == "__main__":
    rospy.init_node('turtlebot_navigation_waiting')

    # 订阅目标点到达结果
    rospy.Subscriber('/move_base/result', MoveBaseActionResult, result_callback)

    # 订阅 uarm1 指令
    rospy.Subscriber('/turtlebot_start', Bool, uarm1_callback)

    # 订阅 uarm2 指令
    rospy.Subscriber('/turtlebot/notification', Bool, uarm2_callback)

    rospy.loginfo("TurtleBot is ready to receive commands from uarm1 and uarm2.")

    rospy.spin()
