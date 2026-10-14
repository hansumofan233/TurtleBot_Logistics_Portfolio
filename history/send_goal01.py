#!/usr/bin/env python3

import rospy
from geometry_msgs.msg import PoseStamped
from std_msgs.msg import String
import math  # 导入数学库

# 定义目标点序列
waypoints = [
    (0.6, 0.2, 0),  # 第一个目标点
    (1.2, 0.5, 1.57),  # 第二个目标点
]

# 用于跟踪状态
waiting_for_uarm1 = True  # 标记是否在等待 uarm1 的指令
waiting_for_uarm3 = False  # 标记是否在等待 uarm3 的指令

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

def notify_camera():
    """
    向摄像头发送信号，通知小车已到达目标点
    """
    camera_pub = rospy.Publisher('/camera_signal', String, queue_size=10)
    rospy.sleep(1)  # 等待发布器初始化
    camera_pub.publish("capture")
    rospy.loginfo("Signal sent to camera: capture")


def uarm1_callback(msg):
    command = msg.data.strip().lower()
    # 根据接收到的指令执行逻辑

    global waiting_for_uarm1, waiting_for_uarm3

    if waiting_for_uarm1 and msg.data.strip().lower() == "start":
        rospy.loginfo("Received 'start' command from uarm1. Navigating to the first goal.")
        # 导航到第一个目标点
        x, y, yaw = waypoints[0]  # 获取第一个目标点
        send_goal(x, y, yaw)
        rospy.sleep(5)  # 等待机器人到达目标点

        # 通知摄像头
        notify_camera()

        # 更新状态：进入待命状态，等待 uarm3 的指令
        rospy.loginfo("Waiting for the next command from uarm3.")
        waiting_for_uarm1 = False
        waiting_for_uarm3 = True
    else:
        rospy.logwarn("Invalid or unexpected command from uarm1.")


def uarm3_callback(msg):
    """
    接收来自 uarm3 的指令并触发导航到第二个目标点
    :param msg: 接收到的指令消息
    """
    global waiting_for_uarm3

    if waiting_for_uarm3 and msg.data.strip().lower() == "proceed":
        rospy.loginfo("Received 'proceed' command from uarm3. Navigating to the second goal.")
        # 导航到第二个目标点
        x, y, yaw = waypoints[1]  # 获取第二个目标点
        send_goal(x, y, yaw)
        waiting_for_uarm3 = False  # 重置状态
        rospy.loginfo("Navigation to the second goal completed.")
    else:
        rospy.logwarn("Invalid or unexpected command from uarm3.")


if __name__ == "__main__":
    rospy.init_node('turtlebot_navigation_waiting')

    # 订阅来自 uarm1 的启动指令
    rospy.Subscriber('/turtlebot_start', String, uarm1_callback)

    # 订阅来自 uarm3 的继续指令
    rospy.Subscriber('/uarm3_command', String, uarm3_callback)

    rospy.loginfo("TurtleBot is ready to receive commands from uarm1 and uarm3.")

    rospy.spin()  # 保持节点运行
