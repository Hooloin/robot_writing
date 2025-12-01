# 内容：工业机器人写字应用仿真程序
# 时间：2018/6/19
# RoboDK Version: 3.4.1

from robolink import *      # 加载robolink模块
from robodk import *        # 加载robodk模块

import sys                  # 加载sys模块
import os                   # 加载os

RDK = Robolink()            # 定义RoboDK工作站

# 定义工作站中的对象
robot = RDK.Item('ABB IRB 120-3/0.6')            # 定义机器人对象
write_frame = RDK.Item('写字坐标系')              # 定义写字坐标系：write_frame
write_tool = RDK.Item('画笔')                    # 定义写字工具
pixel = RDK.Item('像素点')                        # 定义写字像素点
image_template = RDK.Item('模板')                 # 定义画板的模板
image = RDK.Item('画板')                          # 预定义工作站的画板

######## 定义函数 ###########

# 定义函数：将二维空间中的点转化为三维空间中的点（4*4矩阵）
def point2D_2_pose(point, tangent):
    return transl(point.x, point.y, 0)*rotz(tangent.angle())

# 机器人写字程序
def svg_write_robot(svg_img, board, pix, item_frame, item_tool, robot):
    APPROACH = 10                                              # 定义常量APPROACH为100     
    home_joints = [0,0,0,0,-90,0]                                # 定义机器人的起始位置
    
    robot.setPoseFrame(item_frame)                              # 定义机器人的工件坐标系
    robot.setPoseTool(item_tool)                                # 定义机器人的工具坐标系
    robot.MoveJ(home_joints)                                    # 机器人移动到起始位置
    
    orient_frame2tool = roty(pi)                                # 定义写字目标点的方向

    for path in svg_img:                                        # 遍历svg_img中的path数据
        pix.Recolor(path.fill_color)                            # 根据svg图片中文字的颜色设置仿真时文字的颜色

        np = path.nPoints()                                     # 获得该path路径中所有的点

        p_0 = path.getPoint(0)                                  # 定义path中的第一个点
        target0 = transl(p_0.x, p_0.y, 0)*orient_frame2tool     # 将p_0转化为机器人目标点target_0(4*4矩阵)
        target0_app = target0*transl(0,0,-APPROACH)             # 定义目标点：target0_app
        robot.MoveL(target0_app)                                # 机器人移动到目标点target0_app

        for i in range(np):                                     # 遍历np中所有的点
            p_i = path.getPoint(i)                              # 定义path路径中的第i个点的值：p_i  
            v_i = path.getVector(i)                             # 定义path路径中的第i个点的方向：v_i  
            pt_pose = point2D_2_pose(p_i, v_i)                  # 将二维空间的点p_i转化为三维空间的点：pt_pose
            
            target = transl(p_i.x, p_i.y, 0)*orient_frame2tool  # 定义机器人写字的目标点：target

            robot.MoveL(target)                                 # 机器人移动到目标点：target

            board.AddGeometry(pix, pt_pose)                     # RoboDK工作站添加文字笔画

        target_app = target*transl(0,0,-APPROACH)               # 定义目标点：target_app
        robot.MoveL(target_app)                                 # 机器人移动到目标点：target_app
        
    robot.MoveL(home_joints)                                    # 机器人返回起始位置

######## 机器人写字主程序 #########

# 从svgpy文件夹中加载svg模块
path_stationfile = RDK.getParam('PATH_OPENSTATION')     # 获取当前工作站的路径
sys.path.append(os.path.abspath(path_stationfile))      # 将当前工作站的路径添加到系统路径中
from svgpy.svg import *                                 # 加载svg模块

# 指定所要写字的svg格式图片，并处理该图片数据
IMAGE_FILE = 'zju.svg'                           # 定义所需的svg格式的图片名称，用户可以修改
svgfile = path_stationfile + '/svg_pic/' + IMAGE_FILE   # 定义该图片所在的路径

svgdata = svg_load(svgfile)                             # svg_load函数加载该图片，获得该图片的数据

IMAGE_SIZE = Point(200, 300)                            # 定义写字区域的大小
MM_X_PIXEL = 0.5                                          # 定义文字的分辨率 
svgdata.calc_polygon_fit(IMAGE_SIZE, MM_X_PIXEL)        # 根据IMAGE_SIZE和MM_X_PIXEL调整svgdata
size_img = svgdata.size_poly()                          # 返回调整后的图片数据

# 开始写字前，删除工作站中已有的文字图片对象
if image.Valid() and image.Type() == ITEM_TYPE_OBJECT: image.Delete()

# 复制画板模板，生成新的对象，并命名为画板，设置其尺寸大小
image_template.Copy()                                   # 复制工作站中的对象：画板模板
image = write_frame.Paste()                             # 写字坐标系下粘贴画板模板
image.setVisible(True, False)                           # 复制得到的对象设置显示可见
image.setName('画板')                                    # 复制得到的对象设置名称为：画板
image.Scale([size_img.x/250, size_img.y/250, 1])        # 根据图片数据调整画板的尺寸大小

# 调用机器人写字程序
svg_write_robot(svgdata, image, pixel, write_frame, write_tool, robot)

