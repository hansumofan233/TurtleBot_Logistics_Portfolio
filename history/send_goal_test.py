#!/usr/bin/env python3

import rospy
from geometry_msgs.msg import PoseStamped, Twist
from std_msgs.msg import String
import math  # 导入数学库

# 定义目标点序列
waypoints = [
    (1.12, 0.75, -1.57),   # 第一个目标点
    (0.55, 0.45, 0.1),    # 第二个目标点
    (1.3, 0.45, 0),
    (1.3, 0.55, 1.57),
    (1.1, 0.8, 3.3), 
]

def send_goal(x, y, yaw):
    """
    发布目标点
    :param x: 目标点 x 坐标（地图框架下）
    :param y: 目标点 y 坐标（地图框架下）
    :param yaw: 目标点的朝向（弧度）
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

def move_forward(duration, speed=0.2):
    """
    让小车向前移动指定时间
    :param duration: 向前移动的持续时间（秒）
    :param speed: 向前移动的速度（默认 0.2 m/s）
    """
    velocity_pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
    rospy.sleep(1)  # 等待发布器初始化

    move_cmd = Twist()
    move_cmd.linear.x = speed  # 设置线速度

    start_time = rospy.Time.now()
    rospy.loginfo("Moving forward...")

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
    向摄像头发送信号，通知小车已到达目标点
    """
    camera_pub = rospy.Publisher('/camera_signal', String, queue_size=10)
    rospy.sleep(1)  # 等待发布器初始化
    camera_pub.publish("capture")
    rospy.loginfo("Signal sent to camera: capture")


def move_to_first_two_goals():
    """
    导航到第一个和第二个目标点，并输出 'stop'
    """
    for i in range(2):  # 遍历第一个和第二个目标点
        x, y, yaw = waypoints[i]
        send_goal(x, y, yaw)
        rospy.sleep(5)  # 模拟等待机器人到达目标点

        # 通知摄像头
        notify_camera()

    # 输出 'stop'
    rospy.loginfo("stop")


def move_to_last_goal():
    """
    导航到最后一个目标点并输出 'finish'
    """
    for i in range(2, 5):  # 遍历第3个到最后一个目标点
        x, y, yaw = waypoints[i]
        send_goal(x, y, yaw)
        rospy.sleep(5)  # 模拟等待机器人到达目标点

    rospy.loginfo("wait back")
    # 等待 'back' 指令移动到最后一个目标点
    while not rospy.is_shutdown():
        if user_input.lower().strip() == "back":
             rospy.loginfo("Received 'back' command. Moving forward...")
             move_forward(0.5, 0.3)
             rospy.loginfo("finish")
        break
    else:
        rospy.logwarn("Invalid input. Please enter 'back'.")


if __name__ == "__main__":
    rospy.init_node('turtlebot_navigation_manual')

    rospy.loginfo("TurtleBot manual navigation ready. Input '1' to move to the first two goals, '3' to move to the last goal.")

    while not rospy.is_shutdown():
        user_input = input("Enter command (1: move to first two goals, 3: move to last goal): ").strip()
        if user_input == "1":
            rospy.loginfo("Command received: 1")
            move_to_first_two_goals()  # 移动到第一个和第二个目标点
        elif user_input == "3":
            rospy.loginfo("Command received: 3")
            move_to_last_goal()  # 移动到最后一个目标点
        else:
            rospy.logwarn("Invalid input. Please enter '1' or '3'.")