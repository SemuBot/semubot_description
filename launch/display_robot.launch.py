from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution, PythonExpression
from ament_index_python.packages import get_package_share_path
import os

def generate_launch_description():
    pkg = get_package_share_path("semubot_description")
    
    version = DeclareLaunchArgument(
        'version', default_value='v1', choices=['v1', 'v2'],
        description='Robot version to display')

    urdf_path = PathJoinSubstitution([
        str(pkg),
        'urdf',
        PythonExpression(["'semubot.urdf.xacro' if '", LaunchConfiguration('version'),
                          "' == 'v1' else 'semubot_v2.urdf.xacro'"])])
    
    rviz_path = os.path.join(
        pkg,
        'config',
        'semubot_description.rviz')

    robot_description_content = ParameterValue(Command(['xacro ', urdf_path]), value_type=str)

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
        version,
        robot_state_publisher,
        joint_state_publisher,
        rviz2
    ])