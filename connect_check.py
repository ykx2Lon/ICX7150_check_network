
import sys
import os
from dotenv import load_dotenv
from netmiko import ConnectHandler, BaseConnection
from ping3 import ping, verbose_ping
import time
from typing import List, Optional
import datetime

# --- 設定 ---
HOST = "8.8.8.8"  # 檢查連線的目標 (Google DNS)
PORT = 53          # 檢查的埠號 (DNS 常用 53)
TIMEOUT = 3        # 逾時秒數


# 1. 儲存原始的 stdout (以便之後恢復)
original_stdout = sys.stdout 

# 2. 開啟您要寫入的檔案
# 'a' 是附加模式 (append)，'w' 是覆蓋模式 (write)
log_file = open('D:/net_log/print_log.txt', 'a', encoding='utf-8')

# 3. 將 stdout 重定向到檔案
sys.stdout = log_file


 # 檢查連線的目標 (Google DNS)
# -------------
trouble_prot = -1
def check_connection(ip = HOST):
    """
    嘗試連線到指定的 host 和 port，檢查網路是否暢通。
    """
    delay = ping(ip)
    return delay is not None

# port_str 為 interface ethernet 後面接的port name，可以是範圍。ex:"1/1/3 to 1/1/16" 或只有 "1/1/3"
def conn_operate_interface(conn: BaseConnection, port_str, operate_str):
    if(not  port_str):
        raise Exception("port_str cannot be empty")
    if(not  operate_str):
        raise Exception("operate_str cannot be empty")
        
    # 若目前不在config mode，須先進入
    if conn.check_config_mode() is False:
        conn.config_mode()
    
    conn.send_command(f"interface ethernet {port_str}")
    conn.send_command(operate_str)
    conn.send_command("write memory")
    
def conn_check_ping_success(conn: BaseConnection,target_ip):
    if conn.check_config_mode():
        conn.exit_config_mode()
    output = conn.send_command("ping "+target_ip, cmd_timeout=30)
    if "Success rate is 100 percent" in output:
        return True
    return False



def range_strings(n: int, max_port: int = 24) -> List[str]:
    """
    回傳排除 n 的兩段日期範圍（左段 1..n-1、右段 n+1..max_day）。
    - 空段會被省略（不回傳）
    - 單一天會輸出 '1/1/X'
    - 多天會輸出 '1/1/A to 1/1/B'
    """
    def fmt(a: int, b: int) -> Optional[str]:
        if a > b:
            return None           # 空段：省略
        if a == b:
            return f"1/1/{a}"     # 單一天
        return f"1/1/{a} to 1/1/{b}"

    left  = fmt(1, n - 1)
    right = fmt(n + 1, max_port)
    return [s for s in (left, right) if s is not None]

def checkL2toL3(main_port = 2):
    load_dotenv(verbose=True, override=True)
    dev = {
    "device_type": "ruckus_fastiron",
    "host": os.getenv('L2_IP'),
    "username": os.getenv('L2_USER_NAME'),
    "use_keys": False,
    "password": os.getenv('L2_USER_PWD'),      
    "fast_cli": True,     # 加快互動
    "global_delay_factor": 1.0,
    "secret":os.getenv('L2_ENABLE_PWD'),
    "session_log": "netmiko_session.log",
    }
    exp_str = os.getenv('L2_SWITCH_NAME')+'#'
    with ConnectHandler(**dev) as conn:
        print(f"成功連線至{os.getenv('L2_IP')}")
        conn.enable()
        conn.send_command("skip-page-display") # skip-page-display:ruckus指令，關閉CLI分頁，下次輸入指令會一次吐完，不會有 --More--（此指令需enable。
        ping_success = conn_check_ping_success(conn, os.getenv('L3_IP'))
        print(ping_success)
        if ping_success:
            print("L2 至 2F_L3 switch連線正常，目前應為全館斷線狀態。請檢查L3對外連線")
            return 0 
        print("L2 與 L3連線異常")
        # disable main_port以外的全部
        close_ports = range_strings(main_port)
        map(lambda s: close_ports(conn, s, "disalbe"), close_ports)
        time.sleep(90)
        # 重ping確認
        ping_success = conn_check_ping_success(conn, os.getenv('L3_IP'))
        print(f"ping 結果:{ping_success}")
        if ping_success:
            print("確定為某個port造成的問題")
            print("開始將其他 port 逐個 enable")
            # 每個開始enable，記錄從哪一個開始ping不到
            disconnect = False
            global trouble_prot
            for trouble_prot in range(1,25):
                # 跳過當前本script所在Lab
                if trouble_prot == main_port:
                    continue
                conn_operate_interface(conn, f"1/1/{trouble_prot}", "enable")
                time.sleep(30)
                output = conn.send_command("ping "+os.getenv('L3_IP'), expect_string=exp_str, cmd_timeout=30)
                if "Success rate is 100 percent" not  in output:
                    disconnect = True
                    break
        if disconnect:
            print(f"有問題的port 為{trouble_prot}")
        else:
            print("本次未發現有問題的port")
        conn_operate_interface(conn, f"1/1/1 to 1/1/24", "enable")

        return False

    

# --- 主程式 ---
if __name__ == '__main__':

    # 檢查當前是否可以順利連線到網際網路
    
    can_connect = check_connection()
    if(can_connect):
        print(f"{datetime.datetime.now()}"+" 正常")
        sys.exit()
    # 檢查L2是否可正常連線到L3
    # 若無法連線到網際網路，進入 L2 斷開其他port的連線
    checkL2toL3()


    


    

