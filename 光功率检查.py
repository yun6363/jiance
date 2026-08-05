# -*- coding: utf-8 -*-
import pandas as pd
import os

def parse_power_value(value):
    """解析接收光功率字段，支持单值或多值（逗号分隔），返回平均值（浮点数）。"""
    if pd.isna(value):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        value = value.strip()
        if not value:
            return None
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
            try:
                return float(value)
            except ValueError:
                return None
    return None

def check_power(avg, upper, lower):
    """
    根据平均值和上下限判断状态。
    返回：'正常', '异常-光强', '异常-光弱', '丢弃' 或 None（数据不足）
    """
    if avg is None:
        return None
    # 特殊值 -40 直接丢弃（不参与范围判断）
    if abs(avg + 40.0) < 1e-6:
        return '丢弃'
    # 若上下限缺失，无法判断
    if pd.isna(upper) or pd.isna(lower):
        return None
    # 严格判断：下限 < avg < 上限 为正常，否则按超上限或低下限细分
    if lower < avg < upper:
        return '正常'
    elif avg >= upper:
        return '异常-光强'
    elif avg <= lower:
        return '异常-光弱'
    else:
        # 理论不会到这里，但以防万一
        return '异常'

def process_excel(input_file):
    """处理单个 Excel 文件，添加结果列并保存为新文件。"""
    df = pd.read_excel(input_file, sheet_name=0, header=0)
    col_rx = '接收光功率(dBm)'
    col_upper = '接收光功率上限(dBm)'
    col_lower = '接收光功率下限(dBm)'
    
    if not all(col in df.columns for col in [col_rx, col_upper, col_lower]):
        raise ValueError(f'文件中缺少以下列之一：{col_rx}, {col_upper}, {col_lower}')
    
    result_col = '光功率检查结果'
    if result_col in df.columns:
        df = df.drop(columns=[result_col])
    
    def row_check(row):
        avg = parse_power_value(row[col_rx])
        upper = row[col_upper]
        lower = row[col_lower]
        return check_power(avg, upper, lower)
    
    df[result_col] = df.apply(row_check, axis=1)
    
    base, ext = os.path.splitext(input_file)
    output_file = f'{base}_检查结果{ext}'
    df.to_excel(output_file, index=False)
    print(f'✅ 处理完成，结果保存至：{output_file}')

def main():
    print('=' * 50)
    print('光功率检查工具 v2.0')
    print('判断规则：')
    print('  正常   ：下限 < 平均值 < 上限')
    print('  异常-光强：平均值 ≥ 上限')
    print('  异常-光弱：平均值 ≤ 下限')
    print('  丢弃   ：平均值 = -40')
    print('多值格式：x,x,x 自动取平均值')
    print('=' * 50)
    while True:
        file_path = input('\n请输入 Excel 文件名（含扩展名，输入 q 退出）: ').strip()
        if file_path.lower() == 'q':
            print('退出程序。')
            break
        if not os.path.isfile(file_path):
            print(f'❌ 文件 "{file_path}" 不存在，请重新输入。')
            continue
        try:
            process_excel(file_path)
        except Exception as e:
            print(f'❌ 处理出错：{e}')

if __name__ == '__main__':
    main()
