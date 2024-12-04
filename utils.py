from datetime import datetime


def print_current_time(step: int):
    """返回当前时间，精确到毫秒，格式：YYYY-MM-DD HH:MM:SS.mmm"""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.") + f"{datetime.now().microsecond // 1000:03d}"
    # 调用函数并打印当前时间
    print(f"step:{step} 当前时间: {current_time}")
