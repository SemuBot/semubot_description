from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import Command
from ament_index_python.packages import get_package_share_path
import os

def generate_launch_description():
    pkg = get_package_share_path("semubot_description")
    
    urdf_path = os.path.join(
        pkg,
        'urdf',
        'semubot.urdf.xacro')
    
    rviz_path = os.path.join(
        pkg,
        'config',
        'semubot_description.rviz')

    robot_description_content = Command(['xacro ', urdf_path])

    # Robot State Publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[
            {'robot_description': robot_description_content}
        ]
    )

    # Joint State Publisher
    joint_state_publisher = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        output='screen',
        parameters=[
            {'robot_description': robot_description_content}
        ]
    )

    # RViz2
    rviz2 = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=[
            '-d', rviz_path
        ]
    )

    return LaunchDescription([
        robot_state_publisher,
        joint_state_publisher,
        rviz2
    ])