from launch import LaunchDescription
from launch.actions import AppendEnvironmentVariable, DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import (Command, LaunchConfiguration, PathJoinSubstitution,
                                  PythonExpression)
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from ament_index_python.packages import get_package_share_path
import os


def generate_launch_description():
    pkg = get_package_share_path('semubot_description')
    version = LaunchConfiguration('version')
    name = PythonExpression(["'semubot' if '", version, "' == 'v1' else 'semubot_v2'"])

    urdf_path = PathJoinSubstitution([
        str(pkg), 'urdf', PythonExpression(["'", name, ".urdf.xacro'"])])
    robot_description = ParameterValue(
        Command(['xacro ', urdf_path, ' sim:=true']), value_type=str)

    gazebo = IncludeLaunchDescription(
        PathJoinSubstitution([str(get_package_share_path('ros_gz_sim')), 'launch', 'gz_sim.launch.py']),
        launch_arguments={'gz_args': '-r empty.sdf'}.items())

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_description, 'use_sim_time': True}])

    spawn = Node(
        package='ros_gz_sim',
        executable='create',
        output='screen',
        arguments=['-topic', 'robot_description', '-name', name, '-z', '0.01'])

    # /cmd_vel in, /odom + TF + joint states + clock out
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        output='screen',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
            ['/model/', name, '/odometry@nav_msgs/msg/Odometry[gz.msgs.Odometry'],
            ['/model/', name, '/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V'],
            ['/world/empty/model/', name, '/joint_state@sensor_msgs/msg/JointState[gz.msgs.Model'],
        ],
        remappings=[
            (['/model/', name, '/odometry'], '/odom'),
            (['/model/', name, '/tf'], '/tf'),
            (['/world/empty/model/', name, '/joint_state'], '/joint_states'),
        ])

    return LaunchDescription([
        DeclareLaunchArgument('version', default_value='v1', choices=['v1', 'v2'],
                              description='Robot version to simulate'),
        # Lets Gazebo resolve package://semubot_description/... mesh paths
        AppendEnvironmentVariable('GZ_SIM_RESOURCE_PATH', os.path.dirname(pkg)),
        gazebo,
        robot_state_publisher,
        spawn,
        bridge,
    ])
