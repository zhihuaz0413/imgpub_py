import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import os
from ament_index_python.packages import get_package_share_directory


class ImagePublisher(Node):
    def __init__(self):
        super().__init__('image_publisher')
        self.publisher_ = self.create_publisher(Image, 'image_topic', 10)
        self.bridge = CvBridge()

        # Get the relative path to the images folder within this package
        package_name = 'imgpub_py'
        package_share_directory = get_package_share_directory(package_name)
        self.image_folder = os.path.join(package_share_directory, 'data/shadow')  # Replace 'data/images' with your folder structure

        self.image_list = sorted(os.listdir(self.image_folder))
        self.current_index = 0
        self.timer = self.create_timer(1.0, self.publish_image)  # Publish an image every second
        self.get_logger().info(f'Image Publisher Node started, reading from {self.image_folder}')

    def publish_image(self):
        if self.current_index < len(self.image_list):
            image_path = os.path.join(self.image_folder, self.image_list[self.current_index])
            if not image_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                self.get_logger().warn(f"Skipping non-image file: {image_path}")
                self.current_index += 1
                return

            self.get_logger().info(f'Publishing image: {self.image_list[self.current_index]}')
            cv_image = cv2.imread(image_path)
            if cv_image is None:
                self.get_logger().error(f"Failed to read image: {image_path}")
                self.current_index += 1
                return

            ros_image = self.bridge.cv2_to_imgmsg(cv_image, encoding='bgr8')
            self.publisher_.publish(ros_image)
            self.current_index += 1
        else:
            self.get_logger().info('No more images to publish. Shutting down...')
            self.timer.cancel()
            rclpy.shutdown()


def main(args=None):
    rclpy.init(args=args)
    node = ImagePublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Node interrupted by user')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
