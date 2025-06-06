import pandas as pd
import numpy as np
import re
from sklearn.preprocessing import MinMaxScaler


def calculate_cpu_utilization(df):
    """计算整体CPU利用率"""
    # 提取所有CPU时间列
    cpu_cols = [col for col in df.columns if 'node_cpu_seconds_total' in col]

    # 计算总CPU时间（所有核心所有状态）
    df['cpu_total'] = df[cpu_cols].sum(axis=1)

    # 提取空闲时间列（idle状态）
    idle_cols = [col for col in cpu_cols if 'mode=idle' in col]
    df['cpu_idle'] = df[idle_cols].sum(axis=1)

    # 计算CPU利用率 = 1 - (空闲时间/总时间)
    df['cpu_util'] = 1 - (df['cpu_idle'] / df['cpu_total'])

    # 清理临时列
    df.drop(['cpu_total', 'cpu_idle'] + cpu_cols, axis=1, inplace=True, errors='ignore')
    return df


def calculate_memory_utilization(df):
    """计算内存利用率"""
    # 动态检测内存指标
    mem_avail_cols = [col for col in df.columns
                      if re.search(r'node_memory_(MemAvailable|available)_bytes', col)]
    mem_total_cols = [col for col in df.columns
                      if re.search(r'node_memory_(MemTotal|total)_bytes', col)]

    if mem_avail_cols and mem_total_cols:
        mem_avail = mem_avail_cols[0]
        mem_total = mem_total_cols[0]
        df['mem_util'] = 1 - (df[mem_avail] / df[mem_total])
    else:
        # 备用方案：使用空闲内存计算
        mem_free = [col for col in df.columns
                    if re.search(r'node_memory_(MemFree|free)_bytes', col)]
        if mem_free and mem_total_cols:
            df['mem_util'] = 1 - (df[mem_free[0]] / df[mem_total_cols[0]])
        else:
            # 最终备用方案：使用0填充
            df['mem_util'] = 0

    # 清理原始内存列
    mem_cols = [col for col in df.columns if 'node_memory_' in col]
    df.drop(mem_cols, axis=1, inplace=True, errors='ignore')
    return df


def calculate_disk_io(df):
    """计算磁盘I/O综合指标"""
    # 初始化指标
    df['disk_read_mbps'] = 0
    df['disk_write_mbps'] = 0

    # 遍历所有磁盘设备
    for device in ['sda', 'sdb', 'sdc', 'sdd', 'sde']:
        read_col = f'node_disk_read_bytes_total{{device={device}}}'
        write_col = f'node_disk_written_bytes_total{{device={device}}}'

        if read_col in df.columns:
            # 转换为MB/s (假设时间窗口为2秒)
            df['disk_read_mbps'] += df[read_col] / (1024 ** 2) / 2
        if write_col in df.columns:
            df['disk_write_mbps'] += df[write_col] / (1024 ** 2) / 2

    # 清理原始磁盘列
    disk_cols = [col for col in df.columns if 'node_disk_' in col]
    df.drop(disk_cols, axis=1, inplace=True, errors='ignore')
    return df


def calculate_network_utilization(df):
    """计算网络综合指标"""
    # 接收和发送总量
    rx_cols = [col for col in df.columns if 'node_network_receive_bytes_total' in col]
    tx_cols = [col for col in df.columns if 'node_network_transmit_bytes_total' in col]

    if rx_cols:
        df['net_rx_mbps'] = df[rx_cols].sum(axis=1) / (1024 ** 2) / 2  # MB/s
    if tx_cols:
        df['net_tx_mbps'] = df[tx_cols].sum(axis=1) / (1024 ** 2) / 2  # MB/s

    # 清理原始网络列
    net_cols = [col for col in df.columns if 'node_network_' in col]
    df.drop(net_cols, axis=1, inplace=True, errors='ignore')
    return df


def calculate_filesystem_utilization(df):
    """计算文件系统使用率"""
    # 提取所有文件系统指标
    avail_cols = [col for col in df.columns if 'node_filesystem_avail_bytes' in col]
    size_cols = [col for col in df.columns if 'node_filesystem_size_bytes' in col]

    if avail_cols and size_cols:
        # 计算整体使用率（加权平均）
        total_avail = df[avail_cols].sum(axis=1)
        total_size = df[size_cols].sum(axis=1)
        df['fs_util'] = 1 - (total_avail / total_size)

    # 清理原始文件系统列
    fs_cols = [col for col in df.columns if 'node_filesystem_' in col]
    df.drop(fs_cols, axis=1, inplace=True, errors='ignore')
    return df


