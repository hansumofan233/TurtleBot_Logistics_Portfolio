#!/usr/bin/env python3

import rospy
from geometry_msgs.msg import PoseStamped, Twist
from std_msgs.msg import String,Bool
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


def notify_docking_station():
    """
    向对接站发送信号
    """
    docking_pub = rospy.Publisher('/TURTLEBOT1/nav_dock', Bool, queue_size=10)
    rospy.sleep(1)  # 等待发布器初始化
    docking_pub.publish(True)
    rospy.loginfo("Signal sent to docking station: dock")

uarm1_active = False
uarm2_active = False

def uarm1_callback(msg):
    """
    接收 uarm1 指令，导航到第一个和第二个目标点
    """
    global uarm1_active
    if msg.data:  # 如果指令为 True
        if uarm1_active:
            rospy.logwarn("uarm1 command is already active. Ignoring new command.")
        else:
            uarm1_active = True
            rospy.loginfo("Processing command from uarm1.")
            for i in range(2):  # 遍历第一个和第二个目标点
                x, y, yaw = waypoints[i]
                send_goal(x, y, yaw)
                rospy.sleep(5)  # 模拟等待机器人到达目标点

            # 在第二个目标点通知摄像头
            notify_camera()

            uarm1_active = False  # 重置状态
            rospy.loginfo("uarm1 command processed and reset.")
    else:  # 如果指令为 False
        rospy.logwarn("uarm1 command received as False. No action taken.")

def uarm2_callback(msg):
    """
    接收 uarm2 指令，导航到第3到第5个目标点并移动到对接站
    """
    global uarm2_active
    if msg.data:  # 如果指令为 True
        if uarm2_active:
            rospy.logwarn("uarm2 command is already active. Ignoring new command.")
        else:
            uarm2_active = True
            rospy.loginfo("Processing command from uarm2.")

            # 导航到第3到第5个目标点
            for i in range(2, 5):
                x, y, yaw = waypoints[i]
                send_goal(x, y, yaw)
                rospy.sleep(5)  # 模拟等待机器人到达目标点

            # 停止 3 秒
            rospy.loginfo("Waiting for 3 seconds...")
            rospy.sleep(3)

            # 按指定速度和距离向前移动
            move_forward(0.5, 0.3)

            # 向对接站发送信号
            notify_docking_station()

            # 重置状态
            uarm2_active = False
            rospy.loginfo("uarm2 command processed and reset.")
    else:  # 如果指令为 False
        rospy.logwarn("uarm2 command received as False. No action taken.")


if __name__ == "__main__":
    rospy.init_node('turtlebot_navigation_waiting')

    # 订阅来自 uarm1 的启动指令
    rospy.Subscriber('/turtlebot_start', Bool, uarm1_callback)

    # 订阅来自 uarm2 的指令
    rospy.Subscriber('/turtlebot/notification', Bool, uarm2_callback)

    rospy.loginfo("TurtleBot is ready to receive commands from uarm1 and uarm2.")

    rospy.spin()  # 保持节点运行