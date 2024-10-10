import rcl.py 
from rclpy.node import Node 
from std_msgs.msg import String 

class rover_control_node(Node):
    def __init__(self) : 
        super().__init__('rover_control_node') 
        self.control_signal_publisher=self.create_publisher(String,'control_sginal',10)
        self.shape_data_publisher=self.create_publisher(String,'detected_shapes',10)

        self.timer=self.create_timer(1.0,self.publish_data)

        self.control_signal = "Initial Conrol Signal"
        self.detected_shapes="No shapes detected "
    def publish_data(self) : 
        msg=String()
        msg.data=self.control_signal 
        self.control_signal_publisher.publish(msg)
        self.get_logger().info(f'Published Control Signal : {msg.data}')

        msg.data=self.detected_shapes 
        self.shape_data_publisher.publish(msg)
        self.get_logger().info(f'Published Detected Shapes : {msg.data}')

def main(args=None) : 
    rclpy.init(args=args) 
    RovCntrl=rover_control_node()
    rclpy.spin(rover_control_node)
    rover_control_node.destroy_node()
    rclpy.shutdown()

if __name__=='__main__' : 
    main()
