
from enum import Enum
# 需要执行的功能
class ExecTypes(Enum):
    login = 0b1
    group_join      = 0b1 << 1
    group_info      = 0b1 << 2
    group_kick      = 0b1 << 3

    send_text       = 0b1 << 4
    receive_text    = 0b1 << 5
    others          = 0b1 << 6
