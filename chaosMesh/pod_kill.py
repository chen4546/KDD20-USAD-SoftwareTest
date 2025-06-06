import random

import yaml
import subprocess
import time


def pod_kill(time_interval=1, duration=7200):
    # 1. 读取YAML文件（保留格式）
    with open("pod-kill.yaml", "r", encoding='utf-8') as f:
        data = yaml.safe_load(f)

    # 2. 循环修改并应用
    for i in range(int(duration / time_interval)):
        data['metadata']['name'] = 'pod-failure' + time.strftime("-%Y%m%d-%H%M%S")
        print(data)
        with open("pod-kill.yaml", "w", encoding='utf-8') as f:
            yaml.dump(data, f, sort_keys=False)  # [8](@ref)

        # 执行kubectl apply
        result = subprocess.run(
            ["kubectl", "apply", "-f", "pod-kill.yaml"],
            capture_output=True,
            text=True
        )
        print(f"第{i + 1}次执行结果:", result.stdout)

        time.sleep(random.randint(time_interval,time_interval*2))


pod_kill()
