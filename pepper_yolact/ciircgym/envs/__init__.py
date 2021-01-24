from gym.envs.registration import register
#from ciircgym.envs import kuka
#from ciircgym.envs import righthand
#from ciircgym.envs import ur5
#from ciircgym.envs import pepper_throw

# --- COMPOSITIONS MUJOCO ---

register(
    id="PepperFlipperSimple-v0",
    entry_point="circgym.envs.mujoco.simple_env:PepperFlipperSimpleEnv",
    max_episode_steps=500,
)

register(
    id="PepperMazeSimple-v0",
    entry_point="ciircgym.envs.mujoco.simple_env:PepperMazeSimpleEnv",
    max_episode_steps=500,
)

register(
    id="ReachyMinigolfSimple-v0",
    entry_point="ciircgym.envs.mujoco.simple_env:ReachyMinigolfSimpleEnv",
    max_episode_steps=500,
)

register(
    id="PepperSoccerSimple-v0",
    entry_point="ciircgym.envs.mujoco.simple_env:PepperSoccerSimpleEnv",
    max_episode_steps=500,
)

register(
    id="PepperThrowerSimple-v0",
    entry_point="ciircgym.envs.mujoco.simple_env:PepperThrowerSimpleEnv",
    max_episode_steps=500,
)

register(
    id="UR5MinigolfSimple-v0",
    entry_point="ciircgym.envs.mujoco.simple_env:UR5MinigolfSimpleEnv",
    max_episode_steps=500,
)



# --- PEPPER MUJOCO ENVS ---

register(
    id="PepperAllJointsSimple-v0",
    entry_point="ciircgym.envs.mujoco.simple_env:PepperAllJointsSimpleEnv",
    max_episode_steps=500,
)

register(
    id="PepperAllJointsFixedSimple-v0",
    entry_point="ciircgym.envs.mujoco.simple_env:PepperAllJointsFixedSimpleEnv",
    max_episode_steps=500,
)


register(
    id="PepperBothArmsFixedSimple-v0",
    entry_point="ciircgym.envs.mujoco.simple_env:PepperBothArmsFixedSimpleEnv",
    max_episode_steps=500,
)

register(
    id="PepperLeftArmSimple-v0",
    entry_point="ciircgym.envs.mujoco.simple_env:PepperLeftArmSimpleEnv",
    max_episode_steps=500,
)

register(
    id="PepperLeftArmFixedSimple-v0",
    entry_point="ciircgym.envs.mujoco.simple_env:PepperLeftArmFixedSimpleEnv",
    max_episode_steps=500,
)

register(
    id="PepperWheelsSimple-v0",
    entry_point="ciircgym.envs.mujoco.simple_env:PepperWheelsSimpleEnv",
    max_episode_steps=500,
)

register(
    id="PepperWheelsFixedSimple-v0",
    entry_point="ciircgym.envs.mujoco.simple_env:PepperWheelsFixedSimpleEnv",
    max_episode_steps=500,
)

register(
    id="PepperReachMinimal-v0",
    entry_point="ciircgym.envs.pepper.pepper_env:PepperEnv",
    max_episode_steps=200,
)

register(
    id="PepperReachCamera-v0",
    entry_point="ciircgym.envs.pepper.peppercam_env:PepperCamEnv",
    max_episode_steps=50,
)

register(
    id="PepperGrasp-v0",
    entry_point="ciircgym.envs.pepper.pepper_grasp:PepperGraspEnv",
    max_episode_steps=200,
)

register(
    id="PepperThrow-v0",
    entry_point="ciircgym.envs.pepper.pepper_throw:PepperThrowEnv",
    max_episode_steps=200,
)


# --- PEPPER PYBULLET ENVS ---

register(
    id="PepperThrowQibullet-v0",
    entry_point="ciircgym.envs.pepper.pepper_qibullet_thrower:RobotEnv",
    max_episode_steps=200,
)

register(
    id="PepperReachQibullet-v0",
    entry_point="ciircgym.envs.pepper.pepper_qibullet_reacher:RobotEnv",
    max_episode_steps=512,
)

register(
    id="PepperMoveQibullet-v0",
    entry_point="ciircgym.envs.pepper.pepper_qibullet_mover:RobotEnv",
    max_episode_steps=5120,
)

# Kuka reach training environments
register(
    id="KukaReachWorkspace-v0",
    entry_point="ciircgym.envs.mujoco.kuka_reach_mujoco_workspace:KukaReach",
    max_episode_steps=2500,
)
register(
    id="KukaReachKitchenUnit-v0",
    entry_point="ciircgym.envs.mujoco.kuka_reach_mujoco_kitchen_unit:KukaReach",
    max_episode_steps=2500,
)
register(
    id="KukaReach603-v0",
    entry_point="ciircgym.envs.mujoco.kuka_reach_mujoco_603:KukaReach",
    max_episode_steps=2500,
)

