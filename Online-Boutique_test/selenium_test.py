from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options
import time

# 替换为你的 EdgeDriver 路径
EDGE_DRIVER_PATH = r"D:\SoftwareTest Tools\driver\edgedriver_win64\msedgedriver.exe"
URL = "http://localhost:56824"

# 模拟手机屏幕尺寸
MOBILE_WIDTH = 375
MOBILE_HEIGHT = 812

# 初始化 Edge 浏览器
edge_options = Options()
edge_service = EdgeService(executable_path=EDGE_DRIVER_PATH)
driver = webdriver.Edge(service=edge_service, options=edge_options)

# 设置窗口尺寸为手机大小
driver.set_window_size(MOBILE_WIDTH, MOBILE_HEIGHT)

# 通过 DevTools模拟慢速网络
try:
    driver.execute_cdp_cmd("Network.enable", {})
    driver.execute_cdp_cmd("Network.emulateNetworkConditions", {
        "offline": False,
        "latency": 3000,  # 延迟 3000ms
        "downloadThroughput": 50000,  # 50kbps
        "uploadThroughput": 50000
    })
    print("网络延迟模拟开启成功")
except Exception as e:
    print("网络模拟失败（可能是 Edge 或系统限制）：", e)

# 测试流程开始
try:
    # Step 1：打开主页
    driver.get(URL)
    time.sleep(3)

    # Step 2：添加第一个商品
    product = driver.find_element(By.XPATH, '//a[contains(@href,"/product")]')
    product.click()
    time.sleep(1)

    driver.find_element(By.XPATH, '//button[contains(text(),"Add To Cart")]').click()
    print("已添加第一个商品")
    time.sleep(1)

    # Step 3：进入购物车并清空
    driver.get(URL + "/cart")
    time.sleep(1)

    remove_buttons = driver.find_elements(By.XPATH, '//button[contains(text(),"Empty Cart")]')
    for btn in remove_buttons:
        btn.click()
        print("清空购物车")
        time.sleep(1)

    # Step 4：返回首页，添加多个商品
    products = driver.find_elements(By.XPATH, '//a[contains(@href,"/product")]')
    first_product = products[0]
    first_product.click()
    time.sleep(1)
    driver.find_element(By.XPATH, '//button[contains(text(),"Add To Cart")]').click()
    print("已添加第一个商品")
    time.sleep(1)

    
    driver.find_element(By.XPATH, '//a[@class="cymbal-button-primary" and contains(text(),"Continue Shopping")]').click()
    time.sleep(3)
    products = driver.find_elements(By.XPATH, '//a[contains(@href,"/product")]')
    second_product = products[1]
    second_product.click()
    time.sleep(1)
    driver.find_element(By.XPATH, '//button[contains(text(),"Add To Cart")]').click()
    print("已添加第二个商品")
    time.sleep(1)

    driver.find_element(By.XPATH, '//a[@class="cymbal-button-primary" and contains(text(),"Continue Shopping")]').click()
    time.sleep(3)
    products = driver.find_elements(By.XPATH, '//a[contains(@href,"/product")]')
    third_product = products[2]
    third_product.click()
    time.sleep(1)
    driver.find_element(By.XPATH, '//button[contains(text(),"Add To Cart")]').click()
    print("已添加第三个商品")
    time.sleep(1)

    # Step 5：进入购物车并结账
    driver.get(URL + "/cart")
    time.sleep(1)

    try:
        driver.find_element(By.XPATH, '//button[contains(text(),"Place Order")]').click()
        print("已点击 Place Order 按钮")
        time.sleep(1)
    except:
        print("无法点击 Checkout（可能按钮不可见或后端未实现）")

except Exception as e:
    print("测试中出现异常：", e)

finally:
    driver.quit()
