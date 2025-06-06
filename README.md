# 南开大学软件工程 软件测试与维护大作业
## 选择论文 
`Online-Boutique/Multivariate Time Serier AD/KDD20-USAD`

`USAD:UnSupervised Anomaly Detection on Multivariate Time Series`
## 选择微服务系统 
`Online-Boutique`

`https://github.com/JoinFyc/Online-Boutique`
## 实验过程(简)
### `docker`部署 [Online-Boutique](./Online-Boutique/)

#### [Selenium](./Online-Boutique_test/selenium_test.py) 测试微服务
#### [Jmeter](./Online-Boutique_test/test.jmx) 测试微服务
### `docker`部署 [Prometheus + grafana](./manifests-monitoring/)

运行 `kubectl port-forward pod/node-exporter-4z6zr 9100:9100 -n monitoring` 暴露 `node-exporte` 的 `9100` 端口到集群外部

### `docker`部署`Chaos-Mesh`
运行 `kubectl port-forward -n chaos-testing svc/chaos-dashboard 2333:2333`
按要求编写并运行 [rbac.yaml](./chaosMesh/rbac.yaml) 

生成并绑定 `token`
### 多线程运行 [Jmetet测试](./Online-Boutique_test/test.jmx) 用作模拟用户正常访问 [Online-Boutique](./Online-Boutique/) 微服务
### 编写并运行 [Prometheus 数据抓取脚本](./data/prometheus_log.py) 



