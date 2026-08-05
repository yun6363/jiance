import pandas as pd
import re
import os
import sys

def parse_power_value(value):
    """
    解析接收光功率字段，支持单值或多值（逗号分隔），返回平均值（浮点数）。
    若无法解析则返回 None。
    """
    if pd.isna(value):
        return None
    # 如果是数值类型，直接转换
    if isinstance(value, (int, float)):
        return float(value)
    # 字符串处理
    if isinstance(value, str):
        # 去除首尾空格
        value = value.strip()
        if not value:
            return None
        # 如果包含逗号，则分割
        if ',' in value:
            parts = [p.strip() for p in value.split(',') if p.strip()]
            nums = []
            for p in parts:
                try:
                    nums.append(float(p))
                except ValueError:
                    continue
            if not nums:
                return None
            return sum(nums) / len(nums)
        else:
            # 单个数字
            try:
                return float(value)
            except ValueError:
                return None
    return None


def check_power(avg, upper, lower):
    """
    根据平均值、上下限进行判断。
    返回：'正常'、'异常'、'丢弃' 或 None（当数据缺失时）
    """
    if avg is None:
        return None
    # 特殊值 -40 标记为丢弃（严格相等，浮点比较）
    if abs(avg + 40.0) < 1e-6:
        return '丢弃'
    # 若上下限缺失，则无法判断
    if pd.isna(upper) or pd.isna(lower):
        return None
    # 判断是否在范围内（下限 < 平均值 < 上限）
    if lower < avg < upper:
        return '正常'
    else:
        return '异常'


def process_excel(input_file):
    """
    处理单个 Excel 文件，添加结果列并保存为新文件。
    """
    # 读取第一个 sheet
    df = pd.read_excel(input_file, sheet_name=0, header=0)
    # 定义列名（基于样本数据）
    col_rx = '接收光功率(dBm)'
    col_upper = '接收光功率上限(dBm)'
    col_lower = '接收光功率下限(dBm)'
    # 检查必要列是否存在
    如果 不是所有(列 在 df.列名中针对 列 [col_rx, col_upper, col_lower]):
        raise ValueError(f'文件中缺少以下列之一：{col_rx}, {col_upper}, {col_lower}')

    # 新建结果列（M列）
    result_col = '光功率检查结果'
    如果 result_col 在 df.列:
        df = df.删除(columns=[result_col])

    # 逐行计算
    def row_check(row):
        avg = parse_power_value(row[col_rx])
        upper = row[col_upper]
        lower = row[col_lower]
        return check_power(avg, upper, lower)

    df[result_col] = df.apply(row_check, axis=1)

    # 生成输出文件名
    base, ext = os.path.splitext(input_file)
    output_file = f'{base}_检查结果{ext}'
    df.to_excel(output_file, index=False)
    print(f'✅ 处理完成，结果保存至：{output_file}')


def main():
    print('=' * 50)
    print('光功率检查工具 v1.0')
    print('支持列：接收光功率(dBm) | 接收光功率上限(dBm) | 接收光功率下限(dBm)')
    print('多值格式：x,x,x 将自动取平均值')
    print('平均值 = -40 时标记为“丢弃”')
    print('=' * 50)
    当 真:
        file_path = input('\n请输入 Excel 文件名（含扩展名，输入 q 退出）: ').strip()
        如果 file_path.lower() == 'q':
            打印('退出程序。')
             break
        如果 不是 os.path.isfile(file_path):
            打印(f'❌ 文件 "{file_path}" 不存在，请重新输入。')
             continue
        尝试:
            process_excel(file_path)
        except Exception as e:
            print(f'❌ 处理出错：{e}')


如果 __name__ == '__main__':
    主函数()
