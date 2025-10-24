import os
import sys
import main
import time
import push
import config
import random
from loghelper import log
from error import CookieError, StokenError


def find_config(ext: str) -> list:
    """
    搜索指定扩展名的配置文件
    
    Args:
        ext (str): 文件扩展名，如 '.yaml' 或 '.yml'
    
    Returns:
        list: 符合条件的配置文件名列表
    """
    file_name = []
    for files in os.listdir(config.path):
        if os.path.splitext(files)[1] == ext:
            if config.config_prefix == "" or files.startswith(config.config_prefix):
                file_name.append(files)
    return file_name


def ql_config(config_list: list) -> list:
    """
    筛选青龙多用户配置文件（头部匹配）
    
    青龙面板的配置文件通常以 'mhy_' 开头，此函数用于筛选这些文件
    
    Args:
        config_list (list): 配置文件列表
    
    Returns:
        list: 青龙多用户配置文件列表
    """
    config_list_ql = []
    for files in config_list:
        if 'mhy_' == files[:4]:
            config_list_ql.append(files)
    return config_list_ql


def get_config_list() -> list:
    """
    获取所有可用的配置文件列表
    
    搜索 .yaml 和 .yml 文件，并根据环境变量判断是否使用青龙面板模式
    
    Returns:
        list: 配置文件列表
    """
    config_list = find_config('.yaml')
    config_list.extend(find_config('.yml'))
    # 增强环境变量处理，添加更多的错误处理和默认值
    config_prefix = os.getenv("AutoMihoyoBBS_config_prefix")
    config_multi = os.getenv("AutoMihoyoBBS_config_multi", "0")
    ql_dir = os.getenv("QL_DIR")
    
    if config_prefix is None and config_multi == '1':
        # 判断通过读取青龙目录环境变量来判断用户是否使用青龙面板
        if ql_dir is not None:
            config_list = ql_config(config_list)
    if len(config_list) == 0:
        log.warning("未检测到配置文件，请确认 config 文件夹存在 .yaml/.yml 后缀名的配置文件！")
        exit(1)
    return config_list


def main_multi(autorun: bool) -> tuple:
    """
    多用户模式主执行函数
    
    依次执行所有配置文件的任务，并汇总结果
    
    Args:
        autorun (bool): 是否自动运行，False 时会等待用户确认
    
    Returns:
        tuple: (状态码, 推送消息)
            状态码：
            0 - 全部成功
            1 - 全部失败
            2 - 部分失败
            3 - 有验证码触发
    """
    log.info("AutoMihoyoBBS Multi User mode")
    log.info("正在搜索配置文件！")
    config_list = get_config_list()
    if autorun:
        log.info(f"已搜索到 {len(config_list)} 个配置文件，正在开始执行！")
    else:
        log.info(f"已搜索到 {len(config_list)} 个配置文件，请确认是否无多余文件！\r\n{config_list}")
        try:
            input("请输入回车继续，需要重新搜索配置文件请 Ctrl+C 退出脚本")
        except KeyboardInterrupt:
            exit(0)
    results = {"ok": [], "close": [], "error": [], "captcha": []}
    detailed_messages = []  # 存储每个账号的详细签到信息

    for i in config_list:
        log.info(f"正在执行 {i}")
        config.config_Path = os.path.join(config.path, i)

        # 获取账号配置用于推送消息
        config.load_config(config.config_Path)
        account_name = i.replace('.yaml', '').replace('config', '主账号').replace('account', '账号')

        try:
            run_code, run_message = main.main()
        except (CookieError, StokenError) as e:
            results["error"].append(i)
            error_msg = "账号 Cookie 出错！" if isinstance(e, CookieError) else "账号 Stoken 有问题！"
            detailed_messages.append(f"【{account_name}】\n❌ {error_msg}")
            if config.config.get("push", "") != "":
                push_handler = push.PushHandler(config.config["push"])
                push_handler.push(1, error_msg)
        else:
            # 增强对返回值的处理，确保所有可能的情况都被考虑到
            if run_code == 0:
                results["ok"].append(i)
                detailed_messages.append(f"【{account_name}】\n✅ 签到成功\n{run_message}")
            elif run_code == 1 or run_code == 2:
                # 处理明确的失败状态
                results["error"].append(i)
                detailed_messages.append(f"【{account_name}】\n❌ 签到失败\n{run_message}")
            elif run_code == 3:
                results["captcha"].append(i)
                detailed_messages.append(f"【{account_name}】\n⚠️ 触发验证码\n{run_message}")
            else:
                # 其他未知状态归类为未执行
                results["close"].append(i)
                detailed_messages.append(f"【{account_name}】\n⏸ 未执行")
        log.info(f"{i} 执行完毕")

        time.sleep(random.randint(3, 10))

    print("")
    # 生成详细的推送消息
    summary = f'📊 执行概览\n共 {len(config_list)} 个账号，成功 {len(results["ok"])} 个，失败 {len(results["error"])} 个，未执行 {len(results["close"])} 个'
    if len(results["captcha"]) > 0:
        summary += f'，触发验证码 {len(results["captcha"])} 个'

    push_message = summary + '\n\n' + '\n\n'.join(detailed_messages)
    log.info(push_message)
    # 更清晰的状态码逻辑
    status = 0  # 默认成功
    if len(results["error"]) == len(config_list):
        status = 1  # 全部失败
    elif len(results["error"]) != 0:
        status = 2  # 部分失败
    elif len(results["captcha"]) != 0:
        status = 3  # 有验证码触发
    
    return status, push_message


if __name__ == "__main__":
    if (len(sys.argv) >= 2 and sys.argv[1] == "autorun") or os.getenv("AutoMihoyoBBS_autorun") == "1":
        autorun_flag = True
    else:
        autorun_flag = False
    task_status, task_push_message = main_multi(autorun_flag)
    # 使用 PushHandler 实例，保持与其他推送处理方式一致
    push_handler = push.PushHandler()
    push_handler.push(task_status, task_push_message)
    exit(0)
