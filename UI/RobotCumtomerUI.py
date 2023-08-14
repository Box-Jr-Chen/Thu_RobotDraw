# coding=utf-8
import os
import threading
import time
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from datetime import datetime

from pathlib import Path
from PIL import Image, ImageTk
from functools import partial
from tktooltip import ToolTip
import re
import numpy as np


class RobotCumtomerUI:
    def __init__(self):
        self.common = None
        self.window = None
        self.tab_RobotControl = None
        self.tab_PicPC = None
        self.tab_PicReal = None
        self.tab_ColorPalette = None

        self.window_height = 620
        self.window_width = 1580
        self.img_draft = None
        self.img_colorful = None
        self.img_colorful_block = None
        self.camreal_canvas = None  # 調色盤

        # 查看調色盤的分析結果
        self.camreal_canvas_anyaize = []
        self.camreal_main_canvas_anyaize = []

        self.picPc_ori_canvas = None
        self.picPc_color_canvas = None
        self.picPc_color_block_canvas = None
        self.colorful_box_blocks = None

        # colorful_box_block 的提示
        self.colorful_box_block_tooltips = []
        self.colorful_box_block_tooltips_select = -1
        self.colorful_box_blocktext = ""

        self.picReal_canvas = None  # 實際畫
        self.picReal_campare_canvas = None  # 實際畫
        self.width_picPc_ori = 550

        self.get_pic_ori_btn = None
        self.get_pic_ori_bone_btn = None
        self.get_pic_color_btn = None

        self.get_real_pic_btn = None

        # get frame
        self.photo = None

        # 調色盤介面內容
        self.cam_Color_Pa_Start = [None, None]
        self.cam_Color_Pa_Size = [None, None]

        self.cam_Color_Cell_Start = [None, None]
        self.cam_Color_Cell_Size = [None, None]
        self.cam_Color_Cell_Offset = [None, None]

        # 預判顏色
        self.cam_Color_Cell_info = [
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
        ]
        # HSV
        self.cam_Color_Cell_HSV_info = [
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
        ]
        self.cam_Color_Main_Start = [
            [None, None],
            [None, None],
            [None, None],
            [None, None],
        ]

        self.cam_Color_Main_Start_info = [None, None, None, None]
        self.cam_Color_Main_Start_HSV_info = [None, None, None, None]

        self.pal_contrast_string = None
        self.pal_brightness_string = None

        self.main_color_contrast_string = None
        self.main_color_brightness_string = None

        self.cam_Color_Main_Size = [None, None]
        # 實際繪圖
        self.get_ColorRealSize = [None, None]
        self.get_ColorRealSize_start = [None, None]
        self.rotaoteAngle = None
        self.is_scale_512 = None
        # 輸入圖畫內容
        self.block_box_blocks = None
        # 機械手臂驅動測試
        # 動作初始
        self.robot_init_btn = None
        # 調色盤動作x12
        self.robot_pal_color_btns = []
        # 調色盤主調色動作x4
        self.robot_pal_main_btns = []
        # 沾水動作
        self.robot_dig_water_btn = None
        # 沾衛生紙動作
        self.robot_dig_issue_btn = None
        # 主畫區測試動作
        self.robot_draw_block_btn = None
        self.robot_draw_block_Entry_x = None
        self.robot_draw_block_Entry_y = None

        self.robot_draw_block_String_x = None
        self.robot_draw_block_String_y = None

        self.robot_draw_test_x = 0
        self.robot_draw_test_y = 0

        # 機械手臂正式開始
        # 開始繪製(start)
        self.robot_draw_start_btn = None
        # 重啟繪製(restart)
        self.robot_draw_restart_btn = None
        # 停止繪製(stop)
        self.robot_draw_stop_btn = None
        # 暫停(可再繼續)繪製(pause)
        self.robot_draw_pause_btn = None

        # 測試繪畫---線搞繪圖
        self.robot_draft_test_btn = None

        # check draft status  0 =ftaft,1=bone
        self.draft_status = 0

        # 預先判斷
        self.main_num_color_check = None
        self.main_color_goal_check = None
        self.main_color_check_result = None
        self.main_color_check_result_label = None

        # 狀態
        self.record_block_num = None
        self.record_color_num = None
        self.record_conturs_num = None
        self.record_line_num = None
        self.record_pen_num = None
        self.record_robot_status = None

    # 草圖顯示
    def get_pic_ori_draft(self):
        filename = filedialog.askopenfilename()

        if filename != "":
            self.common.OPENCV_Analyze.Set_img_ori_draft(filename)
            im = Image.fromarray(self.common.picPc_ori_draft)
            im = self.resize_show(im)

            # 再次顛倒
            im = im.transpose(method=Image.FLIP_TOP_BOTTOM)

            self.img_draft = ImageTk.PhotoImage(im)
            self.picPc_ori_canvas.create_image(0, 0, anchor=tk.NW, image=self.img_draft)

    # 骨架顯示
    def get_pic_ori_draft_bone(self):
        index = self.block_box_blocks.curselection()

        if index:
            # 取消選中狀態
            self.block_box_blocks.selection_clear(index[0])
            self.draft_status = 1

        if self.draft_status == 0:
            im = Image.fromarray(self.common.picPc_ori_draft_bone)
            self.draft_status = 1
        elif self.draft_status == 1:
            im = Image.fromarray(self.common.picPc_ori_draft)
            self.draft_status = 0

        im = self.resize_show(im)

        # 再次顛倒
        im = im.transpose(method=Image.FLIP_TOP_BOTTOM)

        self.img_draft = ImageTk.PhotoImage(im)
        self.picPc_ori_canvas.create_image(0, 0, anchor=tk.NW, image=self.img_draft)

    def get_pic_ori_colorful(self):
        filename = filedialog.askopenfilename()

        if filename != "":
            im = None
            self.common.OPENCV_Analyze.Set_img_ori_colorful(filename)
            im = Image.fromarray(self.common.picPc_ori_colorful)
            im = self.resize_show(im)

            # 再次顛倒
            im = im.transpose(method=Image.FLIP_TOP_BOTTOM)

            # 區塊顯示
            if self.common.select_block_num != -1:
                self.common.OPENCV_Analyze.fun_colorful_seleted_block(
                    self.common.select_block_num
                )
                im = Image.fromarray(self.common.picPc_ori_colorful_dis)
                im = self.resize_show(im)
                # 再次顛倒
                im = im.transpose(method=Image.FLIP_TOP_BOTTOM)

            self.img_colorful = ImageTk.PhotoImage(im)
            self.picPc_color_canvas.create_image(
                0, 0, anchor=tk.NW, image=self.img_colorful
            )

    def save_pic_real(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".jpg", filetypes=[("Image Files", "*.jpg")]
        )

        if file_path != "":
            self.common.image_pic_real.save(file_path, "JPEG")

    def compare_pic_real(self):
        word_label = tk.Label(
            self.tab_PicReal, text="電腦圖片 :", font=("Microsoft JhengHei", 12)
        )
        word_label.place(x=1000, y=5)

        self.picReal_campare_canvas = tk.Canvas(
            self.tab_PicReal,
            width=self.width_picPc_ori,
            height=self.width_picPc_ori,
            bg="gray",
            highlightthickness=1,
            highlightbackground="black",
        )
        self.picReal_campare_canvas.place(x=1000, y=30)

        if self.img_colorful is not None:
            self.picReal_campare_canvas.create_image(
                0, 0, anchor=tk.NW, image=self.img_colorful
            )

    # 0 -1 驗證
    def validate_entry(self, text):
        try:
            value = float(text)
            return 0 <= value <= 1  # 允许的范围是0到1
        except ValueError:
            return False

    def validate_input(self, text):
        return re.match(r"^[0-1]*(\.[0-9]{0,2})?$", text) is not None

    def get_robot_main_test(self):
        self.robot_draw_test_x = self.robot_draw_block_String_x.get()
        self.robot_draw_test_y = self.robot_draw_block_String_y.get()

        self.robot_draw_test_x = format(float(self.robot_draw_test_x), ".2f")
        self.robot_draw_test_y = format(float(self.robot_draw_test_y), ".2f")

        self.robot_draw_block_String_x.set(self.robot_draw_test_x)
        self.robot_draw_block_String_y.set(self.robot_draw_test_y)

        self.common.RobotBehavior.fun_robot_behavior[9](
            self.robot_draw_test_x, self.robot_draw_test_y
        )

    def resize_show(self, im):
        width, height = im.size
        if int(self.width_picPc_ori) < height:
            small_height = int(int(self.width_picPc_ori))
            small_weight = int(small_height * (width / height))
            im = im.resize((small_weight, small_height))
        return im

    def resize_canvas_show(self, im, canvas):
        width, height = im.size
        c_w = canvas.winfo_width()
        c_h = canvas.winfo_height()

        # 如果圖片大於canvas
        if width > c_w or height > c_h:
            small_height = 0
            small_weight = 0
            if width > height:
                small_weight = c_w - 10
                small_height = int(small_weight * (height / width))
            else:
                small_height = c_h - 10
                small_weight = int(small_height * (width / height))

            im = im.resize((small_weight, small_height))
        return im

    def get_Common(self, CommonOb):
        self.common = CommonOb

    def fun_listbox_getblocks(self):
        if len(self.common.blocks_colorful_countor) > 0:
            for i in range(0, len(self.common.blocks_colorful_countor)):
                self.block_box_blocks.insert(tk.END, f"區塊_{i+1}")

    def get_colorful_box_blocktext(self):
        return self.colorful_box_blocktext

    def show_tooltip_listbox(self, event):
        widget = event.widget
        index = self.colorful_box_blocks.index("@%s,%s" % (event.x, event.y))
        # self.colorful_box_blocktext = widget.get(index)
        if index < len(
            self.common.block_colorful_colors_info[self.common.select_block_num]
        ):
            for c_num in range(
                0,
                len(
                    self.common.block_colorful_colors_info[self.common.select_block_num]
                ),
            ):
                if index == c_num:
                    self.colorful_box_blocktext = ",".join(
                        map(
                            str,
                            self.common.block_colorful_colors_info[
                                self.common.select_block_num
                            ][c_num]["colors"],
                        )
                    )
        else:
            self.colorful_box_blocktext = ""

    # 草圖區塊顯示選取
    def on_select_block(self, event):
        if len(self.block_box_blocks.curselection()) <= 0:
            self.block_box_blocks.selection_set(self.common.select_block_num)
            return

        self.common.select_block_num = int(self.block_box_blocks.curselection()[0])

        # 在標籤上顯示選擇的項目
        # 原始
        self.common.OPENCV_Analyze.fun_draft_seleted_block(self.common.select_block_num)

        im = Image.fromarray(self.common.picPc_ori_draft_block_dis)
        im = self.resize_show(im)

        # 再次顛倒
        im = im.transpose(method=Image.FLIP_TOP_BOTTOM)

        self.img_draft = ImageTk.PhotoImage(im)
        self.picPc_ori_canvas.create_image(0, 0, anchor=tk.NW, image=self.img_draft)

        if isinstance(self.common.picPc_ori_colorful, np.ndarray):
            # 彩色
            self.common.OPENCV_Analyze.fun_colorful_seleted_block(
                self.common.select_block_num
            )

            im = Image.fromarray(self.common.picPc_ori_colorful_dis)
            im = self.resize_show(im)

            # 再次顛倒
            im = im.transpose(method=Image.FLIP_TOP_BOTTOM)

            self.img_colorful = ImageTk.PhotoImage(im)
            self.picPc_color_canvas.create_image(
                0, 0, anchor=tk.NW, image=self.img_colorful
            )

            # block
            im = Image.fromarray(
                self.common.picPc_ori_colorful_blocks[self.common.select_block_num]
            )
            im = self.resize_canvas_show(im, self.picPc_color_block_canvas)

            # 再次顛倒
            im = im.transpose(method=Image.FLIP_TOP_BOTTOM)

            self.img_colorful_block = ImageTk.PhotoImage(im)
            self.picPc_color_block_canvas.create_image(
                0, 0, anchor=tk.NW, image=self.img_colorful_block
            )

            self.colorful_box_blocks.delete(0, tk.END)

            for c in self.common.block_colorful_colors_info[
                self.common.select_block_num
            ]:
                colors_str = ",".join(map(str, c["colors"]))
                # des = f"{c['predict']} , 比例 {c['percent_sum']}\n {colors_str}"
                des = f"{c['predict']} , 比例 {c['percent_sum']}"
                self.colorful_box_blocks.insert(tk.END, des)

            # 多加一個判斷提示框結束
            self.colorful_box_blocks.insert(tk.END, "")

            self.colorful_box_blocks.bind("<Motion>", self.show_tooltip_listbox)
            ToolTip(
                self.colorful_box_blocks,
                self.get_colorful_box_blocktext,
                follow=True,
                delay=0,
            )

    # 彩圖區塊顯示選取
    def on_select_color(self, event):
        if len(self.colorful_box_blocks.curselection()) <= 0:
            self.colorful_box_blocks.selection_set(self.common.select_block_color_num)
            return

        self.common.select_block_color_num = int(
            self.colorful_box_blocks.curselection()[0]
        )
        self.common.OPENCV_Analyze.fun_colorful_seleted_color()

        im = Image.fromarray(self.common.picPc_ori_colorful_dis_mask)
        im = self.resize_canvas_show(im, self.picPc_color_block_canvas)

        # 再次顛倒
        im = im.transpose(method=Image.FLIP_TOP_BOTTOM)

        self.img_colorful_block = ImageTk.PhotoImage(im)
        self.picPc_color_block_canvas.create_image(
            0, 0, anchor=tk.NW, image=self.img_colorful_block
        )

    # 創造線搞跟彩稿測試按鈕
    def fun_create_paths_Test_inRobotControl(self):
        tab_RobotControl = self.tab_RobotControl

        word_label = tk.Label(
            tab_RobotControl, text="線稿測試 :", font=("Microsoft JhengHei", 12)
        )
        word_label.place(x=10, y=470)

        self.robot_draft_test_btn = tk.Button(
            tab_RobotControl,
            text=f"線稿動作",
            width=36,
            command=self.common.RobotBehavior.fun_robot_behavior[10],
        )
        self.robot_draft_test_btn.place(x=100, y=470)

        word_label = tk.Label(
            tab_RobotControl, text="彩色測試 :", font=("Microsoft JhengHei", 12)
        )
        word_label.place(x=10, y=520)

        half = int(len(self.common.picPc_ori_colorful_blocks) / 2)
        for i in range(0, len(self.common.picPc_ori_colorful_blocks)):
            x_p = int(i % half)
            y_p = int(i / half)

            self.robot_draft_test_btn = tk.Button(
                tab_RobotControl,
                text=f"區塊_{i+1}",
                width=14,
                command=partial(self.common.RobotBehavior.fun_robot_behavior[11], i),
            )
            self.robot_draft_test_btn.place(x=100 + x_p * 120, y=520 + y_p * 40)

        robot_pal_main_color_btn = tk.Button(
            tab_RobotControl,
            text=f"全區塊調色畫圖",
            width=36,
            command=self.common.RobotBehavior.fun_robot_behavior[13],
        )
        robot_pal_main_color_btn.place(x=700, y=520)

    def fun_tab_RobotControl(self):
        self.robot_draw_block_String_x = tk.StringVar()
        self.robot_draw_block_String_y = tk.StringVar()

        self.main_num_color_check = tk.StringVar()
        self.main_color_goal_check = tk.StringVar()
        self.main_color_check_result = tk.StringVar()

        self.record_block_num = tk.StringVar()
        self.record_color_num = tk.StringVar()
        self.record_conturs_num = tk.StringVar()
        self.record_line_num = tk.StringVar()
        self.record_pen_num = tk.StringVar()
        self.record_robot_status = tk.StringVar()

        self.robot_draw_block_String_x.set(self.robot_draw_test_x)
        self.robot_draw_block_String_y.set(self.robot_draw_test_y)

        self.main_num_color_check.set(self.common.main_color_check_num)
        self.main_color_goal_check.set(self.common.main_color_check_goal)
        # self.main_color_check_result.set(self.common.main_color_check_result)

        self.record_block_num.set(self.common.record_block_num)
        self.record_color_num.set(self.common.record_color_num)
        self.record_conturs_num.set(self.common.record_conturs_num)
        self.record_line_num.set(self.common.record_line_num)
        self.record_pen_num.set(self.common.record_pen_num)
        self.record_robot_status.set(self.common.record_robot_status)

        tab_RobotControl = self.tab_RobotControl

        # 動作初始
        word_label = tk.Label(
            tab_RobotControl, text="手臂動作 :", font=("Microsoft JhengHei", 12)
        )
        word_label.place(x=10, y=10)
        # 手臂初始
        self.robot_init_btn = tk.Button(
            tab_RobotControl,
            text="手臂初始",
            width=36,
            command=self.common.RobotBehavior.fun_robot_behavior[0],
        )
        self.robot_init_btn.place(x=100, y=10)
        # 開始繪製(start)
        self.robot_draw_start_btn = tk.Button(
            tab_RobotControl,
            text="開始繪製",
            width=36,
            command=self.common.RobotBehavior.fun_robot_behavior[1],
        )
        self.robot_draw_start_btn.place(x=400, y=10)
        # 重啟繪製(restart)
        self.robot_draw_restart_btn = tk.Button(
            tab_RobotControl,
            text="重啟繪製",
            width=36,
            command=self.common.RobotBehavior.fun_robot_behavior[2],
        )
        self.robot_draw_restart_btn.place(x=700, y=10)
        # 暫停繪製(stop)
        self.robot_draw_stop_btn = tk.Button(
            tab_RobotControl,
            text="暫停繪製",
            width=36,
            command=self.common.RobotBehavior.fun_robot_behavior[3],
        )
        self.robot_draw_stop_btn.place(x=1000, y=10)
        # 停止繪製(pause)
        self.robot_draw_pause_btn = tk.Button(
            tab_RobotControl,
            text="停止繪製",
            width=36,
            command=self.common.RobotBehavior.fun_robot_behavior[4],
        )
        self.robot_draw_pause_btn.place(x=1300, y=10)

        # ------狀態
        x_dis = 110
        word_label = tk.Label(
            tab_RobotControl, text="目前狀態 :", font=("Microsoft JhengHei", 12)
        )
        word_label.place(x=10, y=60)

        record_robot_status = tk.Entry(
            tab_RobotControl,
            width=16,
            textvariable=self.record_robot_status,
        )
        record_robot_status.place(x=10 + x_dis, y=60)

        word_label = tk.Label(
            tab_RobotControl, text="目前Block :", font=("Microsoft JhengHei", 12)
        )
        word_label.place(x=10 + 2 * x_dis, y=60)

        record_block_num = tk.Entry(
            tab_RobotControl,
            width=16,
            textvariable=self.record_block_num,
        )
        record_block_num.place(x=10 + 3 * x_dis, y=60)

        word_label = tk.Label(
            tab_RobotControl, text="目前Color :", font=("Microsoft JhengHei", 12)
        )
        word_label.place(x=10 + 4 * x_dis, y=60)

        record_color_num = tk.Entry(
            tab_RobotControl,
            width=16,
            textvariable=self.record_color_num,
        )
        record_color_num.place(x=10 + 5 * x_dis, y=60)

        word_label = tk.Label(
            tab_RobotControl, text="目前Conturs :", font=("Microsoft JhengHei", 12)
        )
        word_label.place(x=10 + 6 * x_dis, y=60)

        record_conturs_num = tk.Entry(
            tab_RobotControl,
            width=16,
            textvariable=self.record_conturs_num,
        )
        record_conturs_num.place(x=10 + 7 * x_dis, y=60)

        word_label = tk.Label(
            tab_RobotControl, text="目前Line :", font=("Microsoft JhengHei", 12)
        )
        word_label.place(x=10 + 8 * x_dis, y=60)

        record_line_num = tk.Entry(
            tab_RobotControl,
            width=16,
            textvariable=self.record_line_num,
        )
        record_line_num.place(x=10 + 9 * x_dis, y=60)

        # ------

        word_label = tk.Label(
            tab_RobotControl, text="動作測試 :", font=("Microsoft JhengHei", 12)
        )
        word_label.place(x=10, y=110)
        # 沾水
        self.robot_dig_water_btn = tk.Button(
            tab_RobotControl,
            text="沾水",
            width=36,
            command=self.common.RobotBehavior.fun_robot_behavior[5],
        )
        self.robot_dig_water_btn.place(x=100, y=110)
        # 沾衛生紙
        # self.robot_dig_issue_btn = tk.Button(tab_RobotControl, text='沾衛生紙', width=36, command=self.common.RobotBehavior.fun_robot_behavior[6])
        # self.robot_dig_issue_btn.place(x=100, y=110)
        # 沾主畫區
        self.robot_draw_block_btn = tk.Button(
            tab_RobotControl, text="主畫區測試", width=36, command=self.get_robot_main_test
        )
        self.robot_draw_block_btn.place(x=100, y=160)

        word_label = tk.Label(
            tab_RobotControl, text="X :", font=("Microsoft JhengHei", 12)
        )
        word_label.place(x=400, y=160)

        validate_cmd = tab_RobotControl.register(self.validate_entry)  # 注册一个验证函数
        validate_input_cmd = tab_RobotControl.register(
            self.validate_input
        )  # 注册一个输入验证函数

        self.robot_draw_block_Entry_x = tk.Entry(
            tab_RobotControl,
            width=32,
            validate="all",
            validatecommand=(validate_cmd, "%P"),
            invalidcommand=(validate_input_cmd, "%P"),
            textvariable=self.robot_draw_block_String_x,
        )
        self.robot_draw_block_Entry_x.place(x=430, y=165)

        word_label = tk.Label(
            tab_RobotControl, text="Y :", font=("Microsoft JhengHei", 12)
        )
        word_label.place(x=700, y=160)

        self.robot_draw_block_Entry_y = tk.Entry(
            tab_RobotControl,
            width=32,
            validate="all",
            validatecommand=(validate_cmd, "%P"),
            invalidcommand=(validate_input_cmd, "%P"),
            textvariable=self.robot_draw_block_String_y,
        )
        self.robot_draw_block_Entry_y.place(x=730, y=165)

        # 調色盤動作x12
        word_label = tk.Label(
            tab_RobotControl, text="色格測試 :", font=("Microsoft JhengHei", 12)
        )
        word_label.place(x=10, y=210)

        x_color = 100
        y_color = 210

        for i in range(0, 12):
            x_num = int(i % 4)
            y_num = int(i / 4)
            robot_pal_btn = tk.Button(
                tab_RobotControl,
                text=f"單色區塊 {i+1}",
                width=36,
                command=partial(self.common.RobotBehavior.fun_robot_behavior[7], i),
            )
            robot_pal_btn.place(x=x_color + 300 * x_num, y=y_color + 50 * y_num)
            self.robot_pal_color_btns.append(robot_pal_btn)

        # 調色盤主調色動作x4
        word_label = tk.Label(
            tab_RobotControl, text="調色測試 :", font=("Microsoft JhengHei", 12)
        )
        word_label.place(x=10, y=370)
        x_color = 100
        y_color = 370

        # TODO 錯誤  0,1是同一個X
        for j in range(0, 4):
            y_num = int(j % 2)
            x_num = int(j / 2)

            robot_pal_main_btn = tk.Button(
                tab_RobotControl,
                text=f"調色區塊 {j+1}",
                width=18,
                command=partial(self.common.RobotBehavior.fun_robot_behavior[8], j),
            )
            robot_pal_main_btn.place(x=x_color + 150 * x_num, y=y_color + 50 * y_num)
            self.robot_pal_main_btns.append(robot_pal_main_btn)

        word_label = tk.Label(
            tab_RobotControl, text="主盤取色測試 :", font=("Microsoft JhengHei", 12)
        )
        word_label.place(x=400, y=370)
        x_color = 520
        y_color = 370

        for j in range(0, 4):
            y_num = int(j % 2)
            x_num = int(j / 2)

            robot_pal_main_btn = tk.Button(
                tab_RobotControl,
                text=f"調色區塊 {j+1}",
                width=18,
                command=partial(self.common.RobotBehavior.fun_robot_behavior[12], j),
            )
            robot_pal_main_btn.place(x=x_color + 150 * x_num, y=y_color + 50 * y_num)
            self.robot_pal_main_btns.append(robot_pal_main_btn)

        word_label = tk.Label(
            tab_RobotControl, text="色盤是否符合目標顏色 :", font=("Microsoft JhengHei", 12)
        )
        word_label.place(x=820, y=370)

        robot_pal_main_btn = tk.Button(
            tab_RobotControl, text=f"判斷", width=18, command=self.fun_check_main_goal
        )
        robot_pal_main_btn.place(x=1010, y=370)

        word_label = tk.Label(
            tab_RobotControl, text="編號 :", font=("Microsoft JhengHei", 12)
        )
        word_label.place(x=1180, y=370)

        num = tk.Entry(
            tab_RobotControl,
            width=9,
            validate="all",
            validatecommand=(validate_cmd, "%P"),
            invalidcommand=(validate_input_cmd, "%P"),
            textvariable=self.main_num_color_check,
        )
        num.place(x=1230, y=375)

        word_label = tk.Label(
            tab_RobotControl, text="目標顏色 :", font=("Microsoft JhengHei", 12)
        )
        word_label.place(x=1310, y=370)

        color_goal = tk.Entry(
            tab_RobotControl, width=9, textvariable=self.main_color_goal_check
        )
        color_goal.place(x=1400, y=375)

        goal_check_block = tk.Frame(
            tab_RobotControl,
            width=650,
            height=30,
            highlightthickness=1,
            highlightbackground="black",
        )
        goal_check_block.place(x=820, y=410)

        self.main_color_check_result_label = tk.Label(
            goal_check_block,
            textvariable=self.main_color_check_result,
            font=("Microsoft JhengHei", 12),
        )
        self.main_color_check_result_label.place(x=1, y=1)

    def fun_tab_PicPC(self):
        word_label = tk.Label(
            self.tab_PicPC, text="線稿 :", font=("Microsoft JhengHei", 12)
        )
        word_label.place(x=10, y=5)

        self.picPc_ori_canvas = tk.Canvas(
            self.tab_PicPC,
            width=self.width_picPc_ori,
            height=self.width_picPc_ori,
            bg="gray",
            highlightthickness=1,
            highlightbackground="black",
        )
        self.picPc_ori_canvas.place(x=10, y=30)

        self.get_pic_ori_btn = tk.Button(
            self.tab_PicPC, text="線搞圖", width=36, command=self.get_pic_ori_draft
        )
        self.get_pic_ori_btn.place(x=10, y=590)

        self.get_pic_ori_bone_btn = tk.Button(
            self.tab_PicPC, text="查看線搞路徑", width=36, command=self.get_pic_ori_draft_bone
        )
        self.get_pic_ori_bone_btn.place(x=300, y=590)

        word_label = tk.Label(
            self.tab_PicPC, text="彩色上色圖 :", font=("Microsoft JhengHei", 12)
        )
        word_label.place(x=580, y=5)

        self.picPc_color_canvas = tk.Canvas(
            self.tab_PicPC,
            width=self.width_picPc_ori,
            height=self.width_picPc_ori,
            bg="gray",
            highlightthickness=1,
            highlightbackground="black",
        )
        self.picPc_color_canvas.place(x=580, y=30)

        self.get_pic_color_btn = tk.Button(
            self.tab_PicPC, text="彩色上色", width=36, command=self.get_pic_ori_colorful
        )
        self.get_pic_color_btn.place(x=580, y=590)

        word_label = tk.Label(
            self.tab_PicPC, text="分析後區塊", font=("Microsoft JhengHei", 12)
        )
        word_label.place(x=1140, y=5)

        self.block_box_blocks = tk.Listbox(
            self.tab_PicPC, width=61, height=10, highlightthickness=1, exportselection=0
        )
        self.block_box_blocks.place(x=1140, y=30)

        self.block_box_blocks.bind("<<ListboxSelect>>", self.on_select_block)

        self.picPc_color_block_canvas = tk.Canvas(
            self.tab_PicPC,
            width=250,
            height=250,
            bg="gray",
            highlightthickness=1,
            highlightbackground="black",
        )
        self.picPc_color_block_canvas.place(x=1140, y=210)

        self.colorful_box_blocks = tk.Listbox(
            self.tab_PicPC, width=24, height=25, highlightthickness=1, exportselection=0
        )
        self.colorful_box_blocks.place(x=1400, y=210)

        self.colorful_box_blocks.bind("<<ListboxSelect>>", self.on_select_color)

    def fun_tab_PicReal(self):
        self.get_ColorRealSize[0] = tk.StringVar()
        self.get_ColorRealSize[1] = tk.StringVar()
        self.get_ColorRealSize_start[0] = tk.StringVar()
        self.get_ColorRealSize_start[1] = tk.StringVar()
        self.rotaoteAngle = tk.StringVar()
        self.get_ColorRealSize[0].set(self.common.get_ColorRealSize[0])
        self.get_ColorRealSize[1].set(self.common.get_ColorRealSize[1])

        self.get_ColorRealSize_start[0].set(self.common.get_ColorRealSize_start[0])
        self.get_ColorRealSize_start[1].set(self.common.get_ColorRealSize_start[1])
        self.rotaoteAngle.set(self.common.rotaoteAngle)

        self.is_scale_512 = tk.BooleanVar()
        self.is_scale_512.set(self.common.is_scale_512)

        word_label = tk.Label(
            self.tab_PicReal, text="實際繪圖 :", font=("Microsoft JhengHei", 12)
        )
        word_label.place(x=10, y=5)

        self.picReal_canvas = tk.Canvas(
            self.tab_PicReal,
            width=self.width_picPc_ori,
            height=self.width_picPc_ori,
            bg="gray",
            highlightthickness=1,
            highlightbackground="black",
        )
        self.picReal_canvas.place(x=10, y=30)

        self.get_real_pic_btn = tk.Button(
            self.tab_PicReal, text="存檔", width=36, command=self.save_pic_real
        )
        self.get_real_pic_btn.place(x=10, y=590)

        self.get_real_pic_btn = tk.Button(
            self.tab_PicReal, text="比對繪畫結果", width=36, command=self.compare_pic_real
        )
        self.get_real_pic_btn.place(x=300, y=590)

        # 自定義修改欄位
        x_init = 580

        label_01 = tk.Label(self.tab_PicReal, text="影像數據設定 :")
        label_01.place(x=x_init, y=5)

        # 影像裁切
        label_01 = tk.Label(self.tab_PicReal, text="X :")
        label_01.place(x=x_init, y=30)

        Entry_Start = tk.Entry(
            self.tab_PicReal, width=6, textvariable=self.get_ColorRealSize_start[0]
        )
        Entry_Start.place(x=x_init + 20, y=30)

        label_01 = tk.Label(self.tab_PicReal, text="Y :")
        label_01.place(x=x_init + 75, y=30)

        Entry_End = tk.Entry(
            self.tab_PicReal, width=6, textvariable=self.get_ColorRealSize_start[1]
        )
        Entry_End.place(x=x_init + 95, y=30)

        label_01 = tk.Label(self.tab_PicReal, text="W :")
        label_01.place(x=x_init + 150, y=30)

        Entry_Width = tk.Entry(
            self.tab_PicReal, width=6, textvariable=self.get_ColorRealSize[0]
        )
        Entry_Width.place(x=x_init + 175, y=30)

        label_01 = tk.Label(self.tab_PicReal, text="H :")
        label_01.place(x=x_init + 230, y=30)

        Entry_Heigh = tk.Entry(
            self.tab_PicReal, width=6, textvariable=self.get_ColorRealSize[1]
        )
        Entry_Heigh.place(x=x_init + 250, y=30)

        label_01 = tk.Label(self.tab_PicReal, text="旋轉角度 :")
        label_01.place(x=x_init, y=60)

        Entry_rotaoteAngle = tk.Entry(
            self.tab_PicReal, width=6, textvariable=self.rotaoteAngle
        )
        Entry_rotaoteAngle.place(x=x_init + 60, y=60)

        label_01 = tk.Label(self.tab_PicReal, text="放大圖片 :")
        label_01.place(x=x_init, y=90)

        # create a Tkinter Checkbox
        checkbox = tk.Checkbutton(self.tab_PicReal, variable=self.is_scale_512)
        checkbox.place(x=x_init + 60, y=90)

    # 調色盤
    def fun_tab_ColorPalette(self):
        self.cam_Color_Pa_Start[0] = tk.StringVar()
        self.cam_Color_Pa_Start[1] = tk.StringVar()
        self.cam_Color_Pa_Size[0] = tk.StringVar()
        self.cam_Color_Pa_Size[1] = tk.StringVar()

        self.cam_Color_Cell_Start[0] = tk.StringVar()
        self.cam_Color_Cell_Start[1] = tk.StringVar()
        self.cam_Color_Cell_Size[0] = tk.StringVar()
        self.cam_Color_Cell_Size[1] = tk.StringVar()
        self.cam_Color_Cell_Offset[0] = tk.StringVar()
        self.cam_Color_Cell_Offset[1] = tk.StringVar()

        for i in range(0, len(self.cam_Color_Main_Start)):
            self.cam_Color_Main_Start[i][0] = tk.StringVar()
            self.cam_Color_Main_Start[i][1] = tk.StringVar()

        self.cam_Color_Main_Size[0] = tk.StringVar()
        self.cam_Color_Main_Size[1] = tk.StringVar()

        for i in range(0, len(self.cam_Color_Cell_info)):
            self.cam_Color_Cell_info[i] = tk.StringVar()
        for i in range(0, len(self.cam_Color_Cell_HSV_info)):
            self.cam_Color_Cell_HSV_info[i] = tk.StringVar()

        self.cam_Color_Main_Start_info[0] = tk.StringVar()
        self.cam_Color_Main_Start_info[1] = tk.StringVar()
        self.cam_Color_Main_Start_info[2] = tk.StringVar()
        self.cam_Color_Main_Start_info[3] = tk.StringVar()

        self.cam_Color_Main_Start_HSV_info[0] = tk.StringVar()
        self.cam_Color_Main_Start_HSV_info[1] = tk.StringVar()
        self.cam_Color_Main_Start_HSV_info[2] = tk.StringVar()
        self.cam_Color_Main_Start_HSV_info[3] = tk.StringVar()

        self.pal_contrast_string = tk.StringVar()
        self.pal_brightness_string = tk.StringVar()

        self.main_color_contrast_string = tk.StringVar()
        self.main_color_brightness_string = tk.StringVar()

        self.cam_Color_Pa_Start[0].set(self.common.get_ColorPaletteSize_start[0])
        self.cam_Color_Pa_Start[1].set(self.common.get_ColorPaletteSize_start[1])

        self.cam_Color_Pa_Size[0].set(self.common.get_ColorPaletteSize[0])
        self.cam_Color_Pa_Size[1].set(self.common.get_ColorPaletteSize[1])

        self.cam_Color_Cell_Start[0].set(self.common.PalCell_start[0])
        self.cam_Color_Cell_Start[1].set(self.common.PalCell_start[1])

        self.cam_Color_Cell_Size[0].set(self.common.PalCell[0])
        self.cam_Color_Cell_Size[1].set(self.common.PalCell[1])

        self.cam_Color_Cell_Offset[0].set(self.common.PalCell_offset[0])
        self.cam_Color_Cell_Offset[1].set(self.common.PalCell_offset[1])

        for i in range(0, len(self.common.Pal_main_start)):
            self.cam_Color_Main_Start[i][0].set(self.common.Pal_main_start[i][0])
            self.cam_Color_Main_Start[i][1].set(self.common.Pal_main_start[i][1])

        self.cam_Color_Main_Size[0].set(self.common.Pal_main[0])
        self.cam_Color_Main_Size[1].set(self.common.Pal_main[1])

        self.pal_contrast_string.set(self.common.pal_contrast)
        self.pal_brightness_string.set(self.common.pal_brightness)

        self.main_color_contrast_string.set(self.common.main_color_contrast)
        self.main_color_brightness_string.set(self.common.main_color_brightness)

        anay_para_setting_block = tk.Frame(
            self.tab_ColorPalette,
            width=840,
            height=200,
            highlightthickness=1,
            highlightbackground="black",
        )
        anay_para_setting_block.place(x=440, y=10)

        # 自定義修改欄位
        x_init = 10
        y_init = 5
        label_01 = tk.Label(anay_para_setting_block, text="影像數據設定 :")
        label_01.place(x=x_init, y=y_init)

        # 影像裁切
        label_01 = tk.Label(anay_para_setting_block, text="X :")
        label_01.place(x=x_init, y=y_init + 25)

        Entry_Start = tk.Entry(
            anay_para_setting_block, width=6, textvariable=self.cam_Color_Pa_Start[0]
        )
        Entry_Start.place(x=x_init + 20, y=y_init + 25)

        label_01 = tk.Label(anay_para_setting_block, text="Y :")
        label_01.place(x=x_init + 75, y=y_init + 25)

        Entry_End = tk.Entry(
            anay_para_setting_block, width=6, textvariable=self.cam_Color_Pa_Start[1]
        )
        Entry_End.place(x=x_init + 95, y=y_init + 25)

        label_01 = tk.Label(anay_para_setting_block, text="W :")
        label_01.place(x=x_init + 150, y=y_init + 25)

        Entry_Width = tk.Entry(
            anay_para_setting_block, width=6, textvariable=self.cam_Color_Pa_Size[0]
        )
        Entry_Width.place(x=x_init + 175, y=y_init + 25)

        label_01 = tk.Label(anay_para_setting_block, text="H :")
        label_01.place(x=x_init + 230, y=y_init + 25)

        Entry_Heigh = tk.Entry(
            anay_para_setting_block, width=6, textvariable=self.cam_Color_Pa_Size[1]
        )
        Entry_Heigh.place(x=x_init + 250, y=y_init + 25)

        # 單一裁切
        label_01 = tk.Label(anay_para_setting_block, text="單一顏色區塊擷取 :")
        label_01.place(x=x_init, y=y_init + 45)

        label_01 = tk.Label(anay_para_setting_block, text="X :")
        label_01.place(x=x_init, y=y_init + 75)

        Entry_Start = tk.Entry(
            anay_para_setting_block, width=6, textvariable=self.cam_Color_Cell_Start[0]
        )
        Entry_Start.place(x=x_init + 20, y=y_init + 75)

        label_01 = tk.Label(anay_para_setting_block, text="Y :")
        label_01.place(x=x_init + 75, y=y_init + 75)

        Entry_End = tk.Entry(
            anay_para_setting_block, width=6, textvariable=self.cam_Color_Cell_Start[1]
        )
        Entry_End.place(x=x_init + 95, y=y_init + 75)

        label_01 = tk.Label(anay_para_setting_block, text="W :")
        label_01.place(x=x_init + 150, y=y_init + 75)

        Entry_Width = tk.Entry(
            anay_para_setting_block, width=6, textvariable=self.cam_Color_Cell_Size[0]
        )
        Entry_Width.place(x=x_init + 175, y=y_init + 75)

        label_01 = tk.Label(anay_para_setting_block, text="H :")
        label_01.place(x=x_init + 230, y=y_init + 75)

        Entry_Heigh = tk.Entry(
            anay_para_setting_block, width=6, textvariable=self.cam_Color_Cell_Size[1]
        )
        Entry_Heigh.place(x=x_init + 250, y=y_init + 75)

        label_01 = tk.Label(anay_para_setting_block, text="Off_X :")
        label_01.place(x=x_init + 310, y=y_init + 75)

        Entry_Heigh = tk.Entry(
            anay_para_setting_block, width=6, textvariable=self.cam_Color_Cell_Offset[0]
        )
        Entry_Heigh.place(x=x_init + 350, y=y_init + 75)

        label_01 = tk.Label(anay_para_setting_block, text="Off_Y :")
        label_01.place(x=x_init + 380, y=y_init + 75)

        Entry_Heigh = tk.Entry(
            anay_para_setting_block, width=6, textvariable=self.cam_Color_Cell_Offset[1]
        )
        Entry_Heigh.place(x=x_init + 440, y=y_init + 75)

        # 主調色位置
        label_01 = tk.Label(anay_para_setting_block, text="調色主板位置 :")
        label_01.place(x=x_init, y=y_init + 95)

        label_01 = tk.Label(anay_para_setting_block, text="W :")
        label_01.place(x=x_init, y=y_init + 125)

        Entry_Width = tk.Entry(
            anay_para_setting_block, width=6, textvariable=self.cam_Color_Main_Size[0]
        )
        Entry_Width.place(x=x_init + 25, y=y_init + 125)

        label_01 = tk.Label(anay_para_setting_block, text="H :")
        label_01.place(x=x_init + 80, y=y_init + 125)

        Entry_Heigh = tk.Entry(
            anay_para_setting_block, width=6, textvariable=self.cam_Color_Main_Size[1]
        )
        Entry_Heigh.place(x=x_init + 105, y=y_init + 125)

        x_1 = y_init + 105

        for i in range(0, len(self.common.Pal_main_start)):
            x_1 = x_1 + 55

            label_01 = tk.Label(anay_para_setting_block, text=f"X{i+1} :")
            label_01.place(x=x_1, y=130)

            x_1 = x_1 + 25

            Entry_Start = tk.Entry(
                anay_para_setting_block,
                width=6,
                textvariable=self.cam_Color_Main_Start[i][0],
            )
            Entry_Start.place(x=x_1, y=130)

            x_1 = x_1 + 55

            label_01 = tk.Label(anay_para_setting_block, text=f"Y{i+1} :")
            label_01.place(x=x_1, y=130)

            x_1 = x_1 + 25

            Entry_End = tk.Entry(
                anay_para_setting_block,
                width=6,
                textvariable=self.cam_Color_Main_Start[i][1],
            )
            Entry_End.place(x=x_1, y=130)

        self.camreal_canvas = tk.Canvas(
            self.tab_ColorPalette,
            width=self.common.get_ColorPaletteSize[0],
            height=self.common.get_ColorPaletteSize[1],
            highlightthickness=1,
            highlightbackground="black",
        )
        self.camreal_canvas.place(x=10, y=10)

        r_x_start = 0
        r_y_start = 0

        anay_videos_block = tk.Frame(
            self.tab_ColorPalette,
            width=self.common.get_ColorPaletteSize[0] * 2,
            height=self.common.get_ColorPaletteSize[1] + 20,
            highlightthickness=1,
            highlightbackground="black",
        )
        anay_videos_block.place(x=10, y=220)

        for i in range(0, len(self.common.Color_Cells)):
            canvas = tk.Canvas(
                anay_videos_block,
                width=self.common.PalCell[0],
                height=self.common.PalCell[1],
                highlightthickness=1,
                highlightbackground="black",
            )

            x_row = int(i % 4)
            y_row = int(i / 4)

            r_x_start = (
                10
                + int(self.common.PalCell_offset[0] + 60) * x_row
                + int(self.common.PalCell_start[0])
                + x_row * 10
                + x_row * int(self.common.PalCell[0])
            )
            r_y_start = (
                10
                + int(self.common.PalCell_offset[1] + 10) * y_row
                + int(self.common.PalCell_start[1])
                + y_row * 10
                + y_row * int(self.common.PalCell[1])
            )

            label_01 = tk.Label(
                anay_videos_block, textvariable=self.cam_Color_Cell_info[i]
            )
            label_01.place(x=r_x_start + 28, y=r_y_start)

            label_01 = tk.Label(
                anay_videos_block, textvariable=self.cam_Color_Cell_HSV_info[i]
            )
            label_01.place(x=r_x_start + 28, y=r_y_start + 20)

            canvas.place(x=r_x_start, y=r_y_start)
            self.camreal_canvas_anyaize.append(canvas)

        # 計算 main 位置
        main_x_1_cal = (
            250
            + int(self.common.PalCell_offset[0] + 10) * 4
            + int(self.common.PalCell_start[0])
            + 4 * 10
            + 4 * int(self.common.PalCell[0])
        )
        main_x_2_cal = main_x_1_cal + int(self.common.PalCell_offset[0] + 10) * 6
        main_y_1_cal = 30 + int(self.common.PalCell_start[1])
        main_y_2_cal = (
            5
            + int(self.common.PalCell_offset[1]) * 2
            + int(self.common.PalCell_start[1])
            + 2 * 10
            + 2 * int(self.common.PalCell[1])
        )

        for i in range(0, len(self.common.Color_Mains)):
            r_x_start = main_x_1_cal
            r_y_start = main_y_1_cal

            if int(i / 2) == 0:
                r_x_start = main_x_1_cal
            else:
                r_x_start = main_x_2_cal

            if int(i % 2) == 0:
                r_y_start = main_y_1_cal
            else:
                r_y_start = main_y_2_cal

            label_01 = tk.Label(
                anay_videos_block, textvariable=self.cam_Color_Main_Start_info[i]
            )
            label_01.place(x=r_x_start + 60, y=r_y_start)

            label_01 = tk.Label(
                anay_videos_block, textvariable=self.cam_Color_Main_Start_HSV_info[i]
            )
            label_01.place(x=r_x_start + 60, y=r_y_start + 20)

            canvas = tk.Canvas(
                anay_videos_block,
                width=self.common.Pal_main[0],
                height=self.common.Pal_main[1],
                highlightthickness=1,
                highlightbackground="black",
            )

            canvas.place(x=r_x_start, y=r_y_start)

            self.camreal_main_canvas_anyaize.append(canvas)

        img_setting_block = tk.Frame(
            self.tab_ColorPalette,
            width=425,
            height=220,
            highlightthickness=1,
            highlightbackground="black",
        )
        img_setting_block.place(x=855, y=220)

        label_01 = tk.Label(img_setting_block, text="色格設定 :")
        label_01.place(x=10, y=10)

        label_01 = tk.Label(img_setting_block, text="對比 :")
        label_01.place(x=10, y=35)

        pal_contrast = tk.Entry(
            img_setting_block, width=6, textvariable=self.pal_contrast_string
        )
        pal_contrast.place(x=50, y=35)

        label_01 = tk.Label(img_setting_block, text="亮度 :")
        label_01.place(x=110, y=35)

        pal_brightness = tk.Entry(
            img_setting_block, width=6, textvariable=self.pal_brightness_string
        )
        pal_brightness.place(x=150, y=35)

        label_01 = tk.Label(img_setting_block, text="主色盤設定 :")
        label_01.place(x=10, y=65)

        label_01 = tk.Label(img_setting_block, text="對比 :")
        label_01.place(x=10, y=95)

        pal_contrast = tk.Entry(
            img_setting_block, width=6, textvariable=self.main_color_contrast_string
        )
        pal_contrast.place(x=50, y=95)

        label_01 = tk.Label(img_setting_block, text="亮度 :")
        label_01.place(x=110, y=95)

        pal_brightness = tk.Entry(
            img_setting_block, width=6, textvariable=self.main_color_brightness_string
        )
        pal_brightness.place(x=150, y=95)

    def fun_check_main_goal(self):
        self.common.main_color_check_num = self.main_num_color_check.get()
        self.common.main_color_check_goal = self.main_color_goal_check.get()
        (
            isMatch_goal,
            goal_system_num,
            goal_system_pos,
            main_system_num,
            main_system_pos,
        ) = self.common.RobotBehavior.isMatch_goal_color(
            int(self.common.main_color_check_num), self.common.main_color_check_goal
        )

        result = f"達到目標:{isMatch_goal}-目標色系:{goal_system_num},位置:{goal_system_pos}-色盤色系:{main_system_num},位置:{main_system_pos}"
        self.main_color_check_result.set(result)

    def updateWindow(self):
        while self.common.updateWindow_bool:
            self.photo_plant, self.photo_real = self.common.OPENCV_Analyze.get_frame()
            if self.photo_plant is not None:
                # height = len(self.photo_plant)
                width1 = self.photo_plant.width()
                height1 = self.photo_plant.height()
                self.camreal_canvas.create_image(
                    0, 0, image=self.photo_plant, anchor=tk.NW
                )
                self.camreal_canvas.config(width=width1, height=height1)
            if self.photo_real is not None:
                self.picReal_canvas.create_image(
                    0, 0, image=self.photo_real, anchor=tk.NW
                )

            if len(self.common.Color_Cells) > 0:
                for i in range(0, len(self.common.Color_Cells)):
                    self.camreal_canvas_anyaize[i].create_image(
                        0, 0, image=self.common.Color_Cells[i].Image, anchor=tk.NW
                    )

            if len(self.common.Color_Mains) > 0:
                for i in range(0, len(self.common.Color_Mains)):
                    self.camreal_main_canvas_anyaize[i].create_image(
                        0, 0, image=self.common.Color_Mains[i].Image, anchor=tk.NW
                    )

            # 調色盤參數
            self.common.get_ColorPaletteSize_start[0] = self.cam_Color_Pa_Start[0].get()
            self.common.get_ColorPaletteSize_start[1] = self.cam_Color_Pa_Start[1].get()

            self.common.get_ColorPaletteSize[0] = self.cam_Color_Pa_Size[0].get()
            self.common.get_ColorPaletteSize[1] = self.cam_Color_Pa_Size[1].get()

            self.common.PalCell_start[0] = self.cam_Color_Cell_Start[0].get()
            self.common.PalCell_start[1] = self.cam_Color_Cell_Start[1].get()

            self.common.PalCell[0] = self.cam_Color_Cell_Size[0].get()
            self.common.PalCell[1] = self.cam_Color_Cell_Size[1].get()

            self.common.PalCell_offset[0] = self.cam_Color_Cell_Offset[0].get()
            self.common.PalCell_offset[1] = self.cam_Color_Cell_Offset[1].get()

            for i in range(0, len(self.cam_Color_Main_Start)):
                self.common.Pal_main_start[i][0] = self.cam_Color_Main_Start[i][0].get()
                self.common.Pal_main_start[i][1] = self.cam_Color_Main_Start[i][1].get()

            self.common.Pal_main[0] = self.cam_Color_Main_Size[0].get()
            self.common.Pal_main[1] = self.cam_Color_Main_Size[1].get()

            for i in range(0, len(self.common.Color_Mains)):
                if len(self.common.Color_Mains[i].HSV_Main) > 0:
                    self.cam_Color_Main_Start_info[i].set(
                        self.common.Color_Mains[i].Color_Pre
                    )
                    hsv = f"{i}-({self.common.Color_Mains[i].HSV_Main[0]},{self.common.Color_Mains[i].HSV_Main[1]},{self.common.Color_Mains[i].HSV_Main[2]})"
                    self.cam_Color_Main_Start_HSV_info[i].set(hsv)

            for i in range(0, len(self.common.Color_Cells)):
                if len(self.common.Color_Cells[i].HSV_Main) > 0:
                    self.cam_Color_Cell_info[i].set(
                        self.common.Color_Cells[i].Color_Pre
                    )
                    hsv = f"({self.common.Color_Cells[i].HSV_Main[0]},{self.common.Color_Cells[i].HSV_Main[1]},{self.common.Color_Cells[i].HSV_Main[2]})"
                    self.cam_Color_Cell_HSV_info[i].set(hsv)

            self.common.pal_contrast = int(self.pal_contrast_string.get())
            self.common.pal_brightness = int(self.pal_brightness_string.get())

            self.common.main_color_contrast = int(self.main_color_contrast_string.get())
            self.common.main_color_brightness = int(
                self.main_color_brightness_string.get()
            )

            self.common.get_ColorRealSize[0] = self.get_ColorRealSize[0].get()
            self.common.get_ColorRealSize[1] = self.get_ColorRealSize[1].get()
            self.common.get_ColorRealSize_start[0] = self.get_ColorRealSize_start[
                0
            ].get()
            self.common.get_ColorRealSize_start[1] = self.get_ColorRealSize_start[
                1
            ].get()
            self.common.rotaoteAngle = int(self.rotaoteAngle.get())
            self.common.is_scale_512 = self.is_scale_512.get()

            self.common.main_color_check_num = self.main_num_color_check.get()
            self.common.main_color_check_goal = self.main_color_goal_check.get()

            # self.common.record_robot_status = self.record_robot_status.get()
            # self.common.record_block_num = self.record_block_num.get()
            # self.common.record_color_num = self.record_color_num.get()
            # self.common.record_conturs_num = self.record_conturs_num.get()
            # self.common.record_line_num = self.record_line_num.get()
            # self.common.record_pen_num = self.record_pen_num.get()
            self.record_block_num.set(self.common.record_block_num)
            self.record_color_num.set(self.common.record_color_num)
            self.record_conturs_num.set(self.common.record_conturs_num)
            self.record_line_num.set(self.common.record_line_num)
            self.record_pen_num.set(self.common.record_pen_num)
            self.record_robot_status.set(self.common.record_robot_status)
            time.sleep(0.13)

            if self.common.updateWindow_bool == False:  # 檢查旗標
                break

    def on_closing(self):
        self.common.updateWindow_bool = False

        # 釋放該攝影機裝置
        self.common.OPENCV_Analyze.cap_release()

        self.window.destroy()

    def create_window(self):
        self.window = tk.Tk()
        self.window.title("手臂視窗")

        panel_tab = tk.Frame(
            self.window, width=self.window_width, height=self.window_height
        )
        panel_tab.grid(row=0, column=1, sticky="ns")

        tabsystem = ttk.Notebook(panel_tab)

        self.tab_RobotControl = tk.Frame(
            tabsystem, width=self.window_width, height=self.window_height
        )
        self.tab_PicPC = tk.Frame(
            tabsystem, width=self.window_width, height=self.window_height
        )
        self.tab_PicReal = tk.Frame(
            tabsystem, width=self.window_width, height=self.window_height
        )
        self.tab_ColorPalette = tk.Frame(
            tabsystem, width=self.window_width, height=self.window_height
        )

        tabsystem.add(self.tab_RobotControl, text="手臂控制")
        tabsystem.add(self.tab_PicPC, text="電腦圖片分析")
        tabsystem.add(self.tab_PicReal, text="圖紙分析")
        tabsystem.add(self.tab_ColorPalette, text="調色盤分析")
        tabsystem.pack(expand=1, fill="both")

        self.fun_tab_RobotControl()
        self.fun_tab_PicPC()
        self.fun_tab_PicReal()
        self.fun_tab_ColorPalette()

        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

        # self.updateWindow()

        self.common.threading_updateUI = threading.Thread(target=self.updateWindow)
        self.common.threading_updateUI.setDaemon(True)
        self.common.threading_updateUI.start()

        self.window.mainloop()
