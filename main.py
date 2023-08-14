from UI.RobotCumtomerUI import RobotCumtomerUI
from OPENCV_Analyze.OPENCV_Analyze import OPENCV_Analyze
from RobotBehavior.RobotBehavior import RobotBehavior
from skimage import morphology
# from visual.OpenCV import ImageAnalyze
# from robotsocket.SocketConnect import SocketConnect

from Common.Common import Common
CommonOB=Common()
robot_opencv_analyze = OPENCV_Analyze()
robot_cumtomer_ui = RobotCumtomerUI()
robotbehavior = RobotBehavior()
# opencv = ImageAnalyze()
if __name__ == '__main__':
    
    
    CommonOB.RobotCumtomerUI  = robot_cumtomer_ui
    CommonOB.RobotBehavior    = robotbehavior
    CommonOB.OPENCV_Analyze   = robot_opencv_analyze
    robot_opencv_analyze.get_Common(CommonOB)
    robot_cumtomer_ui.get_Common(CommonOB)
    robotbehavior.get_Common(CommonOB)
    
    robot_opencv_analyze.start_cam_PicReal(None)
    robot_cumtomer_ui.create_window()
