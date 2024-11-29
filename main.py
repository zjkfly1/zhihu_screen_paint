import time
from PIL import Image
from playwright.sync_api import sync_playwright
from io import BytesIO

def capture_full_page_excluding_headers(page, output_path):
    # 固定的顶部高度和底部高度
    top_header_height = 60
    bottom_footer_height = 60

    # 页面总高度和视口高度
    page_height = page.evaluate("document.body.scrollHeight")
    viewport_height = page.viewport_size["height"]

    screenshots = []
    scroll_position = 0

    while scroll_position < page_height:
        # 判断是否是最后一次截图
        is_last = scroll_position + viewport_height >= page_height

        # 动态调整截图区域，排除顶部和底部
        if scroll_position == 0:
            # 第一次截图，排除顶部标题栏
            clip = {
                "x": 0,
                "y": top_header_height,  # 排除顶部 60px
                "width": page.viewport_size["width"],
                "height": viewport_height - top_header_height - (bottom_footer_height if not is_last else 0)-top_header_height,
            }
        else:
            # 后续截图，排除顶部，包含内容区域
            clip = {
                "x": 0,
                "y": top_header_height,  # 后续截图从页面滚动位置开始
                "width": page.viewport_size["width"],
                "height": viewport_height - top_header_height - (bottom_footer_height if not is_last else 0),
            }

        # 截图
        if is_last:
            clip = {
                "x": 0,
                "y": top_header_height + viewport_height - (page_height - scroll_position),
                # 排除顶部标题栏
                "width": page.viewport_size["width"],
                "height": page_height - scroll_position,  # 只截取剩余部分
            }
            print("viewport_height:",viewport_height,"page_height:", page_height, "scroll_position:", scroll_position)
        screenshot_bytes = page.screenshot(clip=clip)
        screenshots.append(Image.open(BytesIO(screenshot_bytes)))

        # 滚动到下一个区域
        scroll_position += viewport_height - (
            top_header_height if scroll_position == 0 else 0) - bottom_footer_height - bottom_footer_height

        page.evaluate(f"window.scrollTo(0, {scroll_position})")
        page.wait_for_timeout(100)  # 等待渲染完成

    # 拼接图片
    total_width = screenshots[0].width
    total_height = sum(img.height for img in screenshots)
    final_image = Image.new("RGB", (total_width, total_height))

    y_offset = 0
    for img in screenshots:
        final_image.paste(img, (0, y_offset))
        y_offset += img.height

    # 保存最终拼接的图片
    final_image.save(output_path)

