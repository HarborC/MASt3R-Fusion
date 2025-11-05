#!/usr/bin/env python

import rosbag
import os
import cv2
from cv_bridge import CvBridge
import numpy as np
import math

# 定义输出文件夹
output_dir = "/home/gpcv/Data4/Datasets/temp/wbl/output1"
imu_file = os.path.join(output_dir, "imu_data.txt")
camera1_dir = os.path.join(output_dir, "usb_cam")
camera2_dir = os.path.join(output_dir, "thermal_camera")

# 创建输出文件夹
os.makedirs(output_dir, exist_ok=True)
os.makedirs(camera1_dir, exist_ok=True)
os.makedirs(camera2_dir, exist_ok=True)

# 初始化CvBridge
bridge = CvBridge()

# 打开ROS bag文件
bag = rosbag.Bag('/home/gpcv/Data4/Datasets/temp/wbl/output1/data.bag')

G = 9.81

def generate_timestamp_file(image_dir, output_file, extensions=('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
    """
    生成 timestamp 文件，格式为：
    #timestamp [ns],filename

    其中 timestamp 是文件名（不含扩展名），
    filename 是不带父目录的纯文件名。
    """
    with open(output_file, 'w') as f:
        for filename in sorted(os.listdir(image_dir)):
            if filename.lower().endswith(extensions):
                name_without_ext = os.path.splitext(filename)[0]
                f.write(f"{name_without_ext} {filename}\n")

# 打开IMU文件
with open(imu_file, 'w') as imu_f:
    # 遍历bag文件中的消息
    for topic, msg, t in bag.read_messages():
        if topic == "/livox/imu":  # 替换为你的IMU话题名称
            # 写入IMU数据
            imu_f.write(f"{msg.header.stamp.to_sec()} {msg.angular_velocity.x* 180/math.pi} {msg.angular_velocity.y* 180/math.pi} {msg.angular_velocity.z* 180/math.pi} "
                        f"{msg.linear_acceleration.x} {msg.linear_acceleration.y} {msg.linear_acceleration.z}\n")

        # elif topic == "/camera/color/image_raw/compressed":  # 替换为你的第一个相机话题名称
        #     if msg._type == "sensor_msgs/CompressedImage":
        #         # 将压缩图像数据转换为 OpenCV 图像
        #         cv_image = bridge.compressed_imgmsg_to_cv2(msg, desired_encoding="passthrough")
        #         # 保存图像，文件名使用时间戳
        #         image_filename = os.path.join(camera1_dir, f"{msg.header.stamp.to_sec()}.png")
        #         cv2.imwrite(image_filename, cv_image)

        # elif topic == "/iray/thermal_img":  # 替换为你的第二个相机话题名称
        #     # 转换图像消息为OpenCV格式
        #     cv_image = bridge.imgmsg_to_cv2(msg, desired_encoding="passthrough")
        #     # 判断图像是否是黑图(95%的像素值为0)
        #     if np.count_nonzero(cv_image) < 0.05 * cv_image.size:
        #         continue
        #     # 保存图像，文件名使用时间戳
        #     image_filename = os.path.join(camera2_dir, f"{msg.header.stamp.to_sec()}.png")
        #     cv2.imwrite(image_filename, cv_image)

generate_timestamp_file(camera2_dir, os.path.join(output_dir, "thermal_camera_timestamp.txt"))
generate_timestamp_file(camera2_dir, os.path.join(output_dir, "usb_camera_timestamp.txt"))

# 关闭bag文件
bag.close()

print("数据解析完成！")