# Kuka push training environments
register(
    id="KukaPushWorkspace-v0",
    entry_point="ciircgym.envs.mujoco.kuka_push_mujoco_workspace:KukaPush",
    max_episode_steps=1800,
)
register(
    id="KukaPushKitchenUnit-v0",
    entry_point="ciircgym.envs.mujoco.kuka_push_mujoco_kitchen_unit:KukaPush",
    max_episode_steps=1800,
)
register(
    id="KukaPush603-v0",
    entry_point="ciircgym.envs.mujoco.kuka_push_mujoco_room_603:KukaPush",
    max_episode_steps=1800,
)

# Kuka pick training environment
register(
    id="KukaPickWorkspace-v0",
    entry_point="ciircgym.envs.mujoco.kuka_pick_mujoco_workspace:KukaPick",
    max_episode_steps=2500,
)

# Kuka pick and place training environments
register(
    id="KukaPickAndPlaceWorkspace-v0",
    entry_point="ciircgym.envs.mujoco.kuka_pick_and_place_mujoco_workspace:KukaPickAndPlace",
    max_episode_steps=2500,
)
register(
    id="KukaPickAndPlaceKitchenUnit-v0",
    entry_point="ciircgym.envs.mujoco.kuka_pick_and_place_mujoco_kitchen_unit:KukaPickAndPlace",
    max_episode_steps=2500,
)
register(
    id="KukaPickAndPlace603-v0",
    entry_point="ciircgym.envs.mujoco.kuka_pick_and_place_mujoco_room_603:KukaPickAndPlace",
    max_episode_steps=2500,
)

# Kuka throw training environments
register(
    id="KukaThrowWorkspace-v0",
    entry_point="ciircgym.envs.mujoco.kuka_throw_mujoco_workspace:KukaThrow",
    max_episode_steps=2500,
)
register(
    id="KukaThrowKitchenUnit-v0",
    entry_point="ciircgym.envs.mujoco.kuka_throw_mujoco_kitchen_unit:KukaThrow",
    max_episode_steps=2500,
)
register(
    id="KukaThrow603-v0",
    entry_point="ciircgym.envs.mujoco.kuka_throw_mujoco_603:KukaThrow",
    max_episode_steps=2500,
)
################################################################################
# ------------------------ PANDA MUJOCO ENVIRONMENTS ---------------------------
# Panda reach training environments
register(
    id="PandaReachWorkspace-v0",
    entry_point="ciircgym.envs.mujoco.panda_reach_mujoco_workspace:PandaReach",
    max_episode_steps=2500,
)
register(
    id="PandaReachKitchenUnit-v0",
    entry_point="ciircgym.envs.mujoco.panda_reach_mujoco_kitchen_unit:PandaReach",
    max_episode_steps=2500,
)
register(
    id="PandaReach603-v0",
    entry_point="ciircgym.envs.mujoco.panda_reach_mujoco_603:PandaReach",
    max_episode_steps=2500,
)

# Panda throw training environments
register(
    id="PandaThrowWorkspace-v0",
    entry_point="ciircgym.envs.mujoco.panda_throw_mujoco_workspace:PandaThrow",
    max_episode_steps=2500,
)
register(
    id="PandaThrowKitchenUnit-v0",
    entry_point="ciircgym.envs.mujoco.panda_throw_mujoco_kitchen_unit:PandaThrow",
    max_episode_steps=2500,
)
register(
    id="PandaThrow603-v0",
    entry_point="ciircgym.envs.mujoco.panda_throw_mujoco_603:PandaThrow",
    max_episode_steps=2500,
)

# Panda push training environments
register(
    id="PandaPushWorkspace-v0",
    entry_point="ciircgym.envs.mujoco.panda_push_mujoco_workspace:PandaPush",
    max_episode_steps=2500,
)
register(
    id="PandaPushKitchenUnit-v0",
    entry_point="ciircgym.envs.mujoco.panda_push_mujoco_kitchen_unit:PandaPush",
    max_episode_steps=1800,
)
register(
    id="PandaPush603-v0",
    entry_point="ciircgym.envs.mujoco.panda_push_mujoco_603:PandaPush",
    max_episode_steps=1800,
)

# Panda pick and place training environments
register(
    id="PandaPickAndPlaceWorkspace-v0",
    entry_point="ciircgym.envs.mujoco.panda_pick_and_place_mujoco_workspace:PandaPickAndPlace",
    max_episode_steps=2500,
)
register(
    id="PandaPickAndPlaceKitchenUnit-v0",
    entry_point="ciircgym.envs.mujoco.panda_pick_and_place_mujoco_kitchen_unit:PandaPickAndPlace",
    max_episode_steps=2500,
)
register(
    id="PandaPickAndPlace603-v0",
    entry_point="ciircgym.envs.mujoco.panda_pick_and_place_mujoco_603:PandaPickAndPlace",
    max_episode_steps=2500,
)

