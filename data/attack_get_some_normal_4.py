import pandas as pd
import os
import numpy as np


def sample_and_merge(source_file, target_file, sample_ratio=0.1):
    """
    从源CSV随机抽取数据并追加到目标CSV
    :param source_file: 源CSV文件路径
    :param target_file: 目标CSV文件路径
    :param sample_ratio: 抽样比例（默认为0.1）
    """
    # 读取源文件数据
    source_df = pd.read_csv(source_file)

    # 计算抽样数量（至少1行）
    sample_size = max(1, int(len(source_df) * sample_ratio))

    # 随机抽样[1](@ref)
    sampled_df = source_df.sample(n=sample_size, random_state=np.random.randint(100))

    # 追加到目标文件
    if os.path.exists(target_file):
        # 追加模式（不写入列名）
        sampled_df.to_csv(target_file, mode='a', header=False, index=False)
    else:
        # 新文件写入列名
        sampled_df.to_csv(target_file, index=False)

    print(f"成功从 {source_file} 抽取 {sample_size} 行数据追加到 {target_file}")


# 使用示例
if __name__ == "__main__":
    source_csv = "normal10.csv"  # 替换为你的源文件路径
    target_csv = "attack0.csv"  # 替换为你的目标文件路径

    sample_and_merge(source_csv, target_csv, sample_ratio=0.05)