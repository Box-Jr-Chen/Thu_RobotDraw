# 單線段-多個多筆組(groups_pens)
from dataclasses import dataclass
from .pen import pen

@dataclass
class line :
    def __init__(self):
        self.groups_pens:list[pen] =[]