################################################################################

register(
    id="Kuka-v0",
    entry_point="ciircgym.envs.kuka:KukaEnv",
    max_episode_steps=200,
)

register(
    id="KukaWorkspaceObjectsBB-v0",
    entry_point="ciircgym.envs.mujoco.kuka_workspace_objects_BB:KukaWorkspaceObjectsBBEnv",
    max_episode_steps=200,
)

register(
    id="KukaVision-v0",
    entry_point="ciircgym.envs.mujoco.kuka_vision:KukaVisionEnv",
    max_episode_steps=200,
)

register(
    id="KukaSimpleTouch-v0",
    entry_point="ciircgym.envs.mujoco.kuka_simple_touch:KukaSimpleTouch",
    max_episode_steps=200,
)

register(
    id="KukaIiwaSimple-v0",
    entry_point="ciircgym.envs.mujoco.simple_env:KukaIiwaSimpleEnv",
    max_episode_steps=500,
)

register(
    id="KukaIiwaMagneticSimple-v0",
    entry_point="ciircgym.envs.mujoco.simple_env:KukaIiwaMagneticGripperSimpleEnv",
    max_episode_steps=500,
)

register(
    id="KukaIiwaReflexSimple-v0",
    entry_point="ciircgym.envs.mujoco.simple_env:KukaIiwaReflexTakktileSimpleEnv",
    max_episode_steps=500,
)

register(
    id="KukaIiwaReflexSensorsSimple-v0",
    entry_point="ciircgym.envs.mujoco.simple_env:KukaIiwaReflexTakktileSensorsSimpleEnv",
    max_episode_steps=500,
)

register(
    id="KukaIiwaTwoFingerSimple-v0",
    entry_point="ciircgym.envs.mujoco.simple_env:KukaIiwaTwoFingerSimpleEnv",
    max_episode_steps=500,
)

register(
    id="KukaWorkspaceSimple-v0",
    entry_point="ciircgym.envs.mujoco.simple_env:KukaWorkspaceSimpleEnv",
    max_episode_steps=10000,
)

register(
    id="KukaWorkspaceHumanoidSimple-v0",
    entry_point="ciircgym.envs.mujoco.simple_env:KukaWorkspaceHumanoidSimpleEnv",
    max_episode_steps=500,
)

register(
    id="KukaWorkspaceLeftSimple-v0",
    entry_point="ciircgym.envs.mujoco.simple_env:KukaWorkspaceLeftSimpleEnv",
    max_episode_steps=500,
)

register(
    id="KukaWorkspaceRightSimple-v0",
    entry_point="ciircgym.envs.mujoco.simple_env:KukaWorkspaceRightSimpleEnv",
    max_episode_steps=500,
)

# --- KUKA PYBULLET ENVS ---

register(
    id="KukaWorkspacePyBullet-v0",
   entry_point="ciircgym.envs.kuka_workspace_env:KukaWorkspaceEnvPyBullet",
    max_episode_steps=200,
)

register(
    id="KukaEnvPyBullet-v0",
   entry_point="ciircgym.envs.old_structure.kuka_env_pybullet:KukaGymEnv",
    max_episode_steps=200,
)

register(
    id="KukaEnvPyBulletLP-v0",
   entry_point="ciircgym.envs.old_structure.kuka_env_pybullet:KukaGymEnvLP",
    max_episode_steps=200,
)

register(
    id="KukaEnvPyBulletOneHand-v0",
   entry_point="ciircgym.envs.old_structure.kuka_env_pybullet_one_hand:KukaGymEnv",
    max_episode_steps=200,
)

register(
    id="CrowTestEnv-v0",
    entry_point="ciircgym.envs.crow_test_env:CrowTestEnv",
    max_episode_steps=25600,
)

register(
    id="CrowDatasetsEnv-v0",
    entry_point="ciircgym.envs.crow_datasets_env:CrowDatasetsEnv",
    max_episode_steps=200,
)


# generate dataset - robots
register(
    id="CrowDatasetsEnv-v2",
    entry_point="ciircgym.envs.crow_datasets_env2:CrowDatasetsEnv",
    max_episode_steps=200,
)

register(
    id="KukaReach3D-v0",
   entry_point="ciircgym.envs.old_structure.kuka_reach_3d:KukaGymEnv",
    max_episode_steps=2560,
)

register(
    id="KukaReach3Dtest-v0",
   entry_point="ciircgym.envs.old_structure.kuka_reach_3d_test:KukaGymEnv",
    max_episode_steps=256,
)

register(
    id="KukaPickandPlace3D-v0",
   entry_point="ciircgym.envs.old_structure.kuka_pickandplace_3d:KukaPicknPlace",
    max_episode_steps=256,
)

