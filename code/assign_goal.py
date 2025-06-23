from nav2_msgs.action import NavigateToPose
import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from rclpy.task import Future
import time
import socket

class SendCoordinate:
    def __init__(self):
        self.TARGET_IP = "TARGET_IP"
        self.TARGET_PORT = 5005
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    def send(self, message):
        self.sock.sendto(message.encode('utf-8'), (self.TARGET_IP, self.TARGET_PORT))

class NavigateClient(Node):
    def __init__(self):
        super().__init__('navigate_client')
        # Initialize action client for NavigateToPose
        self.client = ActionClient(self, NavigateToPose, 'navigate_to_pose')
        
        # Define waypoints (x, y, yaw)
        self.waypoints = [
            (-1.35, 0.28, 0.99),  # Waypoint 1
            (3.375, 0.28, 0.99),  # Waypoint 2
            (3.34, -1.43, 0.01),  # Waypoint 3
            (-1.57, -1.43, 0.01), # Waypoint 4
            (3.34, -1.43, 0.99),  # Waypoint 5
            (3.83, -3.02, 0.01),  # Waypoint 6
            (-1.44, -3.02, 0.01), # Waypoint 7
            (3.83, -3.02, 0.99),  # Waypoint 8
            (3.375, 0.28, 0.01),  # Waypoint 9
            (-1.35, 0.28, 0.01)   # Waypoint 10
        ]
        self.current_waypoint_index = 0

        # Default timeout
        self.goal_timeout = 10.0
        self.goal_sent_time = None
        self.current_goal_handle = None

        # Goal status flags
        self.goal_in_progress = False
        self.goal_timeout_triggered = False
        
        # Check goal timeout every second
        self.create_timer(1.0, self.goal_timeout_check_callback)

    def send_goal(self, x, y, yaw):
        # Set timeout based on waypoint index
        if self.current_waypoint_index in [1, 3, 4, 7]:
            self.goal_timeout = 17.0
        else:
            self.goal_timeout = 12.0
        
        while not self.client.wait_for_server(timeout_sec=5.0):
            self.get_logger().info('Waiting for navigation server...')
        
        goal_msg = NavigateToPose.Goal()
        goal_msg.pose.header.frame_id = "map"
        goal_msg.pose.header.stamp = self.get_clock().now().to_msg()
        goal_msg.pose.pose.position.x = x
        goal_msg.pose.pose.position.y = y
        goal_msg.pose.pose.orientation.w = yaw

        self.get_logger().info(f'Navigating to waypoint {self.current_waypoint_index+1}: x={x}, y={y} (timeout {self.goal_timeout}s)')
        self.goal_sent_time = self.get_clock().now().nanoseconds / 1e9
        self.goal_in_progress = True
        self.goal_timeout_triggered = False
        
        send_goal_future = self.client.send_goal_async(goal_msg)
        send_goal_future.add_done_callback(self.goal_response_callback)
    
    def goal_response_callback(self, future: Future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().info('Goal rejected!')
            self.goal_in_progress = False
            return
        self.get_logger().info('Goal accepted, navigating...')
        self.current_goal_handle = goal_handle
        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self.goal_result_callback)

    def goal_result_callback(self, future: Future):
        if self.goal_timeout_triggered:
            self.get_logger().info(f'Waypoint {self.current_waypoint_index + 1} timed out!')
        else:
            self.get_logger().info(f'Waypoint {self.current_waypoint_index + 1} completed!')
        self.goal_in_progress = False
        self.current_goal_handle = None
        self.goal_sent_time = None

        # Send current waypoint info to laptop
        global send_coord
        if send_coord is not None:
            x, y, yaw = self.waypoints[self.current_waypoint_index]
            send_coord.send(f"{x}, {y}, {yaw}")

        # Move to next waypoint
        self.current_waypoint_index += 1
        if self.current_waypoint_index >= len(self.waypoints):
            self.get_logger().info('All waypoints completed, repeating route...')
            self.current_waypoint_index = 0

        x, y, yaw = self.waypoints[self.current_waypoint_index]
        time.sleep(2)
        self.send_goal(x, y, yaw)

    def goal_timeout_check_callback(self):
        if self.goal_in_progress and self.goal_sent_time is not None and not self.goal_timeout_triggered:
            current_time = self.get_clock().now().nanoseconds / 1e9
            elapsed = current_time - self.goal_sent_time
            if elapsed > self.goal_timeout:
                self.get_logger().info(f'Waypoint {self.current_waypoint_index + 1} timed out (elapsed: {elapsed:.2f}s), canceling goal')
                if self.current_goal_handle is not None:
                    self.current_goal_handle.cancel_goal_async()
                self.goal_timeout_triggered = True

def main(args=None):
    rclpy.init(args=args)
    node = NavigateClient()
    global send_coord
    send_coord = SendCoordinate()
    
    # Send first goal
    x, y, yaw = node.waypoints[0]
    node.send_goal(x, y, yaw)
    
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