def handle_nan_values(df):
    """处理NaN值（优化版，支持多行连续NaN处理）"""
    # 记录原始列
    original_cols = df.columns

    # 策略1：时间窗口信息列 - 双向填充
    win_cols = [col for col in df.columns if col.startswith('window_')]
    if win_cols:
        # 双向填充：先向前填充，再向后填充
        df[win_cols] = df[win_cols].ffill().bfill()

    # 策略2：标签列 - 特殊处理
    if 'Normal/Attack' in df.columns:
        # 用'Normal'填充NaN，保留原有非NaN值
        df['Normal/Attack'] = df['Normal/Attack'].fillna('Normal')

    # 策略3：系统指标列 - 智能填充
    sys_cols = [col for col in df.columns
                if not col.startswith(('window_', 'Normal/Attack'))
                and col in original_cols]

    for col in sys_cols:
        # 时间序列插值（适合连续多行NaN）
        if pd.api.types.is_numeric_dtype(df[col]):
            # 线性插值处理连续NaN
            df[col] = df[col].interpolate(method='linear', limit_direction='both')
            # 剩余NaN用列均值填充
            df[col].fillna(df[col].mean(), inplace=True)
        else:
            # 非数值型用众数填充
            mode_value = df[col].mode()[0] if not df[col].mode().empty else 'unknown'
            df[col].fillna(mode_value, inplace=True)

    # 确保没有新列被添加
    return df[original_cols]

def normalize_data(df):
    """数据归一化到[0,1]范围"""
    # 标识列不参与归一化
    meta_cols = ['window_start', 'window_end', 'Normal/Attack']
    feature_cols = [col for col in df.columns if col not in meta_cols]

    if feature_cols:
        scaler = MinMaxScaler()
        df[feature_cols] = scaler.fit_transform(df[feature_cols])

    return df


def process_data(input_file, output_file):
    """完整数据处理流程"""
    # 读取数据
    df = pd.read_csv(input_file)

    # 处理NaN值（优先处理）
    df = handle_nan_values(df)

    # 特征工程
    df = calculate_cpu_utilization(df)
    df = calculate_memory_utilization(df)
    df = calculate_disk_io(df)
    df = calculate_network_utilization(df)
    df = calculate_filesystem_utilization(df)

    # 保留系统负载指标
    load_cols = [col for col in df.columns if 'node_load' in col]
    other_cols = ['window_start', 'window_end', 'Normal/Attack']
    keep_cols = other_cols + load_cols + [
        'cpu_util', 'mem_util',
        'disk_read_mbps', 'disk_write_mbps',
        'net_rx_mbps', 'net_tx_mbps',
        'fs_util'
    ]

    # 筛选最终列
    final_cols = [col for col in keep_cols if col in df.columns]
    df = df[final_cols]

    # 数据归一化
    df = normalize_data(df)

    # 重采样为10秒窗口（新增部分）
    new_rows = []
    n = len(df)
    step = 5  # 5个2秒窗口 = 10秒
    for i in range(0, n, step):
        if i + step <= n:
            # 获取当前10秒窗口的5个样本
            chunk = df.iloc[i:i + step].copy()

            # 创建新行数据
            new_row = {
                'window_start': chunk['window_start'].iloc[0],  # 窗口起始时间取第一个样本
                'window_end': chunk['window_end'].iloc[-1],  # 窗口结束时间取最后一个样本
                'Normal/Attack': 'Attack' if (chunk['Normal/Attack'] == 'Attack').any() else 'Normal'
            }

            # 计算数值列的平均值（排除元数据列）
            num_cols = [col for col in chunk.columns if col not in other_cols]
            for col in num_cols:
                new_row[col] = chunk[col].mean()

            new_rows.append(new_row)

    # 创建重采样后的DataFrame
    resampled_df = pd.DataFrame(new_rows)

    # 保存处理后的数据
    resampled_df.to_csv(output_file, index=False)
    print(f"处理完成！原始维度: {len(pd.read_csv(input_file).columns)} → 处理后维度: {len(resampled_df.columns)}")
    print(f"时间窗口重采样: {len(df)}个2秒窗口 → {len(resampled_df)}个10秒窗口")
    return resampled_df


# 使用示例
if __name__ == "__main__":
    # input_file = "attack.csv"
    # output_file = "attack0.csv"
    # process_data(input_file, output_file)
    # input_file = "normal.csv"
    # output_file = "normal0.csv"
    # process_data(input_file, output_file)
    input_file = "normal1.csv"
    output_file = "normal10.csv"
    process_data(input_file, output_file)
