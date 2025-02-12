from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
from launch.substitutions import LaunchConfiguration, Command
from launch.conditions import IfCondition, UnlessCondition
import os

def generate_launch_description():
    # Get package paths
    gazebo_ros_pkg = get_package_share_directory('gazebo_ros')
    two_robot_sim_pkg = get_package_share_directory('two_robot_sim')

    # Path configurations
    world_file = os.path.join(two_robot_sim_pkg, 'worlds', 'empty_world.world')
    rviz_path = os.path.join(two_robot_sim_pkg, 'config', 'two_robots.rviz')
    robot1_urdf = os.path.join(two_robot_sim_pkg, 'urdf', 'robot1.urdf')
    robot2_urdf = os.path.join(two_robot_sim_pkg, 'urdf', 'robot2.urdf')

    with open(robot1_urdf, 'r') as f:
        robot1_description = f.read()

    with open(robot2_urdf, 'r') as f:
        robot2_description = f.read()

    return LaunchDescription([

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(gazebo_ros_pkg, 'launch', 'gazebo.launch.py')
            ),
            launch_arguments={
                'world': world_file,
                'extra_gazebo_args': '--verbose'
            }.items()
        ),

        # Robot 1
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            namespace='robot1',
            parameters=[{
                'robot_description': robot1_description,
                'use_sim_time': True,
                'frame_prefix': 'robot1/',  # Important for TF tree
                'publish_frequency': 100.0  # Increase publish frequency
            }],
            # remappings=[
            #     ('/tf', 'robot1/tf'),
            #     ('/tf_static', 'robot1/tf_static'),
            #     ('/joint_states', 'robot1/joint_states')
            # ],
            output='screen'
        ),

        Node(
            package='gazebo_ros',
            executable='spawn_entity.py',
            arguments=[
                '-entity', 'robot1',
                '-topic', 'robot1/robot_description',  # Use topic instead of file
                '-x', '0.0', '-y', '0.5', '-z', '0.1',
                '-robot_namespace', 'robot1'
            ],
            output='screen'
        ),

        #Robot 2
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            namespace='robot2',
            parameters=[{
                'robot_description': robot2_description,
                'use_sim_time': True,
                'frame_prefix': 'robot2/', # Important for TF tree
                'publish_frequency': 100.0  # Increase publish frequency
            }],
            # remappings=[
            #     ('/tf', 'robot2/tf'),
            #     ('/tf_static', 'robot2/tf_static'),
            #     ('/joint_states', 'robot2/joint_states')
            # ],
            output='screen'
        ),

        Node(
            package='gazebo_ros',
            executable='spawn_entity.py',
            arguments=[
                '-entity', 'robot2',
                '-topic', 'robot2/robot_description',  # Use topic instead of file
                '-x', '0.0', '-y', '-0.5', '-z', '0.1',
                '-robot_namespace', 'robot2'
            ],
            output='screen'
        ),

        # Node(
        #     package='tf2_ros',
        #     executable='static_transform_publisher',
        #     arguments=['0', '0', '0', '0', '0', '0', 'robot1/odom', 'robot1/base_link'],
        #     output='screen'
        # ),
        # Node(
        #     package='tf2_ros',
        #     executable='static_transform_publisher',
        #     arguments=['0', '0', '0', '0', '0', '0', 'robot2/odom', 'robot2/base_link'],
        #     output='screen'
        # ),

        # Optional RViz (uncomment if needed)
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', rviz_path],
            output='screen'
        ),

        # # For Robot 1
        # Node(
        #     package='joint_state_publisher',
        #     executable='joint_state_publisher',
        #     namespace='robot1',
        #     parameters=[
        #         {'use_sim_time': True},
        #         {'source_list': ['joint_states']}
        #     ],
        #     output='screen'
        # ),
        #
        # # Joint State Publisher for Robot 1
        Node(
            package='joint_state_publisher',
            executable='joint_state_publisher',
            namespace='robot1',
            parameters=[
                {'use_sim_time': True},
                {'source_list': ['/robot1/joint_states']}  # Fixed source_list
            ],
            remappings=[
                ('/joint_states', '/robot1/joint_states')
            ],
            
            output='screen',
            # condition=UnlessCondition(LaunchConfiguration('gui'))
        ),

        # # Joint State Publisher for Robot 2
        Node(
            package='joint_state_publisher',
            executable='joint_state_publisher',
            namespace='robot2',
            parameters=[
                {'use_sim_time': True},
                {'source_list': ['/robot2/joint_states']}  # Fixed source_list
            ],
            remappings=[
                ('/joint_states', '/robot2/joint_states')
            ],
            output='screen',
            # condition=UnlessCondition(LaunchConfiguration('gui'))
        ),

        # # Joint State Publisher GUI for Robot 1
        # Node(
        #     package='joint_state_publisher_gui',
        #     executable='joint_state_publisher_gui',
        #     namespace='robot2',
        #     parameters=[{'use_sim_time': True}],
        #     output='screen',
        #     condition=IfCondition(LaunchConfiguration('gui'))
        # ),

        # # Joint State Publisher GUI for Robot 2
        # Node(
        #     package='joint_state_publisher_gui',
        #     executable='joint_state_publisher_gui',
        #     namespace='robot2',
        #     parameters=[{'use_sim_time': True}],
        #     output='screen',
        #     condition=IfCondition(LaunchConfiguration('gui'))
        # ),
    ])