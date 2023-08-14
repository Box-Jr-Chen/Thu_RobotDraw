# 單顏色區塊-多線條
from dataclasses import dataclass
from .line import line

@dataclass
class block_color :
    def __init__(self):
        #block 裡面分顏色，顏色裡面才有線
        self.groups_pens:list[list[line]] =[]