register(
    id="CrowWorkspaceEnv-v0",
    entry_point="ciircgym.envs.crow_workspace_env:CrowWorkspaceEnv",
    max_episode_steps=8192,
)

register(
    id="RollingStoneEnv-v0",
    entry_point="ciircgym.envs.rolling_stone_env:RollingStoneEnv",
    max_episode_steps=256,
)

register(
    id="RollingStoneEnv-v1",
    entry_point="ciircgym.envs.rolling_stone_env1:RollingStoneEnv1",
    max_episode_steps=256,
)


register(
    id="KukaReach2D-v0",
   entry_point="ciircgym.envs.old_structure.kuka_reach_2d:KukaGymEnv",
    max_episode_steps=256,
)

register(
    id="ObjectTestEnv-v0",
   entry_point="ciircgym.envs.object_test_env:ObjectTestEnv",
    max_episode_steps=25600,
)

register(
    id="Kukamagneticgripper-v0",
   entry_point="ciircgym.envs.kuka_magnetic_gripper:KukamagneticgripperEnv",
    max_episode_steps=200,
)

# --- GRIPPERS MUJOCO ENVS---

register(
    id="BarrettHandSimple-v0",
    entry_point="ciircgym.envs.mujoco.simple_env:BarrettHandSimpleEnv",
    max_episode_steps=500,
)

register(
    id="BarrettHandTactileSimple-v0",
    entry_point="ciircgym.envs.mujoco.simple_env:BarrettHandTactileSimpleEnv",
    max_episode_steps=500,
)

register(
    id="BarrettHandTorqueSimple-v0",
    entry_point="ciircgym.envs.mujoco.simple_env:BarrettHandTorqueSimpleEnv",
    max_episode_steps=500,
)

register(
    id="BrunelHandSimple-v0",
    entry_point="ciircgym.envs.mujoco.simple_env:BrunelHandSimpleEnv",
    max_episode_steps=500,
)

register(
    id="BrunelHandTendonSimple-v0",
    entry_point="ciircgym.envs.mujoco.simple_env:BrunelHandSimpleEnv",
    max_episode_steps=500,
)

register(
    id="ReflexTakktileHandSimple-v0",
    entry_point="ciircgym.envs.mujoco.simple_env:ReflexTakktileHandSimpleEnv",
    max_episode_steps=500,
)

register(
    id="ReflexTakktileSensorsHandSimple-v0",
    entry_point="ciircgym.envs.mujoco.simple_env:ReflexTakktileHandSensorsSimpleEnv",
    max_episode_steps=500,
)

register(
    id="TwoFingerGripperSimple-v0",
    entry_point="ciircgym.envs.mujoco.simple_env:TwoFingerGripperSimpleEnv",
    max_episode_steps=500,
)

register(
    id="AdaptiveGripperSimple-v0",
    entry_point="ciircgym.envs.mujoco.simple_env:AdaptiveGripperSimpleEnv",
    max_episode_steps=500,
)

# --- ARMS MUJCO ENVS ---

register(
    id="GummiArmSimple-v0",
    entry_point="ciircgym.envs.mujoco.simple_env:GummiArmSimpleEnv",
    max_episode_steps=500,
)

register(
    id="PandaArmSimple-v0",
    entry_point="ciircgym.envs.mujoco.simple_env:PandaArmSimpleEnv",
    max_episode_steps=500,
)

register(
    id="ReachyArmSimple-v0",
    entry_point="ciircgym.envs.mujoco.simple_env:ReachyArmSimpleEnv",
    max_episode_steps=500,
)

register(
    id="UR3ArmSimple-v0",
    entry_point="ciircgym.envs.mujoco.simple_env:UR3ArmSimpleEnv",
    max_episode_steps=500,
)

register(
    id="UR5ArmSimple-v0",
    entry_point="ciircgym.envs.mujoco.simple_env:UR5ArmSimpleEnv",
    max_episode_steps=500,
)

register(
    id="UR10ArmSimple-v0",
    entry_point="ciircgym.envs.mujoco.simple_env:UR10ArmSimpleEnv",
    max_episode_steps=500,
)

register(
    id="YumiRobotSimple-v0",
    entry_point="ciircgym.envs.mujoco.simple_env:YumiRobotSimpleEnv",
    max_episode_steps=500,
)

# --- HUMAN MUJOCO ENVS ---

register(
    id="RealHandsSimple-v0",
    entry_point="ciircgym.envs.mujoco.simple_env:RealHandsSimpleEnv",
    max_episode_steps=500,
)

register(
    id="RealHandsHumanoidSimple-v0",
    entry_point="ciircgym.envs.mujoco.simple_env:RealHandsHumanoidSimpleEnv",
    max_episode_steps=500,
)
