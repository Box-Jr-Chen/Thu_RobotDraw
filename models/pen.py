from dataclasses import dataclass

# 單筆路徑
@dataclass
class pen :
    def __init__(self):
        self.point_start =[0,0,0]
        self.point_precess =[]
        self.point_end =[0,0,0]
