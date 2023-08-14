import threading
import ctypes
import inspect
from models.pal_color import Pal_Color
from models.line import line
from models.block_color import block_color
import numpy as np


class Common:
    def __init__(self):
        self.COM = "COM5"
        self.OPENCV_Analyze = None
        self.RobotCumtomerUI = None
        self.RobotBehavior = None

        self.threading_updateUI = None
        self.threading_robot_Move = None
        # 線段組--線搞
        self.draft_lines: list[line] = []
        # 線段組--顏色區塊
        self.colorful_lines: list[block_color] = []

        # 攝影機擷取範圍

        #  --       實際繪圖畫紙區
        self.get_ColorRealSize = [320, 320]  # (width,height)
        self.get_ColorRealSize_start = [430, 248]
        self.rotaoteAngle = -90
        self.is_scale_512 = False

        #  --       畫盤區
        self.get_ColorPaletteSize = [415, 200]  # (width,height)
        self.get_ColorPaletteSize_start = [367, 0]

        self.PalCell_start = [13, 12]  # (Cell_sx,Cell_sy)
        self.PalCell = [25, 40]  # (width,height)
        self.PalCell_offset = [14, 16]  # (width,height)

        #  --       主調盤
        self.Pal_main_start = [
            [240, 20],
            [240, 120],
            [350, 20],
            [350, 120],
        ]

        self.Pal_main = [50, 50]

        # 顏色行為範圍
        self.Color_Cells = []  # 調色盤單一顏色x12
        self.Color_Mains = []  # 調色盤主顏色x4
        self.color_goal = ""  # 目標色調

        self.color_mix_num_select = -1  # 選擇主色調區域
        self.color_mix_num_nocolor = []  # 沒顏色區域
        self.color_mix_num_color = []  # 有顏色區域

        # 新增調色盤上的區塊內顏色
        for i in range(0, 12):
            pal_Color = Pal_Color()
            pal_Color.Number = i + 1
            self.Color_Cells.append(pal_Color)

        # 新增調色盤上的主區塊內顏色
        for i in range(0, 4):
            pal_Color = Pal_Color()
            pal_Color.Number = i + 1
            self.Color_Mains.append(pal_Color)

        self.robot_pos_pause = [0, 0, 0]

        self.pal_contrast = 60
        self.pal_brightness = 90

        self.main_color_contrast = 0
        self.main_color_brightness = 0

        self.main_color_check_num = 0
        self.main_color_check_goal = "橙色"
        self.main_color_check_result = ""
        # 顏色HSB(Range)
        # TODO (錯誤)S 0-30 趨近於白灰
        # 合併成8色，黃、橙、紅、洋紅、紫、青、綠、黃綠

        self.Color_HSV = {
            # 主色
            "yellow": {
                "name": "黃色",
                "range": [np.array([21, 50, 50]), np.array([36, 255, 255])],
            },
            "orange": {
                "name": "橙色",
                "range": [np.array([10, 50, 50]), np.array([21, 255, 255])],
            },
            "crimson": {
                "name": "深紅色",
                "range": [np.array([170, 50, 50]), np.array([180, 255, 255])],
            },
            "crimson_2": {
                "name": "深紅色",
                "range": [np.array([0, 50, 50]), np.array([10, 255, 255])],
            },
            #  "rose": {"name": "玫瑰紅", "range": [np.array([169, 50, 50]), np.array([177, 255, 255])]},
            # 主色
            #  "magenta": {"name": "洋紅色", "range": [np.array([155, 50, 50]), np.array([170, 255, 255])]},
            "magenta": {
                "name": "洋紅色",
                "range": [np.array([155, 50, 50]), np.array([170, 255, 255])],
            },
            "purpose": {
                "name": "紫色",
                "range": [np.array([130, 50, 50]), np.array([155, 255, 255])],
            },
            # "blue-purpose": {
            #     "name": "藍紫色",
            #     "range": [np.array([118, 50, 50]), np.array([135, 255, 255])],
            # },
            # "blue": {
            #     "name": "藍色",
            #     "range": [np.array([113, 50, 50]), np.array([133, 255, 255])],
            # },
            # 主色
            "cyan": {
                "name": "青色",
                "range": [np.array([93, 50, 50]), np.array([130, 255, 255])],
            },
            "green": {
                "name": "綠色",
                "range": [np.array([36, 50, 50]), np.array([93, 255, 255])],
            },
            # "spring_green": {
            #     "name": "春綠色",
            #     "range": [np.array([56, 50, 50]), np.array([70, 255, 255])],
            # },
            "chartreuse_green": {
                "name": "黃綠色",
                "range": [np.array([37, 50, 50]), np.array([56, 255, 255])],
            },
        }

        # 用於判斷色階範圍與高低
        # 用色的量影響最終顏色，故要判斷先從哪個開始調
        # !!!注意!!!! 顏色會越調越深，當接近於深色或黑色時就無法再調
        # 現實中藍色、藍紫色、紫色區域比青色深，有需要再調嗎?

        self.Systems_Colors = [
            # ["黃色","橙色","深紅色","玫瑰紅","洋紅色"], #黃-深紅色
            ["黃色", "橙色", "深紅色", "洋紅色"],  # 黃-深紅色
            ["洋紅色", "紫色", "藍色", "青色"],  # 洋紅色-藍色
            ["青色", "綠色", "黃綠色", "黃色"],  # 青色-黃綠色
        ]

        # 顏色混色
        # -1. 指定目標顏色
        # -2. 檢查色格裡面的顏色有符合目標色
        # -有 - 抓取
        # -無 - 判斷主色盤4格裡是否符合目標色
        # -有 - 抓取
        # -無 - 判斷主色盤4格裡是否有空格
        # -有 - 調色
        # -無 - 判斷主色盤4格是否有哪一格可以調色(顏色相近)
        # -有 - 調色
        # -無 - 人工擦拭 - 回到(判斷主色盤4格裡是否有空格)
        # -3. 調色(可能狀況)
        # 擷取色格需要洗一次筆
        #   橙色orange-> 黃色 -(洋紅色)橙色
        #   深紅色crimson-> 黃色 -(洋紅色)橙色  -(洋紅色)深紅色
        #   玫瑰紅rose-> 黃色 -(洋紅色)橙色 -(洋紅色)深紅色 -(洋紅色)玫瑰紅 ->(過頭)黃色

        #   紫色purpose-> 洋紅色 -(青色)紫色
        #   藍紫色blue-purpose-> 青色 -(黃色)藍色   -(黃色)藍紫色
        #   藍色blue-> 青色 -(洋紅色)藍色

        #   綠色green-> 青色 -(黃色)綠色
        #   春綠色-spring_green-> 青色 - (黃色)綠色   -(黃色)春綠色
        #   黃綠色-chartreuse_green-> 黃色 -(青色)黃綠色

        # 記錄區-用於停止時重啟使用
        self.record_block_num = -1
        self.record_color_num = -1
        self.record_conturs_num = -1
        self.record_line_num = -1
        self.record_pen_num = -1
        self.record_robot_status = ""

        # 筆的數量
        self.pen_times_draft_setting = 7
        self.pen_times_draft_setting_draft = 1
        self.UI_PicReal_size = (1280, 720)

        # 手臂設定範圍
        # 中心
        self.center = [235.55, 0, -42.09]

        # 邊界 圖片左上、左下、右上、右下
        # z:-62.3?  z:-42.09?
        self.border_pic = [
            [282.55, 45, -42.09],
            [188.55, 45, -42.09],
            [282.55, -45, -42.09],
            [188.55, -45, -42.09],
        ]
        # 抬筆高度
        self.uppen = 5

        self.z_range = [-43.0, -41.9]  # (y = 0-1)
        # 調色盤中間點- 色盤與主調色的中間左邊源
        self.center_p_Palette = [242.55, -58, -27]

        # 畫區中間點- 色盤與主調色的中間左邊源
        self.center_main = [242.55, 0, -20]

        # 調色盤位置12個位置
        # 4-[249.55, -67,-45],
        # 9-[291.55, -105,-45]
        # 上: -37,下 : -44
        # 左右 y+-3 挖色
        self.up_Palette = -34
        self.down_Palette = [-37.5, -42]  # -41~-37
        self.border_Palette = [
            [291.55, -67, -37.8],  # 0
            [278.55, -67, -37.8],  # 1
            [263.55, -67, -37.8],  # 2
            [249.55, -67, -37],  # 3
            [291.55, -86, -37],  # 4
            [278.55, -86, -37],  # 5
            [263.55, -86, -37],  # 6
            [247.55, -86, -37],  # 7
            [291.55, -105, -37],  # 8
            [278.88, -105, -37],  # 9
            [263.21, -105, -37],  # 10
            [247.55, -105, -37],  # 11
        ]
        # 調色盤調色位置4個位置
        # 上: -37,下 : -43.55
        # 上下 y+-6  左右 y+-7 調色
        self.border_Palette_Main = [
            [229.55, -73, -45.55],
            [229.55, -103, -45.55],
            [199.55, -73, -45.55],
            [199.55, -103, -45.55],
        ]

        # 沾水跟衛生紙中間點
        self.center_p_Dig = [235.55, 64, -10]

        # 高=> Z: -10 高=> z:-16
        self.border_DigWater = [
            [257.55, 81, -26],  # 中間
            [243.55, 68, -19],  # 後
            [266.55, 100, -19],  # 前
            [275.55, 66, -19],  # 後2
        ]

        # 左右 y+-7
        # Z:-22
        self.border_DigIssue = [
            [207.55, 81, -40],
        ]

        # 程序狀態範圍
        # --        程序狀態
        self.status_program = {
            "None": 0,
            "Active_Robot": 1,
            "Active_Img": 2,
            "Finish_Img": 3,
        }

        self.status_program_now = self.status_program["None"]

        # --        機器人測試狀態
        self.status_robotTest = {
            "None": 0,
            "Dig_Water": 1,
            "Dig_Issue": 2,
            "Dig_pal": 3,
            "Color_mixing": 4,
            "Dig_Color": 5,
            "draw_main": 6,
        }
        self.status_robotTest_now = self.status_robotTest["None"]

        # --        機器人執行繪畫狀態
        self.status_robot = {
            "None": 0,
            #    'Color_Dip' :1,
            #    'Water_Dip' :2,
            #    'Paper_Dip' :3, # 沾衛生紙
            "Color_Status_Check": 4,  # 顏色狀態判斷
            "Color_Main_Select": 5,  # 選擇顏色
            "Color_Mix": 6,  # 混色
            "Color_Mix_Select_Check": 7,  # 檢查混色
            "Pic_Draw": 8,
            "Draft_Draw": 9,  # 外圍線搞
        }

        self.status_robot_now = self.status_robot["None"]

        # 圖片資訊等紀錄範圍-5j4u3
        self.picPc_ori_draft = None  # 線搞
        self.picPc_ori_draft_block_dis = None
        self.picPc_ori_draft_bone = None  # 線搞－骨架
        self.picPc_ori_colorful = None  # 彩圖
        self.picPc_ori_colorful_dis = None  # 彩圖-用來繪製單一區塊
        self.picPc_ori_colorful_dis_mask = None  # 彩圖單一顏色MASK-區塊單一顏色的MASK

        self.image_pic_real = None  # 真實的畫面，PIL.ImageTk.PhotoImage 形式

        self.picPc_ori_colorful_blocks = []  # 彩圖-各自區塊彩圖

        self.blocks_colorful_countor = []  # 各block區塊coutor
        self.block_colorful_colors_info = []  # 顏色區塊內的顏色資訊
        # colors []
        # percent_sum 比例
        # predict 顏色

        self.blocks_colors_path = []
        # 顏色區塊內的顏色路徑(尚未轉成機器人繪畫路徑) 結構
        # block
        # - color
        #   -coutur(單一顏色可能會有兩個以上的coutur)
        #     -path
        #       -point

        self.select_block_num = -1
        self.select_block_color_num = -1

        self.updateWindow_bool = True
        self.is_ignore_active = False

    # 執行ctype指令
    def async_raise(self, tid, exctype):
        """raises the exception, performs cleanup if needed"""
        tid = ctypes.c_long(tid)
        if not inspect.isclass(exctype):
            exctype = type(exctype)
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
        if res == 0:
            raise ValueError("invalid thread id")
        elif res != 1:
            # """if it returns a number greater than one, you're in trouble,
            # and you should call it again with exc=NULL to revert the effect"""
            ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
            raise SystemError("PyThreadState_SetAsyncExc failed")

    def _get_my_tid(self):
        """determines this (self's) thread id

        CAREFUL: this function is executed in the context of the caller
        thread, to get the identity of the thread represented by this
        instance.
        """
        if not self.isAlive():
            raise threading.ThreadError("the thread is not active")

        # do we have it cached?
        if hasattr(self, "_thread_id"):
            return self._thread_id

        # no, look for it in the _active dict
        for tid, tobj in threading._active.items():
            if tobj is self:
                self._thread_id = tid
                return tid

        # TODO: in python 2.6, there's a simpler way to do: self.ident

        raise AssertionError("could not determine the thread's id")

    # 停止線程
    def stop_thread(self, thread):
        self.async_raise(thread.ident, SystemExit)
