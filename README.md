# semubot_description

## **Overview**
Description package for SemuBot. Includes the URDF/xacro model with a RealSense D435i depth camera, omni-ball drive, arms, and Gazebo simulation support.

## **Table of Contents**
- [Installation](#installation)
- [Dependencies](#dependencies)
- [Building the Package](#building-the-package)
- [Launch Files](#launch-files)
- [Gazebo Simulation](#gazebo-simulation)
- [RealSense D435i Camera](#realsense-d435i-camera)
- [License](#license)

---

## **Installation**

### **1. Clone the Repository**
```bash
cd ~/<YOUR_WORKSPACE_NAME_HERE>/src
git clone https://github.com/SemuBot/semubot_description.git
```

## **Dependencies**
### **1. List of dependencies**
1.1. rviz2<br>
1.2. urdf<br>
1.3. xacro<br>
1.4. realsense2_description — only required when using `camera:=true`<br>
1.5. gz-sim (Gazebo Harmonic or newer) — only required for simulation

### **2. Install ROS dependencies**
```bash
cd ~/<YOUR_WORKSPACE_NAME_HERE>
rosdep install --from-paths src --ignore-src -r -y
```

### **3. Install realsense2_description (optional)**
Only needed if using the camera:
```bash
sudo apt install ros-$ROS_DISTRO-realsense2-description
```

## **Building the package**
```bash
cd ~/<YOUR_WORKSPACE_NAME_HERE>
colcon build --packages-select semubot_description
```

## **Launch files**
### **1. Source workspace**
```bash
source ~/<YOUR_WORKSPACE_NAME_HERE>/install/setup.bash
```
### **2. Available launch files**
#### 2.1. Display robot in RViz
Displays the robot model in RViz, starts `joint_state_publisher` and `robot_state_publisher`.
```bash
ros2 launch semubot_description display_robot.launch.py
```

## **Gazebo Simulation**
The URDF supports Gazebo via the `sim:=true` xacro argument, which loads:
- Joint state publisher plugin
- Odometry publisher plugin (publishes on `/odom` and TF)
- Velocity control plugin (subscribes to `/cmd_vel`)
- RGBD camera sensor 

To spawn SemuBot in Gazebo, pass `sim:=true` when processing the xacro.

## **RealSense D435i Camera**
The RealSense D435i is optional and disabled by default. Enable it with `camera:=true`. In simulation it is modelled as an RGBD sensor on the `/camera` topic.

## **License**
This project is licensed under the Apache 2.0 license - see the [LICENSE](LICENSE) file for more information.
