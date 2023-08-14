from pymycobot.ultraArm import ultraArm
import time
import datetime
import threading
from models import pen, line, block_color


# function :
# Active_Water_Dip_p_center
# Active_Water_Dip
# active_Colorful_Main
# active_Draft
# active_Main
# Active_ColorDip
# Active_ColorDip_center
# Active_ColorMainMixing
class RobotBehavior:
    def __init__(self):
        # 手臂
        # 沾顏料 x12
        # 調色 x 4
        # 洗筆
        # 沾衛生紙

        # 繪圖
        #  - 圖
        #  - 區塊
        #    - 顏色區塊(線段組)
        #    - 未畫區塊(線段組)
        #      - 線段(畫筆組)
        #        - 畫筆(預備點(up) - 繪畫點 -結束點(up))
        #  - 線段黑線(畫筆組)
        #        - 畫筆(預備點(up) - 繪畫點 -結束點(up))

        #  - 停止運動(補充顏料、清除調色盤、更換清水、更換衛生紙)

        self.mc = None
        self.common = None

        self.fun_robot_behavior = []

        self.fun_robot_behavior.append(self.Active_Init)
        self.fun_robot_behavior.append(self.Active_Start)
        self.fun_robot_behavior.append(self.Active_Restart)
        self.fun_robot_behavior.append(self.Active_Stop)
        self.fun_robot_behavior.append(self.Active_Pause)
        self.fun_robot_behavior.append(self.Active_ColorClearTest)
        self.fun_robot_behavior.append(self.Active_ToiletDipTest)
        self.fun_robot_behavior.append(self.Active_ColorDipTest)
        self.fun_robot_behavior.append(self.Active_ColorMixingTest)
        self.fun_robot_behavior.append(self.Active_MainTest)
        self.fun_robot_behavior.append(self.Active_DraftTest)
        self.fun_robot_behavior.append(self.Active_ColorfulTest)
        self.fun_robot_behavior.append(self.Active_ColorMainTest)  # 主盤沾水
        self.fun_robot_behavior.append(self.Active_Colorful_MainTest)  # 主盤沾色(全過程)

    def get_Common(self, CommonOb):
        self.common = CommonOb

    # 主思考
    # 給與區塊線段以後
    # 判斷主顏色x4 是否可調?(可)
    # 沾水
    # 沾衛生紙
    # 沾色(一次)
    # 放置主顏色某一調色
    # 離開
    # 鏡頭判斷符合顏色
    # 不符合
    #    - 沾水、沾衛生紙、沾色、放置原先主顏色調色、離開、鏡頭判斷符合顏色
    #   符合
    #    - 繪圖
    #    - 是否有顏色(直接用數量判斷 )
    #         -沾顏料 不沾顏料

    # 機器人執行線程啟動--pars為參數，如果沒有就不帶入
    # pars 規格為json,{key:vale}
    def Thread_Active(self, active_function, pars=None):
        if pars == None:
            self.common.threading_robot_Move = threading.Thread(target=active_function)
        else:
            # pars 不做處理，直接帶入
            self.common.threading_robot_Move = threading.Thread(
                target=active_function, kwargs=pars
            )
        self.common.threading_robot_Move.setDaemon(True)
        self.common.threading_robot_Move.start()

    def Thead_ForceStop(self):
        self.common.stop_thread(self.common.threading_robot_Move)

    def Check_thread_alive(self):
        if (
            self.common.threading_robot_Move is not None
            and self.common.threading_robot_Move.is_alive()
        ):
            print("尚未停止")
            return True

        return False

    def Active_Init(self):
        if self.Check_thread_alive():
            return

        self.Thread_Active(active_function=self.active_Init, pars={"need_Stop": True})

    def active_Init(self, need_Stop):
        print(f"check----------------Active_Init")

        self.Robot_Status_Change(self.common.status_robot["None"])

        if self.mc == None:
            self.mc = ultraArm(self.common.COM, 115200)
        self.mc.go_zero()
        self.mc.set_mode(0)
        coords = self.mc.get_coords_info()
        time.sleep(2)
        print(coords)

        if need_Stop == True:
            self.Thead_ForceStop()

    # START繪圖
    def Active_Start(self):
        print(f"check----------------Active_Start")
        self.Active_RecordInit()
        self.Active_Main()

    # RESTART繪圖--重新啟動，紀錄還在
    def Active_Restart(self):
        print(f"check----------------Active_Restart")
        self.Active_Main()

    # STOP繪圖
    def Active_Stop(self):
        print(f"check----------------Active_Stop")
        self.Thead_ForceStop()
        self.Active_RecordInit()

    # Pause繪圖
    def Active_Pause(self):
        print(f"check----------------Active_Pause")
        self.Thead_ForceStop()

    # 洗筆
    def Active_ColorClearTest(self):
        if self.Check_thread_alive():
            return

        self.Thread_Active(active_function=self.active_ColorClearTest)

    def active_ColorClearTest(self):
        last_status = self.common.status_robotTest_now

        if (
            self.common.status_robotTest_now
            != self.common.status_robotTest["Dig_Water"]
        ):
            self.common.status_robotTest_now = self.common.status_robotTest["Dig_Water"]

            if (
                last_status != self.common.status_robotTest["Dig_Water"]
                and last_status != self.common.status_robotTest["Dig_Issue"]
            ):
                self.Active_Water_Dip_p_center()

        self.Active_Water_Dip()
        self.Thead_ForceStop()

    def Active_Water_Dip_p_center(self):
        if self.common.is_ignore_active == True:
            return

        self.mc.set_coords(self.common.center_p_Dig, 90)
        time.sleep(0.7)

    def Active_Water_Dip(self):
        print(f"check----------------Active_ColorClear")

        if self.common.is_ignore_active == True:
            return

        wait = 1

        x = self.common.border_DigWater[0][0]
        y = self.common.border_DigWater[0][1]
        z = -10

        self.mc.set_coords([x, y, z], 60)
        time.sleep(wait)

        # 旋轉4次
        wait = 0.15
        for i in range(0, 1):
            x = self.common.border_DigWater[0][0] + 6
            y = self.common.border_DigWater[0][1]
            z = self.common.border_DigWater[0][2] - 3

            self.mc.set_coords([x, y, z], 70)
            time.sleep(wait)

            x = self.common.border_DigWater[0][0]
            y = self.common.border_DigWater[0][1] + 6
            z = self.common.border_DigWater[0][2] - 3

            self.mc.set_coords([x, y, z], 70)
            time.sleep(wait)

            x = self.common.border_DigWater[0][0] - 6
            y = self.common.border_DigWater[0][1]
            z = self.common.border_DigWater[0][2] - 3

            self.mc.set_coords([x, y, z], 70)
            time.sleep(wait)

            # x = self.common.border_DigWater[0][0]
            # y = self.common.border_DigWater[0][1] -6
            # z = self.common.border_DigWater[0][2]

            # self.mc.set_coords([x,y,z], 70)
            # time.sleep(wait)

            wait = 0.8

        for j in range(0, 2):
            # 擦拭二角
            for i in range(0, 2):
                x = self.common.border_DigWater[0][0]
                y = self.common.border_DigWater[0][1]
                z = self.common.border_DigWater[0][2] - 3

                self.mc.set_coords([x, y, z], 40)
                time.sleep(wait)

                wait = 0.15

                x = self.common.border_DigWater[1][0] + 8
                y = self.common.border_DigWater[1][1] + 8
                z = self.common.border_DigWater[0][2]

                # 水里
                self.mc.set_coords([x, y, z], 60)
                time.sleep(wait)

                wait = 0.25

                x = self.common.border_DigWater[1][0] + 5
                y = self.common.border_DigWater[1][1] + 5
                z = self.common.border_DigWater[1][2]

                # 水里
                self.mc.set_coords([x, y, z], 60)
                time.sleep(wait)

                # 中
                self.mc.set_coords(self.common.border_DigWater[1], 40)
                time.sleep(wait)

                # 往上
                x = self.common.border_DigWater[1][0] - 4
                y = self.common.border_DigWater[1][1] - 4
                z = self.common.border_DigWater[1][2] + 5

                # 最後更高
                if i == 1:
                    z = self.common.border_DigWater[1][2] + 8

                self.mc.set_coords([x, y, z], 60)
                time.sleep(wait)

                # 往內(同高)
                x = self.common.border_DigWater[1][0] + 5
                y = self.common.border_DigWater[1][1] + 5
                z = self.common.border_DigWater[1][2] + 9

                self.mc.set_coords([x, y, z], 60)
                time.sleep(wait)

            for i in range(0, 2):
                x = self.common.border_DigWater[0][0]
                y = self.common.border_DigWater[0][1]
                z = self.common.border_DigWater[0][2] - 3

                self.mc.set_coords([x, y, z], 40)
                time.sleep(wait)

                wait = 0.15

                x = self.common.border_DigWater[2][0] - 6
                y = self.common.border_DigWater[2][1] - 8
                z = self.common.border_DigWater[0][2]

                # 水里
                self.mc.set_coords([x, y, z], 60)
                time.sleep(wait)

                wait = 0.25
                x = self.common.border_DigWater[2][0] - 4
                y = self.common.border_DigWater[2][1] - 4
                z = self.common.border_DigWater[2][2]
                self.mc.set_coords([x, y, z], 60)
                time.sleep(wait)

                self.mc.set_coords(self.common.border_DigWater[2], 20)
                time.sleep(wait)

                x = self.common.border_DigWater[2][0] + 6
                y = self.common.border_DigWater[2][1] + 6
                z = self.common.border_DigWater[2][2] + 4
                self.mc.set_coords([x, y, z], 60)
                time.sleep(wait)

                wait = 0.3
                x = self.common.border_DigWater[2][0] - 4
                y = self.common.border_DigWater[2][1] - 4
                z = self.common.border_DigWater[2][2] + 9
                self.mc.set_coords([x, y, z], 60)
                time.sleep(wait)

            for i in range(0, 2):
                x = self.common.border_DigWater[0][0]
                y = self.common.border_DigWater[0][1]
                z = self.common.border_DigWater[0][2] - 3

                self.mc.set_coords([x, y, z], 40)
                time.sleep(wait)

                wait = 0.15

                x = self.common.border_DigWater[3][0] - 8
                y = self.common.border_DigWater[3][1] + 8
                z = self.common.border_DigWater[0][2]

                # 水里
                self.mc.set_coords([x, y, z], 60)
                time.sleep(wait)

                wait = 0.25

                x = self.common.border_DigWater[3][0] - 5
                y = self.common.border_DigWater[3][1] + 5
                z = self.common.border_DigWater[3][2]

                # 水里
                self.mc.set_coords([x, y, z], 60)
                time.sleep(wait)

                # 中
                self.mc.set_coords(self.common.border_DigWater[3], 40)
                time.sleep(wait)

                # 往上
                x = self.common.border_DigWater[3][0] + 4
                y = self.common.border_DigWater[3][1] - 4
                z = self.common.border_DigWater[3][2] + 5

                # 最後更高
                if i == 1:
                    z = self.common.border_DigWater[3][2] + 8

                self.mc.set_coords([x, y, z], 60)
                time.sleep(wait)

                # 往內(同高)
                x = self.common.border_DigWater[3][0] - 5
                y = self.common.border_DigWater[3][1] + 5
                z = self.common.border_DigWater[3][2] + 9

                self.mc.set_coords([x, y, z], 60)
                time.sleep(wait)

        wait = 0.6
        x = self.common.border_DigWater[0][0]
        y = self.common.border_DigWater[0][1]
        z = -8
        self.mc.set_coords([x, y, z], 60)
        time.sleep(wait)

    # 沾衛生紙
    def Active_ToiletDipTest(self):
        if self.Check_thread_alive():
            return

        self.Thread_Active(active_function=self.active_ToiletDipTest)

    def active_ToiletDipTest(self):
        last_status = self.common.status_robotTest_now

        if (
            self.common.status_robotTest_now
            != self.common.status_robotTest["Dig_Issue"]
        ):
            self.common.status_robotTest_now = self.common.status_robotTest["Dig_Issue"]

            if (
                last_status != self.common.status_robotTest["Dig_Water"]
                and last_status != self.common.status_robotTest["Dig_Issue"]
            ):
                self.Active_Water_Dip_p_center()

        self.Active_Paper_Dip()
        self.Thead_ForceStop()

    def Active_Paper_Dip(self):
        print(f"check----------------Active_ToiletDip")

        # 下方往前
        x = self.common.border_DigIssue[0][0]
        y = self.common.border_DigIssue[0][1]
        z = -16

        self.mc.set_coords([x, y, z], 50)
        time.sleep(1)

        # 下方往後
        x = self.common.border_DigIssue[0][0]
        y = self.common.border_DigIssue[0][1]
        z = self.common.border_DigIssue[0][2]

        self.mc.set_coords([x, y, z], 50)
        time.sleep(0.5)

        # 下方往後1-左
        x = self.common.border_DigIssue[0][0]
        y = self.common.border_DigIssue[0][1] - 4
        z = self.common.border_DigIssue[0][2]

        self.mc.set_coords([x, y, z], 50)
        time.sleep(0.5)

        # 下方往後2-左上
        x = self.common.border_DigIssue[0][0]
        y = self.common.border_DigIssue[0][1] - 4
        z = self.common.border_DigIssue[0][2] + 3

        self.mc.set_coords([x, y, z], 50)
        time.sleep(0.5)

        # 下方往後
        x = self.common.border_DigIssue[0][0]
        y = self.common.border_DigIssue[0][1]
        z = self.common.border_DigIssue[0][2]

        self.mc.set_coords([x, y, z], 50)
        time.sleep(0.5)

        # 下方往後-右
        x = self.common.border_DigIssue[0][0]
        y = self.common.border_DigIssue[0][1] + 4
        z = self.common.border_DigIssue[0][2]

        self.mc.set_coords([x, y, z], 50)
        time.sleep(0.5)

        # 下方往後-右上
        x = self.common.border_DigIssue[0][0]
        y = self.common.border_DigIssue[0][1] + 4
        z = self.common.border_DigIssue[0][2] + 3

        self.mc.set_coords([x, y, z], 50)
        time.sleep(0.5)

        # 下方往後
        x = self.common.border_DigIssue[0][0]
        y = self.common.border_DigIssue[0][1]
        z = self.common.border_DigIssue[0][2]

        self.mc.set_coords([x, y, z], 50)
        time.sleep(0.5)

        # 下方往前
        x = self.common.border_DigIssue[0][0]
        y = self.common.border_DigIssue[0][1]
        z = -16

        self.mc.set_coords([x, y, z], 50)
        time.sleep(0.6)

    # 沾色
    def Active_ColorDipTest(self, Dip_Num):
        if self.Check_thread_alive():
            return

        self.Thread_Active(
            active_function=self.active_ColorDipTest, pars={"Dip_Num": Dip_Num}
        )

    def active_ColorDipTest(self, Dip_Num):
        print(f"check----------------Active_ColorDip- {Dip_Num}")

        if (
            self.common.status_robotTest_now
            != self.common.status_robotTest["Color_mixing"]
        ):
            self.common.status_robotTest_now = self.common.status_robotTest[
                "Color_mixing"
            ]
            self.Active_ColorDip_center()

        self.Active_ColorDip(Dip_Num, border_clear=True)
        self.Thead_ForceStop()

    def Active_ColorDip(self, Dip_Num, border_clear=True, layer=-1):
        if self.common.is_ignore_active == True:
            return

        z_down = -39
        if layer > 0:
            z_down = self.common.down_Palette[0] - (
                abs(self.common.down_Palette[1] - self.common.down_Palette[0])
                * (layer / 3)
            )
        elif layer == -99:
            z_down = self.common.down_Palette[1]

        x1 = self.common.border_Palette[Dip_Num][0]
        y1 = self.common.border_Palette[Dip_Num][1] + 4
        z1 = self.common.up_Palette

        x2 = self.common.border_Palette[Dip_Num][0]
        y2 = self.common.border_Palette[Dip_Num][1] + 2
        z2 = z_down

        x3 = self.common.border_Palette[Dip_Num][0]
        y3 = self.common.border_Palette[Dip_Num][1] - 1
        z3 = z_down

        x4 = self.common.border_Palette[Dip_Num][0]
        y4 = self.common.border_Palette[Dip_Num][1] - 3.5
        z4 = self.common.up_Palette

        # #移動到點上1
        self.mc.set_coords([x1, y1, z1], 50)
        time.sleep(1)

        # #移動到點下2

        self.mc.set_coords([x2, y2, z2], 20)
        time.sleep(0.6)

        # #移動到點下3
        self.mc.set_coords([x3, y3, z3], 20)
        time.sleep(0.6)

        # 往邊角擦拭
        if border_clear == True:
            print(f"往邊角擦")
            # 移動到點邊
            self.mc.set_coords([x3, y3 - 10, z3 + 2], 30)
            time.sleep(0.5)

            # 移動到上面
            self.mc.set_coords([x4, y3 - 11, z4], 20)
            time.sleep(0.5)
        else:
            # #移動到點上3
            self.mc.set_coords([x4, y4, z4], 20)
            time.sleep(0.5)

    def Active_ColorDip_center(self):
        if self.common.is_ignore_active == True:
            return

        # 沾色中間主點
        self.mc.set_coords(self.common.center_p_Palette, 40)
        time.sleep(2)

    def Active_Main_center(self):
        if self.common.is_ignore_active == True:
            return

        # 沾色中間主點
        self.mc.set_coords(self.common.center_main, 40)
        time.sleep(1)

    # 調色
    def Active_ColorMixingTest(self, Mixing_Num):
        if self.Check_thread_alive():
            return

        self.Thread_Active(
            active_function=self.Active_ColorMainMixing, pars={"Mixing_Num": Mixing_Num}
        )

    def Active_ColorMainTest(self, Mixing_Num):
        if (
            self.common.status_robotTest_now
            != self.common.status_robotTest["Color_mixing"]
        ):
            self.common.status_robotTest_now = self.common.status_robotTest[
                "Color_mixing"
            ]
            self.Active_ColorDip_center()

        self.Active_ColorMainMixing(Mixing_Num)
        self.Thead_ForceStop()

    def Active_ColorMainTest(self, Mixing_Num):
        if self.Check_thread_alive():
            return

        self.Thread_Active(
            active_function=self.active_ColorMainTest, pars={"Mixing_Num": Mixing_Num}
        )

    def active_ColorMainTest(self, Mixing_Num):
        if (
            self.common.status_robotTest_now
            != self.common.status_robotTest["Dig_Color"]
        ):
            self.common.status_robotTest_now = self.common.status_robotTest["Dig_Color"]
            self.Active_ColorDip_center()

        self.Active_Color_MainDip(Mixing_Num)
        self.Thead_ForceStop()

    # Main Color_Mix
    def Active_ColorMainMixing(self, Mixing_Num):
        print(f"check----------------Active_ColorMixing- {Mixing_Num}")
        # 中間主點

        if self.common.is_ignore_active == True:
            return

        x_once_step = 2
        y_border = 8.5
        wait_sed = 0.8
        firt_speed = 82
        z_up = self.common.up_Palette
        z_down = self.common.border_Palette_Main[Mixing_Num][2]

        # # 往前
        for i in range(0, 8):
            x_setp = self.common.border_Palette_Main[Mixing_Num][0] - i * x_once_step
            y_setp = self.common.border_Palette_Main[Mixing_Num][1] + y_border
            if i % 2 == 1:
                y_setp = self.common.border_Palette_Main[Mixing_Num][1] - y_border

            # 高
            x = x_setp
            y = y_setp
            z = z_up

            self.mc.set_coords([x, y, z], firt_speed)
            time.sleep(wait_sed)
            # 低1

            wait_sed = 0.1
            firt_speed = 82

            y_setp = self.common.border_Palette_Main[Mixing_Num][1] + y_border
            if i % 2 == 1:
                y_setp = self.common.border_Palette_Main[Mixing_Num][1] - y_border

            x = x_setp
            y = y_setp
            z = z_down

            self.mc.set_coords([x, y, z], firt_speed)
            time.sleep(wait_sed)

            # 低2 (往右划)
            x_setp = (
                self.common.border_Palette_Main[Mixing_Num][0] - (i + 1) * x_once_step
            )

            y_setp = self.common.border_Palette_Main[Mixing_Num][1] - y_border
            if i % 2 == 1:
                y_setp = self.common.border_Palette_Main[Mixing_Num][1] + y_border

            x = x_setp
            y = y_setp
            z = z_down

            self.mc.set_coords([x, y, z], firt_speed)
            time.sleep(wait_sed)

            # 高2 抬高
            y_setp = self.common.border_Palette_Main[Mixing_Num][1] - y_border
            if i % 2 == 1:
                y_setp = self.common.border_Palette_Main[Mixing_Num][1] + y_border

            x = x_setp
            y = y_setp
            z = z_up

            self.mc.set_coords([x, y, z], firt_speed)
            time.sleep(wait_sed)

        firt_speed = 82
        wait_sed = 0.1
        # # 往後
        for i in range(0, 6):
            i = 8 - i

            x_setp = self.common.border_Palette_Main[Mixing_Num][0] - i * x_once_step
            y_setp = self.common.border_Palette_Main[Mixing_Num][1] + y_border
            if i % 2 == 1:
                y_setp = self.common.border_Palette_Main[Mixing_Num][1] - y_border

            # 高
            x = x_setp
            y = y_setp
            z = z_up

            self.mc.set_coords([x, y, z], firt_speed)
            time.sleep(wait_sed)
            # 低1

            y_setp = self.common.border_Palette_Main[Mixing_Num][1] + y_border
            if i % 2 == 1:
                y_setp = self.common.border_Palette_Main[Mixing_Num][1] - y_border

            x = x_setp
            y = y_setp
            z = z_down

            self.mc.set_coords([x, y, z], firt_speed)
            time.sleep(wait_sed)

            # 低2 (往右划)
            x_setp = (
                self.common.border_Palette_Main[Mixing_Num][0] - (i - 1) * x_once_step
            )

            y_setp = self.common.border_Palette_Main[Mixing_Num][1] - y_border
            if i % 2 == 1:
                y_setp = self.common.border_Palette_Main[Mixing_Num][1] + y_border

            x = x_setp
            y = y_setp
            z = z_down

            self.mc.set_coords([x, y, z], firt_speed)
            time.sleep(wait_sed)

            # 高2 抬高
            y_setp = self.common.border_Palette_Main[Mixing_Num][1] - y_border
            if i % 2 == 1:
                y_setp = self.common.border_Palette_Main[Mixing_Num][1] + y_border

            x = x_setp
            y = y_setp
            z = z_up

            self.mc.set_coords([x, y, z], firt_speed)
            time.sleep(wait_sed)

    # Main Color_Dip
    def Active_Color_MainDip(self, Mixing_Num):
        print(f"check----------------Active_MainDip- {Mixing_Num}")
        # 中間主點

        x_once_step = 2
        y_border = 8.5
        wait_sed = 1
        firt_speed = 60
        z_up = self.common.up_Palette - 5
        z_down = self.common.border_Palette_Main[Mixing_Num][2]
        # # 往前
        for i in range(0, 6):
            x_setp = self.common.border_Palette_Main[Mixing_Num][0] - i * x_once_step
            y_setp = self.common.border_Palette_Main[Mixing_Num][1] + y_border
            if i % 2 == 1:
                y_setp = self.common.border_Palette_Main[Mixing_Num][1] - y_border

            # 高
            x = x_setp
            y = y_setp
            z = z_up

            self.mc.set_coords([x, y, z], firt_speed)
            time.sleep(wait_sed)
            # 低1

            wait_sed = 0.1
            firt_speed = 82

            y_setp = self.common.border_Palette_Main[Mixing_Num][1] + y_border
            if i % 2 == 1:
                y_setp = self.common.border_Palette_Main[Mixing_Num][1] - y_border

            x = x_setp
            y = y_setp
            z = z_down

            self.mc.set_coords([x, y, z], firt_speed)
            time.sleep(wait_sed)

            # 低2 (往右划)
            x_setp = (
                self.common.border_Palette_Main[Mixing_Num][0] - (i + 1) * x_once_step
            )

            y_setp = self.common.border_Palette_Main[Mixing_Num][1] - y_border
            if i % 2 == 1:
                y_setp = self.common.border_Palette_Main[Mixing_Num][1] + y_border

            x = x_setp
            y = y_setp
            z = z_down

            self.mc.set_coords([x, y, z], firt_speed)
            time.sleep(wait_sed)

            # 高2 抬高
            y_setp = self.common.border_Palette_Main[Mixing_Num][1] - y_border
            if i % 2 == 1:
                y_setp = self.common.border_Palette_Main[Mixing_Num][1] + y_border

            x = x_setp
            y = y_setp
            z = z_up

            self.mc.set_coords([x, y, z], firt_speed)
            time.sleep(wait_sed)

    # 主畫區測試
    def Active_MainTest(self, X, Y):
        if self.Check_thread_alive():
            return

        self.Thread_Active(active_function=self.active_MainTest, pars={"X": X, "Y": Y})

    def active_MainTest(self, X, Y):
        print(f"check----------------Active_MainTest => {X},{Y}")

        # 中心
        Robot_XY = self.Active_MainTranlation(0.5, 0.5)

        self.mc.set_coords([Robot_XY[0], Robot_XY[1], -30], 50)
        time.sleep(1)

        Robot_XY = self.Active_MainTranlation(X, Y)

        # 點位上
        self.mc.set_coords([Robot_XY[0], Robot_XY[1], -42.09], 30)
        time.sleep(0.7)

        # 點位下
        self.mc.set_coords([Robot_XY[0], Robot_XY[1], -47.09], 30)
        time.sleep(0.7)

        # 點位上
        self.mc.set_coords([Robot_XY[0], Robot_XY[1], -42.09], 30)
        time.sleep(0.7)
        self.Thead_ForceStop()

    # 檢查狀態
    def check_record_status(self, status: str):
        if (
            self.common.record_robot_status != ""
            and self.common.record_robot_status == status
        ):
            return True
        elif self.common.record_robot_status == "":
            return True

        return False

    def check_record_num(self, record_num, check_num):
        if record_num == -1:
            return True
        elif record_num != -1 and record_num == check_num:
            return True

        return False

    def Active_RecordInit(self):
        self.common.record_block_num = -1
        self.common.record_color_num = -1
        # self.common.record_conturs_num = -1
        self.common.record_line_num = -1
        self.common.record_pen_num = -1
        self.common.record_robot_status = ""

    # ---手臂啟動繪畫!!!
    def Active_Main(self):
        if self.Check_thread_alive():
            return

        self.Thread_Active(active_function=self.active_Main)

    def active_Main(self):
        print("Step1.-開始彩圖")

        if self.active_Colorful_Main() == False:
            print("Stop!!")
            return
        else:
            # 整個色彩結束後往線稿去
            # 往線搞去先把紀錄全清除
            self.Active_RecordInit()
            self.Robot_Status_Change(self.common.status_robot["Draft_Draw"])

        # 整個都畫完，再畫上線稿
        if self.check_record_status("Draft_Draw"):
            print("Step2.-開始線稿")
            self.active_Draft()

        # 完成後重新Init
        self.active_Init(need_Stop=False)
        self.Thead_ForceStop()

    def Robot_Status_Change(self, status_robot):
        if self.common.status_robot_now == status_robot:
            return

        self.common.status_robot_now = status_robot

        if self.common.status_robot_now == self.common.status_robot["None"]:
            pass
        # elif self.common.status_robot_now == self.common.status_robot['Color_Dip']:
        #     pass
        # elif self.common.status_robot_now == self.common.status_robot['Water_Dip']:
        #     # self.common.record_robot_status = 'Water_Dip'
        #     #不記錄record 免得影響pause
        #     # self.Active_Water_Dip()
        #     pass
        # elif self.common.status_robot_now == self.common.status_robot['Paper_Dip']:
        #     #self.common.record_robot_status = 'Paper_Dip'
        #     #不記錄record 免得影響pause
        #     # self.Active_Paper_Dip()
        #     pass
        elif (
            self.common.status_robot_now
            == self.common.status_robot["Color_Status_Check"]
        ):
            self.common.record_robot_status = "Color_Status_Check"
        elif (
            self.common.status_robot_now
            == self.common.status_robot["Color_Main_Select"]
        ):
            pass
        elif self.common.status_robot_now == self.common.status_robot["Color_Mix"]:
            pass
        elif (
            self.common.status_robot_now
            == self.common.status_robot["Color_Mix_Select_Check"]
        ):
            pass
        elif self.common.status_robot_now == self.common.status_robot["Pic_Draw"]:
            self.common.record_robot_status = "Pic_Draw"
        elif self.common.status_robot_now == self.common.status_robot["Draft_Draw"]:
            self.common.record_robot_status = "Draft_Draw"

    # 線搞測試
    def Active_DraftTest(self):
        if self.Check_thread_alive():
            return

        self.Thread_Active(active_function=self.active_DraftTest)

    def active_DraftTest(self):
        # 把之前紀錄都清空
        self.reset_records()
        self.active_Draft()
        self.Thead_ForceStop()

    # 線搞實作(與啟動的畫一起做)
    def active_Draft(self):
        pen_times = self.common.pen_times_draft_setting_draft
        lines = self.common.draft_lines

        # 先做一次沾水跟顏料
        self.Active_Water_Dip_p_center()
        self.Active_Water_Dip()
        self.Active_Water_Dip_p_center()

        # 找黑色
        for cell_num in range(0, len(self.common.Color_Cells)):
            if self.common.Color_Cells[cell_num].Color_Pre == "黑色":
                self.Active_ColorDip_center()
                self.Active_ColorDip(cell_num, border_clear=True)
                break

        self.Active_ColorDip_center()

        # 每一條線
        for line_num in range(0, len(lines)):
            if self.check_record_num(self.common.record_line_num, line_num) == False:
                continue
            self.common.record_line_num = line_num

            # 每一筆
            for pen_num in range(0, len(lines[line_num].groups_pens)):
                if self.check_record_num(self.common.record_pen_num, pen_num) == False:
                    continue

                self.common.record_pen_num = pen_num

                one_pen = lines[line_num].groups_pens[pen_num]

                # start
                self.mc.set_coords(one_pen.point_start, 20)
                time.sleep(1)

                # 繪圖過程
                for one_point in one_pen.point_precess:
                    self.mc.set_coords(one_point, 10)
                    time.sleep(0.16)

                # end
                self.mc.set_coords(one_pen.point_end, 20)
                time.sleep(1)

                pen_times = pen_times - 1

                if pen_times <= 0:
                    pen_times = self.common.pen_times_draft_setting_draft
                    self.Active_Water_Dip_p_center()
                    self.Active_Water_Dip()
                    self.Active_Water_Dip_p_center()

                    # 找黑色點
                    for cell_num in range(0, len(self.common.Color_Cells)):
                        if self.common.Color_Cells[cell_num].Color_Pre == "黑色":
                            self.Active_ColorDip_center()
                            self.Active_ColorDip(cell_num, border_clear=True)
                            self.Active_ColorDip_center()
                            break

                # 做完一筆清一筆
                self.common.record_pen_num = -1
            # 做完一筆清一筆
            self.common.record_line_num = -1

    # 彩搞測試
    def Active_ColorfulTest(self, i):
        if self.Check_thread_alive():
            return

        self.Thread_Active(active_function=self.active_ColorfulTest, pars={"i": i})

    def active_ColorfulTest(self, i):
        print(f"測試區域:{i}")

        self.Active_Water_Dip_p_center()
        time.sleep(2)
        self.reset_records()
        if self.check_record_num(self.common.record_block_num, i) == False:
            return
        # print(f"測試開始")
        self.active_Colorful_Block_Single(i)
        self.common.record_block_num = -1
        self.Thead_ForceStop()

    # 彩搞實際繪圖測試
    def Active_Colorful_MainTest(self):
        if self.Check_thread_alive():
            return

        self.Thread_Active(active_function=self.active_Colorful_MainTest)

    def active_Colorful_MainTest(self):
        # 把之前紀錄都清空
        self.reset_records()
        self.active_Colorful_Main()
        self.Thead_ForceStop()

    # TODO pen_times 數量計算 還未加 彩搞實作(與啟動的畫一起做)
    def active_Colorful_Main(self):
        self.Active_Water_Dip_p_center()

        # Color_Status_Check 跟 Pic_Draw 判斷直接寫在裡面，懶得改
        # 找尋彩稿裡的資訊-還要加入判斷過往紀錄機制

        if self.check_record_status("Color_Status_Check") or self.check_record_status(
            "Pic_Draw"
        ):
            is_color_draw = False
            for block_info_num in range(0, len(self.common.block_colorful_colors_info)):
                if (
                    self.check_record_num(self.common.record_block_num, block_info_num)
                    == False
                ):
                    continue
                self.common.record_block_num = block_info_num
                is_color_draw = True

                print(f"第{block_info_num}區塊")

                if self.active_Colorful_Block_Single(block_info_num) == False:
                    return False

                # 整格block 內的顏色都判斷完並畫完後
                self.common.record_block_num = -1

            if is_color_draw == False:
                print("未畫出彩圖區塊")
                return False

            print("區塊畫完")
            return True

        print("不是區塊判定")
        return False

    def active_Colorful_Block_Single(self, block_info_num):
        # 檢查block每個顏色
        for colors_info_num in range(
            0, len(self.common.block_colorful_colors_info[block_info_num])
        ):
            if (
                self.check_record_num(self.common.record_color_num, colors_info_num)
                == False
            ):
                continue
            self.common.record_color_num = colors_info_num

            # 如果顏色判斷失敗，直接停掉
            if (
                self.active_Colorful_colors_info_Single(block_info_num, colors_info_num)
                == False
            ):
                return False

            # print('下一個')
            # 整個線段內的單一顏色判斷並都畫完以後把紀錄清掉
            self.common.record_color_num = -1

        return True

    def active_Colorful_colors_info_Single(self, block_info_num, colors_info_num):
        color_info = self.common.block_colorful_colors_info[block_info_num][
            colors_info_num
        ]

        if self.check_record_status("Color_Status_Check"):
            self.Robot_Status_Change(self.common.status_robot["Color_Status_Check"])
            # -1. 指定目標顏色
            self.common.color_goal = color_info["predict"]

            if self.active_Colorful_check_Single() == False:
                return False
            else:
                self.Robot_Status_Change(self.common.status_robot["Pic_Draw"])

        # 顏色調好以後開始繪圖
        if self.check_record_status("Pic_Draw"):
            self.active_Colorful_colors_lines_cycle(block_info_num, colors_info_num)

            # coutur 畫完清除紀錄
            # self.common.record_conturs_num = -1
        # 整個區塊顏色畫完，重新回到檢查模式
        self.Robot_Status_Change(self.common.status_robot["Color_Status_Check"])

        return True

    # 筆數到，重新取色再畫
    def active_Colorful_colors_lines_cycle(self, block_info_num, colors_info_num):
        color_info = self.common.block_colorful_colors_info[block_info_num][
            colors_info_num
        ]

        isDrawStatus = True
        # 一開始已經判斷顏色
        isFirst_in = True
        while isDrawStatus:
            if isFirst_in == False:
                if self.check_record_status("Color_Status_Check"):
                    self.Robot_Status_Change(
                        self.common.status_robot["Color_Status_Check"]
                    )
                    # -1. 指定目標顏色
                    self.common.color_goal = color_info["predict"]

                    if self.active_Colorful_check_Single() == False:
                        return
                    else:
                        self.Robot_Status_Change(self.common.status_robot["Pic_Draw"])
            # 顏色的動作都好了以後開始繪圖
            if self.check_record_status("Pic_Draw"):
                # 算畫了幾筆
                pen_times = self.common.pen_times_draft_setting

                # 裡面是 list[list[line]]，因為還有個contur
                colorful_conturs = self.common.colorful_lines[
                    block_info_num
                ].groups_pens[colors_info_num]

                isCycle = False

                # 沾色中間主點
                self.mc.set_coords(self.common.center_main, 40)
                time.sleep(1)

                for colorful_lines_num in range(0, len(colorful_conturs)):
                    if (
                        self.check_record_num(
                            self.common.record_line_num, colorful_lines_num
                        )
                        == False
                    ):
                        continue

                    self.common.record_line_num = colorful_lines_num

                    groups_pens = colorful_conturs[colorful_lines_num].groups_pens

                    # groups_pens 只有一個
                    for pen_num in range(0, len(groups_pens)):
                        if (
                            self.check_record_num(self.common.record_pen_num, pen_num)
                            == False
                        ):
                            continue
                        self.common.record_pen_num = pen_num

                        # 改為一個line裡面只有一筆pen(因為距離很短，不用再判斷一筆要不要沾顏料)
                        # 不在紀錄點位，只記錄到pen
                        pen = groups_pens[pen_num]

                        # start
                        self.mc.set_coords(pen.point_start, 70)
                        time.sleep(0.5)

                        # 繪圖過程
                        for one_point in pen.point_precess:
                            self.mc.set_coords(one_point, 50)
                            time.sleep(0.35)

                        # end
                        self.mc.set_coords(pen.point_end, 70)
                        time.sleep(0.5)

                        # 這筆畫完清除紀錄
                        self.common.record_pen_num = -1

                    # print(f"目前檢查{pen_times}")
                    # time.sleep(1)
                    pen_times = pen_times - 1
                    # 筆畫到了，重新判斷、取色，再畫
                    if pen_times <= 0:
                        isFirst_in = False
                        lines_num_next = colorful_lines_num + 1
                        if lines_num_next < len(colorful_conturs):
                            self.common.record_line_num = lines_num_next

                            print(f"重新取色!!  第{self.common.record_line_num}線")
                            self.Active_Water_Dip_p_center()
                            time.sleep(0.3)
                            self.Robot_Status_Change(
                                self.common.status_robot["Color_Status_Check"]
                            )
                            isCycle = True
                            break
                        else:
                            isDrawStatus = False

                    self.common.record_line_num = -1

                if isCycle == False:
                    isDrawStatus = False
                    self.common.record_line_num = -1
                    print(f"第{block_info_num}區塊第{colors_info_num}個顏色訊息繪圖結束")
        self.common.record_line_num = -1

    def active_Colorful_check_Single(self):
        # -2. 檢查顏色
        acitve_cmd, index, dis_layer = self.active_ColorStatus_check(
            self.common.color_goal
        )

        print(f"acitve_cmd :{acitve_cmd}")

        # 進入人工停止清理模式後，再重新判斷
        if acitve_cmd == "Stop_and_ClearMain":
            print(f"事前判斷失敗--人工清理")
            return False

        self.Active_Water_Dip_p_center()
        self.Active_Water_Dip()
        self.Active_Water_Dip_p_center()

        if acitve_cmd == "Cells":  # 直接提取繪製
            self.Active_ColorDip(index)
        elif acitve_cmd == "Mains":  # 直接提取繪製， TODO 少一個提取主色盤顏色動作
            self.Active_Color_MainDip(index)
        elif acitve_cmd == "ColorMix":  # 進入混色模式
            if self.active_ColorMix_Process(index, dis_layer):
                pass
            else:
                # 混色失敗-人工清理
                return False

        return True

    # return 文字與index,dis_layer
    # 文字 -"Stop_and_ClearMain"清理色盤,"ColorMix"調色(可能主盤裡是白色或其他顏色),"Cells"色格裡,"Mains"色盤裡
    # index -"-1"為沒有(可能代表需要人工清除主色盤顏色),index 為哪個區塊
    # dis_layer -"-1"為沒有,index 目標顏色跟主盤色的差距
    def active_ColorStatus_check(self, color_goal):
        print(f"目標顏色: {color_goal}")

        # 檢查色格是否相同
        for cell_num in range(0, len(self.common.Color_Cells)):
            #   print(f'色格 {cell_num}: {self.common.Color_Cells[cell_num].Color_Pre}')
            if self.common.Color_Cells[cell_num].Color_Pre == color_goal:
                return "Cells", cell_num, -1

        # 檢查色盤是否相同---2023年6/5取消，顏色量不夠
        # for main_num in range(0,len(self.common.Color_Mains)):
        #       if self.common.Color_Mains[main_num].Color_Pre == color_goal:
        #           return "Mains",main_num,-1

        # 1. 找尋主盤的"同色調"
        for main_num in range(0, len(self.common.Color_Mains)):
            if self.common.Color_Mains[main_num].Color_Pre != "白色":
                # 目標顏色的色調 與 色盤的色調 是否相同

                goal_system_num, goal_system_pos = self.get_system_color_num_pos(
                    color_goal
                )
                (
                    main_system_num,
                    main_system_pos,
                ) = self.get_system_color_num_pos_match_goal(
                    self.common.Color_Mains[main_num].Color_Pre, color_goal
                )

                if (
                    goal_system_num != -1
                    and main_system_num != -1
                    and goal_system_num == main_system_num
                ):
                    dis_layer = goal_system_pos - main_system_pos
                    print(f"主盤同色系--{main_num}--{dis_layer}")
                    return "ColorMix", main_num, dis_layer

        # 2. 找尋主盤的有"白色"
        for main_num in range(0, len(self.common.Color_Mains)):
            if self.common.Color_Mains[main_num].Color_Pre == "白色":
                print(f"主盤白色--{main_num}")
                return "ColorMix", main_num, -99

        # 人工清除主色盤顏色
        return "Stop_and_ClearMain", -1, -1

    def reset_records(self):
        self.common.record_block_num = -1
        self.common.record_color_num = -1
        # self.common.record_conturs_num = -1
        self.common.record_line_num = -1
        self.common.record_pen_num = -1
        self.common.record_robot_status = ""

    # 找尋顏色屬於那個色系
    def get_system_color_num_pos(self, color_name):
        for color_system_num in range(0, len(self.common.Systems_Colors)):
            if color_name in self.common.Systems_Colors[color_system_num]:
                return color_system_num, self.common.Systems_Colors[
                    color_system_num
                ].index(color_name)

        return -1, -1

    # 找尋顏色屬於那個色系，並符合目標顏色的色系
    def get_system_color_num_pos_match_goal(self, color_name, goal):
        get_color_sys_pos = []
        # print(f"m_c--{color_name}")
        # print(f"--{goal}")

        # for i in range(0, len(self.common.Color_Mains)):
        #     print(f"22--{i}-{self.common.Color_Mains[i].Color_Pre}")

        for color_system_num in range(0, len(self.common.Systems_Colors)):
            if color_name in self.common.Systems_Colors[color_system_num]:
                get_color_sys_pos.append(
                    {
                        "sys_num": color_system_num,
                        "sys_num_pos": self.common.Systems_Colors[
                            color_system_num
                        ].index(color_name),
                    }
                )

        for s_p in get_color_sys_pos:
            goal_system_num, goal_system_pos = self.get_system_color_num_pos(goal)

            if s_p["sys_num"] == goal_system_num:
                return s_p["sys_num"], s_p["sys_num_pos"]

        return -1, -1

    # 判定是否符合目標色系__已經選定好主調盤位置
    def isMatch_goal_color(self, main_num, color_goal):
        print(f"{main_num}-{color_goal}")

        # 檢查主色盤此編號的顏色是否與目標顏色相同
        for main_num_c in range(0, len(self.common.Color_Mains)):
            if self.common.Color_Mains[main_num_c].Color_Pre == color_goal:
                return True, -1, -1, -1, -1
        # 如果還是沒有到目標顏色，重新找尋顏色系統
        goal_system_num, goal_system_pos = self.get_system_color_num_pos(color_goal)

        main_system_num, main_system_pos = self.get_system_color_num_pos_match_goal(
            self.common.Color_Mains[main_num].Color_Pre, color_goal
        )

        return False, goal_system_num, goal_system_pos, main_system_num, main_system_pos

    # 混色狀態開始
    # dis=-99，等於一開始是白色
    def active_ColorMix_Process(self, main_num, dis):
        self.Robot_Status_Change(self.common.status_robot["Color_Mix"])

        get_color_pal = -1
        isFirst_in = True
        isMatch_goal = False
        system_num, system_pos = self.get_system_color_num_pos(self.common.color_goal)
        System_Colors = self.common.Systems_Colors[system_num]

        dis_g_m = dis
        # - 顏色到達 結束混色
        # - 未到，洗筆後繼續混色
        while isMatch_goal == False:
            # 目標顏色 - 主色盤顏色
            # 正 往 右
            # 負 往 左

            # 先調哪種顏色
            if dis_g_m != -99:
                if dis_g_m < 0:
                    get_color_pal = 0
                else:
                    get_color_pal = len(System_Colors) - 1
            else:
                # -99等於從白色開始
                # 找到目標顏色最接近的顏色開始混色
                if system_pos >= int(len(self.common.Systems_Colors[system_num]) / 2):
                    get_color_pal = len(System_Colors) - 1
                else:
                    get_color_pal = 0

            color_name = System_Colors[get_color_pal]

            # 哪一格
            print(
                f"混色---目標顏色:{self.common.color_goal},色系為:{system_num},取顏色:{color_name}"
            )

            is_find_cell_color = False

            # 找出色格中顏色
            for cell_num in range(0, len(self.common.Color_Cells)):
                if self.common.Color_Cells[cell_num].Color_Pre == color_name:
                    if isFirst_in == False:
                        self.Active_Water_Dip_p_center()

                        # 不回去洗筆狀態，直接改
                        self.Active_Water_Dip()
                        # 怕水沒乾
                        time.sleep(1)

                    # 主盤跟調色盤中間
                    self.Active_ColorDip_center()

                    self.Active_ColorDip(cell_num, layer=dis_g_m)
                    is_find_cell_color = True
                    isFirst_in = False
                    break

            if is_find_cell_color == True:
                # 主盤調色
                self.Active_ColorMainMixing(main_num)
            else:
                print("未找到色格顏色")
                return False
            # 避免擋住攝影機
            self.Active_Water_Dip_p_center()
            time.sleep(0.5)
            # 再次檢查
            (
                isMatch_goal,
                goal_system_num,
                goal_system_pos,
                main_system_num,
                main_system_pos,
            ) = self.isMatch_goal_color(main_num, self.common.color_goal)

            # 如果發生 目標顏色系統跟主盤顏色系統不一致了，進行人工清洗
            if goal_system_num != main_system_num:
                print("混色階段_人工清理")
                return False

            System_Colors = self.common.Systems_Colors[goal_system_num]
            dis_g_m = goal_system_pos - main_system_pos

        return True

    #  線搞平面點位轉化成機器人點位
    def robot_draft_paths(self, draft_path):
        # 一次抓幾個點當作一筆
        pan_once_points = 20
        self.common.draft_lines.clear()

        height, width, channels = self.common.picPc_ori_draft_bone.shape
        for p in draft_path:
            once_line = line.line()
            # 計算pan的量
            count_pans = int(len(p) / pan_once_points)

            # last_pens 把剩餘的放在count_pans最後一個group_pens內
            if len(p) % pan_once_points > 0:
                last_pens = 1

            # count_pans = 畫筆的數量(剩餘的點放在最後一個group_pens)
            for i in range(0, count_pans):
                num_min = pan_once_points * i
                num_max = pan_once_points * (i + 1) + 1  # end 需要再加1，要到下一筆的start

                # 剩餘的點放到最後的筆群組
                if i >= count_pans - 1:
                    if last_pens >= 1:
                        num_max = len(p) - 1

                # 計算出0-1值
                p_min = [float(p[num_min][0] / width), float(p[num_min][1] / height)]
                p_max = [float(p[num_max][0] / width), float(p[num_max][1] / height)]
                # 每一個pen
                one_pen = pen.pen()
                # start
                r_p = self.Active_MainTranlation(p_min[0], p_min[1])
                one_pen.point_start = [r_p[0], r_p[1], -38.09]

                # end
                r_p = self.Active_MainTranlation(p_max[0], p_max[1])
                one_pen.point_end = [r_p[0], r_p[1], -38.09]
                # 別忘記 j是不會到num_max，所以必須要加一
                for j in range(num_min, num_max + 1):
                    x = float(p[j][0] / width)
                    y = float(p[j][1] / height)

                    p_pro = [x, y]

                    range_robot = y * abs(
                        self.common.z_range[0] - self.common.z_range[1]
                    )

                    robot_z = self.common.z_range[1] - range_robot

                    p_process = self.Active_MainTranlation(p_pro[0], p_pro[1])
                    r_p = [p_process[0], p_process[1], robot_z]
                    one_pen.point_precess.append(r_p)

                once_line.groups_pens.append(one_pen)

            self.common.draft_lines.append(once_line)

    # 彩搞平面點位轉化成機器人點位 - 此區有點複雜
    def robot_color_paths(self, color_path):
        self.common.colorful_lines.clear()

        height, width, channels = self.common.picPc_ori_colorful.shape

        # for block in color_path :
        for block_num in range(0, len(color_path)):
            block = color_path[block_num]

            blocks_color = block_color.block_color()
            # 顏色區塊
            for color_couturs in block:
                once_coutur = []
                # 每個顏色也有不能位置的coutur
                for color_coutur in color_couturs:
                    for path in color_coutur:
                        once_line = line.line()

                        for p_n in range(0, len(path)):
                            # 變成1 個line 只有前後兩點
                            if p_n >= len(path) - 1:
                                break

                            num_min = p_n
                            num_max = num_min + 1

                            # 計算出0-1值

                            p_min = [
                                float(path[num_min][0] / width),
                                float(path[num_min][1] / height),
                            ]
                            p_max = [
                                float(path[num_max][0] / width),
                                float(path[num_max][1] / height),
                            ]

                            one_pen = pen.pen()
                            # start
                            r_p = self.Active_MainTranlation(p_min[0], p_min[1])
                            one_pen.point_start = [r_p[0], r_p[1], -42.09]

                            # end
                            r_p = self.Active_MainTranlation(p_max[0], p_max[1])
                            one_pen.point_end = [r_p[0], r_p[1], -42.09]

                            for j in range(num_min, num_max + 1):
                                p_pro = [
                                    float(path[j][0] / width),
                                    float(path[j][1] / height),
                                ]
                                p_process = self.Active_MainTranlation(
                                    p_pro[0], p_pro[1]
                                )
                                r_p = [p_process[0], p_process[1], -47.00]

                                one_pen.point_precess.append(r_p)

                            once_line.groups_pens.append(one_pen)
                        once_coutur.append(once_line)
                blocks_color.groups_pens.append(once_coutur)

            self.common.colorful_lines.append(blocks_color)

    def Active_MainTranlation(self, X, Y):
        # 對於機器人平面視角的x,y
        d_y_dis = self.common.border_pic[0][0] - self.common.border_pic[1][0]
        d_x_dis = self.common.border_pic[0][1] - self.common.border_pic[2][1]

        d_y0 = self.common.border_pic[1][0]
        d_x0 = self.common.border_pic[2][1]

        d_x_step = d_x_dis * float(X)
        d_y_step = d_y_dis * float(Y)

        d_r_x = d_x0 + d_x_step
        d_r_y = d_y0 + d_y_step

        # 機器人座標的X,Y
        return [round(d_r_y, 2), round(d_r_x, 2)]
