import csv
import os
import re
from datetime import datetime, timedelta
from collections import defaultdict


def parse_metrics_file(file_path):
    """
    解析原始指标文件，返回结构化的时间序列数据
    返回值: [(timestamp, { (metric_name, labels): value }), ...]
    """
    data_blocks = []
    current_timestamp = None
    current_metrics = {}
    current_metric_type = {}

    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            # 解析时间戳行
            if line.startswith("# TIMESTAMP:"):
                if current_timestamp:  # 保存上一个块
                    data_blocks.append((current_timestamp, current_metrics))
                ts_str = line.split(":", 1)[1].strip()
                current_timestamp = datetime.fromisoformat(ts_str)
                current_metrics = {}
                current_metric_type = {}
            # 解析指标类型
            elif line.startswith("# TYPE"):
                parts = line.split()
                if len(parts) >= 4:  # TYPE <name> <type>
                    metric_name = parts[2]
                    metric_type = parts[3]
                    current_metric_type[metric_name] = metric_type
            # 解析指标值
            elif line and not line.startswith("#"):
                # 处理带标签的指标: metric{label="value"} 123.45
                if "{" in line:
                    name_part, rest = line.split("{", 1)
                    metric_name = name_part.strip()
                    labels_part, value_part = rest.split("}", 1)
                    labels = {}
                    for pair in labels_part.split(","):
                        if "=" in pair:
                            key, val = pair.split("=", 1)
                            labels[key.strip()] = val.strip('"')
                    value = float(value_part.strip())
                # 处理无标签指标
                else:
                    parts = line.split()
                    metric_name = parts[0]
                    value = float(parts[1])
                    labels = {}

                # 记录指标值及类型
                metric_type_val = current_metric_type.get(metric_name, "untyped")
                current_metrics[(metric_name, frozenset(labels.items()))] = {
                    "value": value,
                    "type": metric_type_val
                }

    # 添加最后一个块
    if current_timestamp:
        data_blocks.append((current_timestamp, current_metrics))
    return data_blocks


def aggregate_time_windows(data_blocks, window_seconds=5):
    """
    按时间窗口聚合指标数据
    返回值: [{"start": datetime, "end": datetime, "metrics": {metric_key: agg_value}},...]
    """
    if not data_blocks:
        return []

    # 按时间排序
    data_blocks.sort(key=lambda x: x[0])

    # 确定时间范围
    min_time = data_blocks[0][0]
    max_time = data_blocks[-1][0]

    # 创建时间窗口
    window_sec = window_seconds
    current_start = min_time
    windows = []

    while current_start <= max_time:
        window_end = current_start + timedelta(seconds=window_sec)
        windows.append({
            "start": current_start,
            "end": window_end,
            "metrics": defaultdict(list)  # {(name, labels): [values]}
        })
        current_start = window_end

    # 分配数据点到时间窗口
    for ts, metrics in data_blocks:
        for window in windows:
            if window["start"] <= ts < window["end"]:
                for metric_key, metric_data in metrics.items():
                    window["metrics"][metric_key].append(metric_data["value"])
                break

    # 计算聚合值
    for window in windows:
        agg_metrics = {}
        for metric_key, values in window["metrics"].items():
            name, labels = metric_key
            metric_type = "untyped"  # 默认值
            for _, m in data_blocks:
                if metric_key in m:
                    # 增加键存在检查
                    if "type" in m[metric_key]:
                        metric_type = m[metric_key]["type"]
                        break

            if not values:
                agg_value = float('nan')
            elif metric_type == "counter":
                # 处理计数器重置
                total = 0
                last = values[0]
                for val in values[1:]:
                    if val >= last:
                        total += val - last
                    else:  # 计数器重置
                        total += last
                    last = val
                agg_value = total
            else:  # gauge/untyped
                agg_value = sum(values) / len(values)  # 平均值

            # 构建可读的指标字符串
            label_str = ",".join(f"{k}={v}" for k, v in labels)
            metric_id = f"{name}{{{label_str}}}"
            agg_metrics[metric_id] = agg_value

        window["metrics"] = agg_metrics

    return windows


def export_windowed_csv(windows, output_file):
    """导出CSV格式的时间窗口数据"""
    all_metrics = set()
    for window in windows:
        all_metrics.update(window["metrics"].keys())

    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        # 写入表头
        headers = ["window_start", "window_end"] + sorted(all_metrics)
        writer.writerow(headers)

        # 写入每行数据
        for window in windows:
            row = [
                window["start"].isoformat(),
                window["end"].isoformat()
            ]
            for metric in headers[2:]:
                row.append(window["metrics"].get(metric, ""))
            writer.writerow(row)


# 主处理流程
def process_metrics(input_file, output_csv, window_seconds=5):
    print(f"处理文件: {input_file}")
    print("步骤1: 解析原始指标数据...")
    data_blocks = parse_metrics_file(input_file)
    print(f"解析完成，共 {len(data_blocks)} 个时间点数据")

    print(f"步骤2: 按 {window_seconds} 秒窗口聚合数据...")
    windows = aggregate_time_windows(data_blocks, window_seconds)
    print(f"生成 {len(windows)} 个时间窗口")

    print(f"步骤3: 导出CSV: {output_csv}")
    export_windowed_csv(windows, output_csv)
    print("处理完成！")


# 使用示例
if __name__ == "__main__":
    # 配置参数

    all_files=os.listdir(os.getcwd())
    for file in all_files:
        if '.txt' in file:
            print(file)
            INPUT_FILE = file #"prometheus_metrics_2025060523.txt"  # 采集的数据文件
            if not os.path.exists("windowed_metrics/normal1"):
                os.mkdir("windowed_metrics/normal1")
            OUTPUT_CSV = "windowed_metrics/normal1/" + INPUT_FILE.replace('.txt', '.csv')
            window_seconds = 2  # 时间窗口大小（秒）

            process_metrics(INPUT_FILE, OUTPUT_CSV, window_seconds)

