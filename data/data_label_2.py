import os

import pandas as pd


def add_attack_column(input_file, output_file, attack_status='Normal',is_first_file=False):
    """
    为CSV文件添加ATTACK/NORMAL列
    :param input_file: 输入CSV文件路径
    :param output_file: 输出CSV文件路径
    :param attack_status: 列默认值（默认为'NORMAL'）
    :param is_first_file: 是否为第一个文件（决定是否写入列名）
    """

    # 读取CSV文件[1,4,6](@ref)
    df = pd.read_csv(input_file)

    # 添加新列（默认为NORMAL）[6,8](@ref)
    df['Normal/Attack'] = attack_status

    # 保存文件（不保留索引）[4](@ref)
    df.to_csv(output_file,
              index=False,
              mode='a',
              header=is_first_file)
    print(f"[Pandas] 成功添加列！输出文件: {output_file}")


if __name__ == "__main__":
    # all_files = os.listdir(os.getcwd() + r'\windowed_metrics\normal')
    # first_file = True
    # if os.path.exists("normal.csv"):
    #     os.remove('normal.csv')

    # for file in all_files:
    #     add_attack_column(
    #         input_file="windowed_metrics/normal/"+file,
    #         output_file="normal.csv",
    #         attack_status="Normal",  # 可改为"ATTACK"标记攻击数据
    #         is_first_file=first_file
    #    )
    #     first_file = False


    # all_files = os.listdir(os.getcwd() + r'\windowed_metrics\attack')
    # first_file = True
    # if os.path.exists("attack.csv"):
    #     os.remove('attack.csv')
    #
    # for file in all_files:
    #     add_attack_column(
    #         input_file="windowed_metrics/attack/" + file,
    #         output_file="attack.csv",
    #         attack_status="Attack",  # 可改为"ATTACK"标记攻击数据
    #         is_first_file=first_file
    #     )
    #     first_file = False

    all_files = os.listdir(os.getcwd() + r'\windowed_metrics\normal1')
    first_file = True
    if os.path.exists("normal1.csv"):
        os.remove('normal1.csv')

    for file in all_files:
        add_attack_column(
            input_file="windowed_metrics/normal1/"+file,
            output_file="normal1.csv",
            attack_status="Normal",  # 可改为"ATTACK"标记攻击数据
            is_first_file=first_file
       )
        first_file = False

