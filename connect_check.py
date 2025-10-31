import socket
import platform
import subprocess
import datetime
import sys
import os

# --- 設定 ---
HOST = "8.8.8.8"  # 檢查連線的目標 (Google DNS)
PORT = 53          # 檢查的埠號 (DNS 常用 53)
TIMEOUT = 3        # 逾時秒數
# -------------

def check_connection(host=HOST, port=PORT, timeout=TIMEOUT):
    """
    嘗試連線到指定的 host 和 port，檢查網路是否暢通。
    """
    try:
        socket.setdefaulttimeout(timeout)
        # 建立一個 TCP socket
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error as ex:
        # print(f"連線失敗: {ex}") # 用於除錯
        return False

def connect_122():
    dev = {
    "device_type": "ruckus_fastiron",
    "host": os.getenv('L3_IP'),
    "username": os.getenv('L3_USER_NAME'),
    "use_keys": False,
    "password": os.getenv('L3_USER_PWD'),      
    "fast_cli": True,     # 加快互動
    "global_delay_factor": 1.0,
    "secret":os.getenv('L3_ENABLE_PWD'),
    "session_log": "netmiko_session.log",
    }

# --- 主程式 ---
if __name__ == '__main__':
    # 檢查是否可以順利連線
    can_connect = check_connection()
    if(can_connect):
        sys.exit()
    
    # 無法連線，進入 140.123.106.253斷開其他port的連線
    dev = {
    "device_type": "ruckus_fastiron",
    "host": os.getenv('L3_IP'),
    "username": os.getenv('L3_USER_NAME'),
    "use_keys": False,
    "password": os.getenv('L3_USER_PWD'),      
    "fast_cli": True,     # 加快互動
    "global_delay_factor": 1.0,
    "secret":os.getenv('L3_ENABLE_PWD'),
    "session_log": "netmiko_session.log",
}


    

