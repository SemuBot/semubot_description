# semubot_description

## **Overview**
Description package for SemuBot.
## **Table of Contents**
- [Installation](#installation)
- [Dependencies](#dependencies)
- [Building the Package](#building-the-package)
- [Launch Files](#launch-files)
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
1.1. rviz<br>
1.2. urdf<br>
1.3. xacro
### **2. Install dependencies**
```bash
cd ~/<YOUR_WORKSPACE_NAME_HERE>
rosdep install --from-paths src --ignore-src -r -y
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
#### 2.1. Display simulated robot
Displays the robot's model in rviz, starts joint_state_publisher and robot_state_publisher
```bash
#### Load SemuBot model
ros2 launch semubot_description display_robot.launch.py
```

## **License**
This project is licensed under the Apache 2.0 license - see the [LICENSE](LICENSE) file for more information.