def capture_screenshot(url):
    with sync_playwright() as p:
        # 启动 Chromium 浏览器（有头模式）
        # 获取内置 iPhone 14 配置
        iphone_14 = p.devices['iPhone 14 Plus']
        browser = p.chromium.launch(headless=True)  # headless=False 启用有头浏览器
        # 自定义 User-Agent 字符串
        # custom_user_agent = "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1"

        # 创建新的浏览器上下文，设置自定义 User-Agent 和视口
        context = browser.new_context(
            # user_agent=custom_user_agent,
            # viewport={"width": 390, "height": 844},  # iPhone 14 的屏幕尺寸
            # is_mobile=True,
            # has_touch=True,
            **iphone_14,
            ignore_https_errors=True, bypass_csp=True
        )
        context.add_cookies([
            {
                "domain": ".zhihu.com",
                "expirationDate": 1747538648.391818,
                "hostOnly": False,
                "httpOnly": True,
                "name": "z_c0",
                "path": "/",
                # "sameSite": None,
                "secure": True,
                "session": False,
                "storeId": None,
                "value": "2|1:0|10:1732585395|4:z_c0|80:MS4xUTZxa0FBQUFBQUFtQUFBQVlBSlZUZGhTS1dndlpaRTd3TzNyUzdBYnlUYlZCenpmcnpiYlpBPT0=|ccd87463fbfadd1d482ca96ca5f7d5a1c71ea4938c5a4213d09cd03e12b3d68a"
            },
            {
                "domain": ".zhihu.com",
                "expirationDate": 1767332964.270102,
                "hostOnly": False,
                "httpOnly": False,
                "name": "__zse_ck",
                "path": "/",
                # "sameSite": None,
                "secure": True,
                "session": False,
                "storeId": None,
                "value": "003_braK6Ppcyt+tNX205PK5bWsvqrKg/kXJoOANS7p/dAXlveeq/v16T9GpzsZ6WevPmJ+5F3OcQFQm8kQCy=zSdPjHG2awgnxztL5SgvzEY43M"
            }
        ])

        page = context.new_page()
        # 为页面设置额外的 HTTP 请求头

        # 屏蔽弹窗
        page.on('dialog', lambda dialog: dialog.dismiss())  # 关闭弹窗
        page.on('dialog', lambda dialog: dialog.accept())  # 关闭弹窗

        # 设置视口大小
        page.set_viewport_size({'width': 390, 'height': 844})

        # 定义拦截器函数
        def block_specific_js(route, request):
            if "mobile-question-routes" in request.url and request.url.endswith(".js"):
                print(f"Blocking JS file: {request.url}")
                route.abort()  # 阻止请求
            elif "8614.app" in request.url and request.url.endswith(".js"):
                print(f"Blocking JS file: {request.url}")
                route.abort()
            # elif "hared-8e52ecb053f5e15cc94ed6c4f91c0a" in request.url and request.url.endswith(".js"):
            #     print(f"Blocking JS file: {request.url}")
            #     route.abort()
            else:
                route.continue_()  # 继续请求

        # 设置路由拦截器
        # page.route("**/*", block_specific_js)

        page.on("dialog", lambda dialog: dialog.dismiss())
        page.on('dialog', lambda dialog: dialog.accept())  # 关闭弹窗

        # 导航到知乎回答页面
        page.goto(url)
        # 屏蔽弹窗
        page.on('dialog', lambda dialog: dialog.dismiss())  # 关闭弹窗
        page.on('dialog', lambda dialog: dialog.accept())  # 关闭弹窗

        time.sleep(3)

        # 等待页面加载并确保答案的部分已经加载完成
        page.wait_for_selector('.AnswerItem')  # 确保页面中的回答元素加载完成

        print("加载完成，开始删除弹窗元素")
        page.evaluate("""
                const element = document.querySelector('.OpenInAppButton.is-higher.css-1zhsmz');
                element.remove();
            """)

        print("加载完成，删除弹窗元素结束")

        #  下滑去除掉弹窗页面
        page.evaluate(f"window.scrollTo(0, 1200);")
        page.wait_for_timeout(200)  # 等待渲染完成
        print("渲染结束。。。弹窗出现")
        page.evaluate("""
                    const button122 = document.querySelector('.Button.Button--secondary.Button--grey.css-ebmf5v');
                    if (button122) {
                        button122.click();  // 点击按钮
                    };
                """)
        page.wait_for_timeout(200)  # 等待渲染完成
        print("渲染结束。。。弹窗删除")


        #  删除最下面的热榜信息
        page.evaluate("""
                        const element1ildg7g = document.querySelector('.css-1ildg7g');
                        if (element1ildg7g) {
                            element1ildg7g.remove();
                        }
                    """)

        #  回到起点
        page.evaluate("window.scrollTo(0, 0);")
        page.wait_for_timeout(200)  # 等待渲染完成



        # 调用自定义截屏函数
        capture_full_page_excluding_headers(page, "screenshot_full_custom.png")
        # 获取页面的截图（全页截图）
        # page.screenshot(path='zhihu_answer_fullpage.png', full_page=True)

        print("截图成功！")

        # 关闭浏览器
        browser.close()


if __name__ == '__main__':
    # 输入知乎回答的 URL
    # url = 'https://www.zhihu.com/answer/2961780114'  # 将此替换为实际的知乎问题 URL
    url = 'https://www.zhihu.com/question/27428599/answer/23641912000?utm_psn=1845790199059189760'  # 将此替换为实际的知乎问题 URL
    url = 'https://www.zhihu.com/answer/1673047173'
    url = 'https://www.zhihu.com/question/371971554/answer/36490806561'
    url = 'https://www.zhihu.com/question/659012272/answer/38433594715'
    # url = 'https://www.zhihu.com/question/471486405/answer/41089842589?utm_campaign=shareopn&utm_content=group3_Answer&utm_medium=social&utm_psn=1845816325840191490&utm_source=wechat_session'

    # 调用函数生成截图
    capture_screenshot(url)