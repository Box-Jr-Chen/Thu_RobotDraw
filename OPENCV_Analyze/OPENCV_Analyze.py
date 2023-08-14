import threading
import PIL.Image, PIL.ImageTk
from skimage import morphology
import os.path
import numpy as np
import cv2 as cv2
import colorsys
import math
import copy

from models.pal_color import Pal_Color
from collections import defaultdict

# 1. 先確認骨架 - 確認線搞線段
# 2. 判斷色塊區域組
# 3. 判斷色塊區域組-各顏色
# 3. 判斷色塊區域組內-各顏色區域的線段
#   - 是區塊
#   - 或是線段
#       # skeletonize化後，找出繪製線段
#       - (進階) 繪製線段 與 contour 判斷
#              - 找出繪製線段 各 point 法線， 並與 poly-contour的線相交的兩點(或沒有)
#              - 依據兩點算出曲線各點的寬度(沒有相交兩點，寬度可能為0)
# 4.色盤調色


class OPENCV_Analyze:
    def __init__(self):
        self.common = None
        self.cap_color = None  # 調色盤攝影機
        self.camIndex = 0
        self.cap_real_width = 1280
        self.cap_real_height = 720

        self.path_image_draft = ""
        self.path_image_colorful = ""

        self.fun_robot_draft_paths = None
        self.fun_listbox_getblocks = None

    def get_Common(self, CommonOb):
        self.common = CommonOb

    def start_cam_PicReal(self, action_isNotOpened):
        if self.common is None:
            print("未設定共用物件")
            return

        self.cap_color = cv2.VideoCapture(self.camIndex, cv2.CAP_DSHOW)
        self.cap_color.set(cv2.CAP_PROP_FRAME_WIDTH, self.common.UI_PicReal_size[0])
        self.cap_color.set(cv2.CAP_PROP_FRAME_HEIGHT, self.common.UI_PicReal_size[1])

        print("給定攝影機")
        if not self.cap_color.isOpened():
            print("無法開啟攝影機")
            if action_isNotOpened is not None:
                action_isNotOpened()

    def Anayzie_Cam_Img_sketch(self, image, num_clusters, contrast, brightness):
        error = ""

        try:
            # 修改亮度與對比
            image = self.Hun_Image(image, contrast, brightness)

            h_image, w_image, ch = image.shape
            data = image.reshape((-1, 3))
            data = np.float32(data)

            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
            # num_clusters = 4  # 聚类的数量
            ret, label, center = cv2.kmeans(
                data,
                num_clusters,
                None,
                criteria,
                num_clusters,
                cv2.KMEANS_RANDOM_CENTERS,
            )

            # card = np.zeros((h_image+50, w_image, 3), dtype=np.uint8)
            clusters = np.zeros([num_clusters], dtype=np.int32)

            for i in range(len(label)):
                clusters[label[i][0]] += 1  # 计算每个类别共有多少个

            clusters = np.float32(clusters) / float(h_image * w_image)  # 计算概率
            center = np.int32(center)  # 因为像素值是 0-255 故对其聚类中心进行强制类型转换
            # 1. 白色如果大於50 趴，判定白色
            # 2. 兩色 H相減，在10以內做平均
            # 3. 兩色 H相減，在10以外判定多種顏色
            max_scale_color = {"hsv": (0, 0, 0), "scale": 0}

            # 判定顏色陣列
            color_hsv_array = []

            for c in np.argsort(clusters)[
                ::-1
            ]:  # 这里对主色按比例从大到小排序 [::-1] 代表首尾反转 如[1,2,3] -> [3, 2, 1]
                b = center[c][0]  # 这一类对应的中心，即 RGB 三个通道的值
                g = center[c][1]
                r = center[c][2]

                h, s, v = colorsys.rgb_to_hsv(b / 255, g / 255, r / 255)
                hc = int(h * 180)
                sc = int(s * 255)
                vc = int(v * 255)

                color_hsv = [hc, sc, vc]
                color_hsv_array.append({"hsv": color_hsv, "scale": clusters[c]})

                # 加入最大比例
                if max_scale_color["scale"] < clusters[c]:
                    max_scale_color["scale"] = clusters[c]
                    max_scale_color["hsv"] = color_hsv

            Color_Firt = max_scale_color["hsv"]
            scale = max_scale_color["scale"]
            Color_Pre = "白色"

            if Color_Firt[2] <= 85:  # 如果是黑色
                Color_Pre = f"黑色"
            # elif Color_Firt[2] >60 and Color_Firt[2] <=130:# 如果是黑色
            #     Color_Pre =  f'灰色'
            elif Color_Firt[1] <= 60:  # 如果是白色
                Color_Pre = f"白色"
            elif scale >= 0.5 and Color_Firt[1] <= 60:  # 如果是白色
                Color_Pre = f"白色"
            else:
                hm_a = 0
                sm_a = 0
                vm_a = 0

                # 不算差距了，直接用最大比例的來做顏色
                # rangeabs  = abs(color_hsv_array[0]['hsv'][0] - color_hsv_array[1]['hsv'][0])
                # Color_Pre = f'r {rangeabs}'
                # if rangeabs <=15 :

                max_hsv = {"hsv": [-1, -1, -1], "scale": -1}

                for c in color_hsv_array:
                    if c["scale"] > max_hsv["scale"]:
                        max_hsv["hsv"] = [c["hsv"][0], c["hsv"][1], c["hsv"][2]]
                        max_hsv["scale"] = c["scale"]

                    # (vc, sm, vm) = (c['hsv'][0], c['hsv'][1], c['hsv'][2])

                    # hm_a = hm_a + vc
                    # sm_a = sm_a + sm
                    # vm_a = vm_a + vm

                    # hm_a = int(hm_a / num_clusters)
                    # sm_a = int(sm_a / num_clusters)
                    # vm_a = int(vm_a / num_clusters)
                Color_Pre = self.Anayzie_Color(
                    (max_hsv["hsv"][0], max_hsv["hsv"][1], max_hsv["hsv"][2])
                )

            return image, Color_Firt, Color_Pre
            # return image,Color_Firt,Color_Pre+ f'({str(Color_Firt[0])},{str(Color_Firt[1])},{str(Color_Firt[2])})'
        except Exception as e:
            return image, [0, 0, 0], e

    # 必須要把黑色去掉
    def Anayzies_Color_block(self, img_block):
        h, w, ch = img_block.shape
        data = img_block.reshape((-1, 3))
        data = np.float32(data)
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        num_clusters = 4  # 聚类的数量
        ret, label, center = cv2.kmeans(
            data, num_clusters, None, criteria, num_clusters, cv2.KMEANS_RANDOM_CENTERS
        )

        clusters = np.zeros([num_clusters], dtype=np.int32)
        for i in range(len(label)):
            clusters[label[i][0]] += 1  # 计算每个类别共有多少个

        clusters = np.float32(clusters) / float(h * w)  # 计算概率
        center = np.int32(center)  # 因为像素值是 0-255 故对其聚类中心进行强制类型转换

        color_hsv_array = []

        for c in np.argsort(clusters)[
            ::-1
        ]:  # 这里对主色按比例从大到小排序 [::-1] 代表首尾反转 如[1,2,3] -> [3, 2, 1]
            dx = np.int(clusters[c] * w)  # 这一类转换成色彩卡片有多宽
            b = center[c][0]  # 这一类对应的中心，即 RGB 三个通道的值
            g = center[c][1]
            r = center[c][2]
            percent = round(float(clusters[c]), 3)

            color_hsv_array.append(
                {"color": [r, g, b], "percent": percent, "predict": ""}
            )

        # 把黑色比例移掉
        scale = 1
        for c in color_hsv_array:
            if c["color"] == [0, 0, 0]:
                scale = scale - c["percent"]

        scale_re = 1 / scale

        color_hsv_array = [
            x for x in color_hsv_array if x["color"] != [0, 0, 0]
        ]  # 移除所有黑色

        for c in color_hsv_array:
            (hc, sc, vc) = colorsys.rgb_to_hsv(
                c["color"][2] / 255, c["color"][1] / 255, c["color"][0] / 255
            )
            c["color"] = [int(hc * 180), int(sc * 255), int(vc * 255)]
            c["percent"] = round(c["percent"] * scale_re, 3)
            c["predict"] = self.Anayzie_Color(c["color"])

        result_dict = defaultdict(list)

        for element in color_hsv_array:
            predict = element["predict"]
            percent = element["percent"]
            color = element["color"]

            result_dict[predict].append({"percent": percent, "color": color})

        result_list = []

        for predict, values in result_dict.items():
            percent_sum = round(sum(val["percent"] for val in values), 3)

            if percent_sum >= 0.995:
                percent_sum = 1

            colors = [val["color"] for val in values]
            result_list.append(
                {"predict": predict, "percent_sum": percent_sum, "colors": colors}
            )

        return result_list

    # 對比跟光亮修改
    def Hun_Image(self, img, contrast, brightness):
        output = img * (contrast / 127 + 1) - contrast + brightness
        output = np.clip(output, 0, 255)
        output = np.uint8(output)

        return output

    def Set_img_ori_draft(self, path: str):
        self.path_image_draft = path
        self.common.picPc_ori_draft = None
        if os.path.isfile(self.path_image_draft):
            self.common.picPc_ori_draft = cv2.imread(path)
            # 用於顯示
            self.common.picPc_ori_draft_block_dis = copy.deepcopy(
                self.common.picPc_ori_draft
            )
            # 上下顛倒圖像
            self.common.picPc_ori_draft = cv2.flip(self.common.picPc_ori_draft, 0)

            # 計算繪畫區塊
            self.get_img_blocks(self.common.picPc_ori_draft)

            gray = cv2.cvtColor(self.common.picPc_ori_draft, cv2.COLOR_BGR2GRAY)
            ret, imgBin = cv2.threshold(gray, 95, 255, 1)
            self.common.picPc_ori_draft_bone, paths_draft = self.img_skeletonize(
                imgBin, False
            )

            # 機器人點轉換
            self.common.RobotBehavior.robot_draft_paths(paths_draft)

        else:
            print("path is not exit")

    def Set_img_ori_colorful(self, path: str):
        self.path_image_colorful = path
        self.common.picPc_ori_colorful = None

        if os.path.isfile(self.path_image_colorful):
            self.common.picPc_ori_colorful = cv2.imread(path)

            # 上下顛倒圖像
            self.common.picPc_ori_colorful = cv2.flip(self.common.picPc_ori_colorful, 0)
            self.common.picPc_ori_colorful = cv2.cvtColor(
                self.common.picPc_ori_colorful, cv2.COLOR_BGR2RGB
            )

            # 直接把各自的block儲存起來(資訊)
            self.common.block_colorful_colors_info.clear()

            for block in self.common.blocks_colorful_countor:
                color_block = self.img_color_check(block)
                self.common.picPc_ori_colorful_blocks.append(color_block)  # 圖片
                self.common.block_colorful_colors_info.append(
                    self.Anayzies_Color_block(color_block)
                )  # 顏色資訊

            # 判斷各區塊内各個顏色的路徑
            # 變成機器路徑
            for block_num in range(0, len(self.common.picPc_ori_colorful_blocks)):
                block_colors = self.common.block_colorful_colors_info[block_num]

                colors_path = []

                # 特殊情況處理

                # 綠色 - 春綠色 - 黃綠色(過度)
                is_green_process, mask = self.is_green_process(block_num)

                if is_green_process:
                    for color_num in range(0, len(block_colors)):
                        if block_colors[color_num]["predict"] == "綠色":
                            path_g = self.range_color_special_path(block_num, mask)
                            colors_path.append(path_g)  # 0
                        elif block_colors[color_num]["predict"] == "春綠色":
                            colors_path.append([])
                        elif block_colors[color_num]["predict"] == "黃綠色":
                            colors_path.append(
                                self.range_color_path(block_num, color_num)
                            )
                else:
                    # 正常情況處理
                    for color_num in range(0, len(block_colors)):
                        colors_path.append(self.range_color_path(block_num, color_num))

                self.common.blocks_colors_path.append(colors_path)

            self.common.RobotBehavior.robot_color_paths(self.common.blocks_colors_path)

            # UI創造線稿測試按鈕
            self.common.RobotCumtomerUI.fun_create_paths_Test_inRobotControl()

        else:
            print("path is not exit")

    def fun_draft_seleted_block(self, num):
        del self.common.picPc_ori_draft_block_dis
        self.common.picPc_ori_draft_block_dis = copy.deepcopy(
            self.common.picPc_ori_draft
        )
        self.draw_line_points(
            False,
            self.common.picPc_ori_draft_block_dis,
            self.common.blocks_colorful_countor[num],
            (0, 0, 255),
            (0, 0, 255),
            5,
            1,
        )

    def fun_colorful_seleted_block(self, num):
        if isinstance(self.common.picPc_ori_colorful_dis, np.ndarray):
            del self.common.picPc_ori_colorful_dis
        self.common.picPc_ori_colorful_dis = copy.deepcopy(
            self.common.picPc_ori_colorful
        )
        self.draw_line_points(
            False,
            self.common.picPc_ori_colorful_dis,
            self.common.blocks_colorful_countor[num],
            (0, 0, 255),
            (0, 0, 255),
            1,
            1,
        )

        # 繪製路徑
        blocks_path = self.common.blocks_colors_path[num]
        for color_l in blocks_path:
            for coutur_l in color_l:
                for path_num in range(0, len(coutur_l)):
                    self.draw_line_points(
                        False,
                        self.common.picPc_ori_colorful_dis,
                        coutur_l[path_num],
                        (255, 0, 0),
                        (0, 255, 255),
                        2,
                        1,
                        need_cycle=False,
                    )

    def fun_colorful_seleted_color(self):
        if isinstance(self.common.picPc_ori_colorful_dis_mask, np.ndarray):
            del self.common.picPc_ori_colorful_dis_mask

        # 綠色 - 春綠色 - 黃綠色(過度)
        is_green_process, mask = self.is_green_process(self.common.select_block_num)

        if is_green_process:
            predict = self.common.block_colorful_colors_info[
                self.common.select_block_num
            ][self.common.select_block_color_num]["predict"]
            if predict == "綠色":
                self.common.picPc_ori_colorful_dis_mask = mask
            elif predict == "春綠色":
                img = self.common.picPc_ori_colorful_blocks[
                    self.common.select_block_num
                ]
                self.common.picPc_ori_colorful_dis_mask = np.zeros(
                    (img.shape[0], img.shape[1]), dtype=np.uint8
                )
            elif predict == "黃綠色":
                self.common.picPc_ori_colorful_dis_mask = self.get_color_mask(
                    self.common.select_block_num, self.common.select_block_color_num
                )

                # contours, hierarchy = cv2.findContours(self.common.picPc_ori_colorful_dis_mask , cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
                # cv2.drawContours(self.common.picPc_ori_colorful_blocks[self.common.select_block_num], contours, -1, (0,255,0), 1)
        else:
            self.common.picPc_ori_colorful_dis_mask = self.get_color_mask(
                self.common.select_block_num, self.common.select_block_color_num
            )

    # -----------------------------判斷
    # 判斷顏色
    def Anayzie_Color(self, hsv):
        h = hsv[0]
        s = hsv[1]
        v = hsv[2]

        for k in self.common.Color_HSV.keys():
            r_h = self.common.Color_HSV[k]["range"]
            min, max = r_h[0], r_h[1]

            if min[0] <= h and h <= max[0]:
                return self.common.Color_HSV[k]["name"]
                # return  str(h)+";"+str(s)+";"+self.common.Color_HSV[k]['l_c']
        return f"none {h}"

    # 算兩點距離
    def dis_2p(self, p1, p2):
        x_d = round(p2[0] - p1[0], 4)
        y_d = round(p2[1] - p1[1], 4)
        return math.sqrt((x_d**2) + (y_d**2))

    # 是否有交互點
    def cross_point(self, line_1, line_2):
        point_is_exit = False
        x = 0
        y = 0

        l1_x1 = line_1[0][0]
        l1_y1 = line_1[0][1]
        l1_x2 = line_1[1][0]
        l1_y2 = line_1[1][1]

        l2_x1 = line_2[0][0]
        l2_y1 = line_2[0][1]
        l2_x2 = line_2[1][0]
        l2_y2 = line_2[1][1]

        if (l1_x2 - l1_x1) == 0:
            k1 = None
        else:
            k1 = (l1_y2 - l1_y1) * 1.0 / (l1_x2 - l1_x1)
            b1 = l1_y1 * 1.0 - l1_x1 * k1 * 1.0

        if (l2_x2 - l2_x1) == 0:
            k2 = None
            b2 = 0
        else:
            k2 = (l2_y2 - l2_y1) * 1.0 / (l2_x2 - l2_x1)
            b2 = l2_y1 * 1.0 - l2_x1 * k2 * 1.0

        if k1 is None:
            if not k2 is None:
                x = l1_x1
                y = k2 * l1_x1 + b2
                point_is_exit = True
        elif k2 is None:
            x = l2_x1
            y = k1 * l2_x1 + b1
        elif not k2 == k1:
            x = (b2 - b1) * 1.0 / (k1 - k2)
            y = k1 * x * 1.0 + b1 * 1.0
            point_is_exit = True

        # 確認是否在兩條實線之內

        x = int(x)
        y = int(y)

        # 直接判斷是否在兩條內X Y 範圍內
        x_range_1 = [l1_x1, l1_x2]
        x_range_1.sort()

        x_range_2 = [l2_x1, l2_x2]
        x_range_2.sort()

        y_range_1 = [l1_y1, l1_y2]
        y_range_1.sort()

        y_range_2 = [l2_y1, l2_y2]
        y_range_2.sort()

        if x < x_range_1[0] or x > x_range_1[1]:
            point_is_exit = False

        if x < x_range_2[0] or x > x_range_2[1]:
            point_is_exit = False

        if y < y_range_1[0] or y > y_range_1[1]:
            point_is_exit = False

        if y < y_range_2[0] or y > y_range_2[1]:
            point_is_exit = False

        return point_is_exit, [x, y]

    # 距離
    def distanceCalculate(self, p1, p2):
        """p1 and p2 in format (x1,y1) and (x2,y2) tuples"""
        dis = ((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2) ** 0.5
        return dis

    # 判斷此顏色區域是不規則poly還是curve-like
    # 事先必須已經做完闊值處理，只判斷一個contour
    # TODO　判斷不成功
    def check_curve(self, contour):
        # 計算周長
        perimeter = cv2.arcLength(contour, True)

        # 近似輪廓為多邊形
        epsilon = 0.01 * perimeter
        approx = cv2.approxPolyDP(contour, epsilon, True)

        # 計算多邊形面積比值
        area = cv2.contourArea(contour)
        approx_area = cv2.contourArea(approx)
        ratio = approx_area / area

        # 根據面積比值判斷形狀
        # print(ratio)

        if ratio > 0.95:
            # print("Curve-like Polygon")
            return True
        else:
            return False

    # 是否是綠色三色過度
    def is_green_process(self, block_num):
        block_colors = self.common.block_colorful_colors_info[block_num]
        if len(block_colors) == 3:
            is_green = False
            is_spring_green = False
            is_chartreuse_green = False

            masks = []
            for color_num in range(0, len(block_colors)):
                if block_colors[color_num]["predict"] == "綠色":
                    is_green = True
                    mask = self.get_color_mask(block_num, color_num)
                    masks.append(mask)
                elif block_colors[color_num]["predict"] == "春綠色":
                    is_spring_green = True
                    mask = self.get_color_mask(block_num, color_num)
                    masks.append(mask)
                elif block_colors[color_num]["predict"] == "黃綠色":
                    is_chartreuse_green = True

            if (
                is_green == True
                and is_spring_green == True
                and is_chartreuse_green == True
            ):
                hsv = self.common.picPc_ori_colorful_blocks[block_num]
                stacked_masks = np.zeros((hsv.shape[0], hsv.shape[1]), dtype=np.uint8)
                for mask in masks:
                    stacked_masks = stacked_masks + mask

                return True, stacked_masks

        return False, None

    # 計算 區塊
    def get_img_blocks(self, img):
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        retv, thresh = cv2.threshold(img_gray, 125, 255, 1)
        # 1.計算各區域
        contours, hierarchy = cv2.findContours(
            thresh, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE
        )

        # 轉成PolyPoint
        blocks = []

        for b, cnt in enumerate(contours):
            # 去掉父階層
            if hierarchy[0, b, 3] != -1:
                approx = cv2.approxPolyDP(cnt, 0.001 * cv2.arcLength(cnt, True), True)
                blocks.append(approx)

        result = []

        # 區塊
        for i_block in range(0, len(blocks)):
            line = []
            for pnum in range(0, len(blocks[i_block])):
                p = blocks[i_block][pnum][0]
                line.append(p)
            result.append(line)

        self.common.blocks_colorful_countor = result
        self.common.RobotCumtomerUI.fun_listbox_getblocks()

    def draw_line_points(
        self,
        need_inner,
        img,
        block,
        color_p,
        color_l,
        size_p,
        size_l,
        need_cycle: bool = True,
    ):
        for pnum in range(0, len(block)):
            if need_inner == False:
                p = block[pnum]
            else:
                p = block[pnum][0]

            cv2.circle(img, (int(p[0]), int(p[1])), size_p, color_p, -1)
            if pnum < len(block) - 1:
                p_next = block[pnum + 1]
                cv2.line(
                    img,
                    (int(p[0]), int(p[1])),
                    (int(p_next[0]), int(p_next[1])),
                    color_l,
                    size_l,
                )
                cv2.circle(img, (int(p_next[0]), int(p_next[1])), size_p, color_p, -1)
            elif pnum == len(block) - 1:
                if need_cycle == False:
                    pass
                else:
                    p_next = block[0]
                    cv2.line(
                        img,
                        (int(p[0]), int(p[1])),
                        (int(p_next[0]), int(p_next[1])),
                        color_l,
                        size_l,
                    )
                    cv2.circle(
                        img, (int(p_next[0]), int(p_next[1])), size_p, color_p, -1
                    )

    # 圖像骨架化
    # 事先必須已經做完闊值處理
    # 線搞骨架化得出路徑
    def img_skeletonize(self, imgBin, is_in_contour):
        imgBin[imgBin == 255] = 1

        skeleton01 = morphology.skeletonize(imgBin)
        skeleton = skeleton01.astype(np.uint8) * 255

        skeleton = np.clip(skeleton, 0, 255)
        skeleton = np.array(skeleton, np.uint8)

        # skeleton = cv2.bitwise_not(skeleton)
        skeleton_rgb = cv2.cvtColor(skeleton * 255, cv2.COLOR_GRAY2RGB)
        paths = self.get_image_contours(skeleton, is_in_contour)

        paths = [x.tolist() for x in paths]

        # 獲取裡面的點
        paths_get = []
        for p in paths:
            p_new = []
            for point in p:
                point2 = [float(point[0][0]), float(point[0][1])]
                p_new.append(point2)
            # 原始點要在放進去
            point2 = [float(p_new[0][0]), float(p_new[0][1])]
            p_new.append(point2)

            paths_get.append(p_new)

        # TODO　刪除太近的點
        for line in paths_get:
            i = 0
            while i < len(line):
                j = i + 1
                while j < len(line):
                    if self.dis_2p(line[i], line[j]) < 5:
                        line.pop(j)
                    else:
                        j += 1
                i += 1

        # 畫出路徑
        for line in paths_get:
            self.draw_line_points(
                False, skeleton_rgb, line, (0, 0, 255), (0, 255, 0), 2, 1
            )

        for line in paths_get:
            point_first = [float(line[0][0]), float(line[0][1])]
            line.append(point_first)

        return skeleton_rgb, paths_get

    def get_image_contours(self, image, need_out):
        # 1.計算各區域
        contours, hierarchy = cv2.findContours(
            image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
        )

        # 轉成PolyPoint
        blocks = []
        for b, cnt in enumerate(contours):
            if need_out == False:
                # 去掉父階層
                if hierarchy[0, b, 3] != -1:
                    approx = cv2.approxPolyDP(
                        cnt, 0.0013 * cv2.arcLength(cnt, True), True
                    )
                    blocks.append(approx)
            else:
                approx = cv2.approxPolyDP(cnt, 0.003 * cv2.arcLength(cnt, True), True)
                blocks.append(approx)

        return blocks

    # 彩圖的 block 分圖
    def img_color_check(self, block):
        leftmost = min(block, key=lambda x: x[0])[0]
        rightmost = max(block, key=lambda x: x[0])[0]
        topmost = min(block, key=lambda x: x[1])[1]
        bottommost = max(block, key=lambda x: x[1])[1]

        cropped_img = self.common.picPc_ori_colorful[
            topmost:bottommost, leftmost:rightmost
        ]

        mask = np.zeros_like(self.common.picPc_ori_colorful)
        cv2.fillPoly(mask, [np.array(block)], (255, 255, 255))

        mask = mask[topmost:bottommost, leftmost:rightmost]

        result = cv2.bitwise_and(cropped_img, mask)  # 保留掩膜内的像素

        return result

    # 彩圖的 block 各自顏色區塊判斷(是否是poly或curve-like)
    # 彩圖的 block 各自顏色區塊路徑規劃
    def get_color_mask(self, block_num, color_num):
        # 将图像转换为 HSV 颜色空间
        hsv = cv2.cvtColor(
            self.common.picPc_ori_colorful_blocks[block_num], cv2.COLOR_RGB2HSV
        )
        predict = self.common.block_colorful_colors_info[block_num][color_num][
            "predict"
        ]

        # 創建空的 numpy array，準備堆疊遮罩
        stacked_masks = np.zeros((hsv.shape[0], hsv.shape[1]), dtype=np.uint8)

        for k in self.common.Color_HSV.keys():
            name = self.common.Color_HSV[k]["name"]

            if predict == name:
                l_h = self.common.Color_HSV[k]["range"][0]
                u_h = self.common.Color_HSV[k]["range"][1]
                # 定義顏色範圍
                mask = cv2.inRange(hsv, l_h, u_h)
                stacked_masks = stacked_masks + mask

        # 執行形態學操作
        kernel = np.ones((5, 5), np.uint8)
        # 執行腐蝕操作
        erosion = cv2.erode(stacked_masks, kernel, iterations=1)
        # 執行膨脹操作
        dilation = cv2.dilate(erosion, kernel, iterations=1)

        # opening = cv2.morphologyEx(stacked_masks, cv2.MORPH_OPEN, kernel)
        # closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel)

        return dilation

    def range_color_path(self, block_num, color_num):
        # 各區塊內的單一顏色
        mask = self.get_color_mask(block_num, color_num)

        color_contours = self.get_image_contours(mask, True)

        # 各單一顏色的color_contours
        contour_path = []
        for contour in color_contours:
            # 直接用長寬比例來計算是不是直線(不是正確，先暫用)
            x_min_c = min(point[0][0] for point in contour)
            x_max_c = max(point[0][0] for point in contour)
            y_min_c = min(point[0][1] for point in contour)
            y_max_c = max(point[0][1] for point in contour)

            scale_c = (y_max_c - y_min_c) / (x_max_c - x_min_c)
            if scale_c >= 4:
                print(" not good bone 2------------")

                img_bone, draw_path = self.img_skeletonize(mask, True)

                # 線搞最後會封閉，但這不行，要把後面點移走
                oneline = draw_path[0]
                oneline.pop()
                oneline = sorted(oneline, key=lambda x: x[1])
                draw_path = [oneline]
                # print(f'{oneline}')
            # poly
            else:
                draw_path = self.get_poly_paths(contour)
            # draw_path = self.get_poly_paths(contour)

            # 需要重新計算大圖上的位置
            block = self.common.blocks_colorful_countor[block_num]

            x_min = min(point[0] for point in block)
            x_max = max(point[0] for point in block)
            y_min = min(point[1] for point in block)
            y_max = max(point[1] for point in block)

            for line in draw_path:
                for point in line:
                    point[0] = x_min + point[0]
                    point[1] = y_min + point[1]

            contour_path.append(draw_path)
        return contour_path

    def range_color_special_path(self, block_num, mask):
        # hsv = cv2.cvtColor(self.common.picPc_ori_colorful_blocks[block_num], cv2.COLOR_RGB2HSV)

        # 創建空的 numpy array，準備堆疊遮罩
        # stacked_masks = np.zeros((hsv.shape[0], hsv.shape[1]), dtype=np.uint8)
        # for mask in masks:
        #         stacked_masks = stacked_masks + mask

        # 執行形態學操作
        kernel = np.ones((5, 5), np.uint8)
        # 執行腐蝕操作
        erosion = cv2.erode(mask, kernel, iterations=1)
        # 執行膨脹操作
        dilation = cv2.dilate(erosion, kernel, iterations=1)

        color_contours = self.get_image_contours(dilation, True)

        # 各單一顏色的color_contours
        contour_path = []
        for contour in color_contours:
            draw_path = self.get_poly_paths(contour)

            # 需要重新計算大圖上的位置
            block = self.common.blocks_colorful_countor[block_num]

            x_min = min(point[0] for point in block)
            x_max = max(point[0] for point in block)
            y_min = min(point[1] for point in block)
            y_max = max(point[1] for point in block)

            for line in draw_path:
                for point in line:
                    point[0], point[1] = x_min + point[0], y_min + point[1]

            contour_path.append(draw_path)
        return contour_path

    # Y值畫線
    def takeY(self, elem):
        return elem[1]

    def get_poly_paths(self, contour):
        pan_width = 15
        scale_lines = 8
        p_p_dis = 30  # 最後一條線要再分點

        x, y, w, h = cv2.boundingRect(contour)

        x_min = x
        x_max = x + w
        y_min = y
        y_max = y + h

        if (x_max - x_min) < 3 or (y_max - y_min) < 3:
            # print('太小不做!')
            return None

        x_range = scale_lines * (x_max - x_min)
        x_range_offset = int((x_range - (x_max - x_min)) / 2)
        pan_times = int(x_range / pan_width)

        # y值加大一點(讓線多畫)
        y_max = y_max + 5
        y_min = y_min - 5
        # 筆畫的初步線條
        lines_Ori = []
        offet = -40
        for d_num in range(1, int((pan_times + 1))):
            p1 = [(offet + x_min + d_num * pan_width) - x_range_offset, y_max]  # 下面
            p2 = [(x_min + d_num * pan_width) - x_range_offset, y_min]  # 上面
            lines_Ori.append([p2, p1])

        # 4.找到與範圍的交點，理論上是雙數點
        lines_cross_1 = []
        for line_pan_num in range(0, len(lines_Ori)):
            points_cross = []

            for pnum in range(0, len(contour)):
                if pnum < len(contour) - 1:
                    p1, p2 = contour[pnum][0], contour[pnum + 1][0]
                elif pnum == len(contour) - 1:
                    p1, p2 = contour[pnum][0], contour[0][0]

                point_is_exit, point_cross = self.cross_point(
                    lines_Ori[line_pan_num], [p1, p2]
                )

                if point_is_exit == True:
                    if point_cross not in points_cross:
                        points_cross.append(point_cross)

            if len(points_cross) > 0:
                lines_cross_1.append(points_cross)

        # 實際上會有一些近的點，去除一些比較近的點
        for line in lines_cross_1:
            i = 0
            while i < len(line):
                j = i + 1
                while j < len(line):
                    if self.dis_2p(line[i], line[j]) < 2:
                        line.pop(j)
                    else:
                        j += 1
                i += 1

        # 筆畫線段歸類
        lines_cross_2 = []

        for line_cross in lines_cross_1:
            # 先將各點透過Y值大小排列
            line_cross.sort(key=self.takeY)
            # 歸類各線段
            for pnum in range(0, len(line_cross)):
                # if len(line_cross) %2 ==1:
                #     cv2.circle(self.common.picPc_ori_colorful , ( int(line_cross[pnum][0]) ,int(line_cross[pnum][1])  ), 2, (255,0,0), -1)

                if pnum < len(line_cross) - 1 and (pnum % 2) == 0:
                    line_sub = []
                    line_sub.append(line_cross[pnum])
                    line_sub.append(line_cross[pnum + 1])
                    lines_cross_2.append(line_sub)

        return lines_cross_2

    # --////---------------------------判斷

    def get_frame(self):
        try:
            if self.cap_color is not None:
                ret, frame = self.cap_color.read()

                if ret:
                    frame2 = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    height_f2, width_f2, channels = frame2.shape

                    # 調色盤位置
                    x_start = int(self.common.get_ColorPaletteSize_start[0])
                    x_width = x_start + int(self.common.get_ColorPaletteSize[0])
                    y_start = int(height_f2) - int(
                        self.common.get_ColorPaletteSize_start[1]
                    )
                    y_height = int(height_f2) - (
                        int(self.common.get_ColorPaletteSize_start[1])
                        + int(self.common.get_ColorPaletteSize[1])
                    )

                    frame_plant = frame2[y_height:y_start, x_start:x_width]

                    # # #實際畫圖位置
                    x_start = int(self.common.get_ColorRealSize_start[0])
                    x_width = x_start + int(self.common.get_ColorRealSize[0])
                    y_start = int(height_f2) - int(
                        self.common.get_ColorRealSize_start[1]
                    )
                    y_height = int(height_f2) - (
                        int(self.common.get_ColorRealSize[1])
                        + int(self.common.get_ColorRealSize_start[1])
                    )

                    frame_real = frame2[y_height:y_start, x_start:x_width]

                    # 指定旋轉角度
                    angle = self.common.rotaoteAngle

                    # 指定旋轉中心點
                    center = (frame_real.shape[1] // 2, frame_real.shape[0] // 2)

                    # 設置旋轉矩陣
                    M = cv2.getRotationMatrix2D(center, angle, 1.0)

                    # 執行旋轉操作
                    frame_real = cv2.warpAffine(
                        frame_real, M, (frame_real.shape[1], frame_real.shape[0])
                    )

                    if self.common.is_scale_512 == True:
                        frame_real = cv2.resize(frame_real, (512, 512))

                    # 定义锐化内核
                    kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])

                    # 应用内核
                    frame_real = cv2.filter2D(frame_real, -1, kernel)

                    # # # 进行双边滤波
                    # frame_real = cv2.bilateralFilter(frame_real, 9, 75, 75)

                    # 各區塊顏色
                    for i in range(0, len(self.common.Color_Cells)):
                        x_row = int(i % 4)
                        y_row = int(i / 4)

                        r_x_start = (
                            int(self.common.PalCell_offset[0]) * x_row
                            + int(self.common.PalCell_start[0])
                            + x_row * 10
                            + x_row * int(self.common.PalCell[0])
                        )
                        r_y_start = (
                            int(self.common.PalCell_offset[1]) * y_row
                            + int(self.common.PalCell_start[1])
                            + y_row * 10
                            + y_row * int(self.common.PalCell[1])
                        )
                        r_x_end = (
                            int(self.common.PalCell_offset[0]) * x_row
                            + int(self.common.PalCell_start[0])
                            + (x_row + 1) * 10
                            + (x_row + 1) * int(self.common.PalCell[0])
                        )
                        r_y_end = (
                            int(self.common.PalCell_offset[1]) * y_row
                            + int(self.common.PalCell_start[1])
                            + (y_row + 1) * 10
                            + (y_row + 1) * int(self.common.PalCell[1])
                        )

                        # 新增調色盤上的區塊內顏色
                        frame_color = frame_plant[r_y_start:r_y_end, r_x_start:r_x_end]
                        (
                            Anayzie_image,
                            HSV_Main,
                            Color_Pre,
                        ) = self.Anayzie_Cam_Img_sketch(
                            frame_color,
                            2,
                            self.common.pal_contrast,
                            self.common.pal_brightness,
                        )

                        frame_color_image = PIL.ImageTk.PhotoImage(
                            image=PIL.Image.fromarray(Anayzie_image)
                        )
                        self.common.Color_Cells[i].Image_Array = frame_color
                        self.common.Color_Cells[i].Image = frame_color_image
                        self.common.Color_Cells[i].HSV_Main = HSV_Main
                        self.common.Color_Cells[i].Color_Pre = Color_Pre

                        cv2.rectangle(
                            frame_plant,
                            (r_x_start, r_y_start),
                            (r_x_end, r_y_end),
                            (0, 100, 255),
                            1,
                            cv2.LINE_AA,
                        )

                    # 調色主位置
                    for i in range(0, len(self.common.Pal_main_start)):
                        r_x_start = int(self.common.Pal_main_start[i][0])
                        r_y_start = int(self.common.Pal_main_start[i][1])
                        r_x_end = int(self.common.Pal_main_start[i][0]) + int(
                            self.common.Pal_main[0]
                        )
                        r_y_end = int(self.common.Pal_main_start[i][1]) + int(
                            self.common.Pal_main[1]
                        )

                        frame_color = frame_plant[r_y_start:r_y_end, r_x_start:r_x_end]
                        (
                            Anayzie_image,
                            HSV_Main,
                            Color_Pre,
                        ) = self.Anayzie_Cam_Img_sketch(
                            frame_color,
                            2,
                            self.common.main_color_contrast,
                            self.common.main_color_brightness,
                        )
                        frame_color_image = PIL.ImageTk.PhotoImage(
                            image=PIL.Image.fromarray(Anayzie_image)
                        )
                        self.common.Color_Mains[i].Image_Array = frame_color
                        self.common.Color_Mains[i].Image = frame_color_image
                        self.common.Color_Mains[i].HSV_Main = HSV_Main
                        self.common.Color_Mains[i].Color_Pre = Color_Pre

                        cv2.rectangle(
                            frame_plant,
                            (r_x_start, r_y_start),
                            (r_x_end, r_y_end),
                            (0, 100, 255),
                            1,
                            cv2.LINE_AA,
                        )

                    image_plant = PIL.ImageTk.PhotoImage(
                        image=PIL.Image.fromarray(frame_plant)
                    )

                    self.common.image_pic_real = PIL.ImageTk.PhotoImage(
                        image=PIL.Image.fromarray(frame_real)
                    )

                    return image_plant, self.common.image_pic_real

        except:
            print("get_frame_error")

            return None, None

    def cap_release(self):
        self.cap_color.release()
        cv2.destroyAllWindows()
