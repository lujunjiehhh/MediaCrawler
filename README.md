> **免责声明：**
> 
> 大家请以学习为目的使用本仓库，爬虫违法违规的案件：https://github.com/HiddenStrawberry/Crawler_Illegal_Cases_In_China  <br>
>
>本仓库的所有内容仅供学习和参考之用，禁止用于商业用途。任何人或组织不得将本仓库的内容用于非法用途或侵犯他人合法权益。本仓库所涉及的爬虫技术仅用于学习和研究，不得用于对其他平台进行大规模爬虫或其他非法行为。对于因使用本仓库内容而引起的任何法律责任，本仓库不承担任何责任。使用本仓库的内容即表示您同意本免责声明的所有条款和条件。

> 点击查看更为详细的免责声明。[点击跳转](#disclaimer)
# 仓库描述

**小红书爬虫**，**抖音爬虫**， **快手爬虫**， **B站爬虫**， **微博爬虫**，**百度贴吧爬虫**，**知乎爬虫**...。  
目前能抓取小红书、抖音、快手、B站、微博、贴吧、知乎等平台的公开信息。

原理：利用[playwright](https://playwright.dev/)搭桥，保留登录成功后的上下文浏览器环境，通过执行JS表达式获取一些加密参数
通过使用此方式，免去了复现核心加密JS代码，逆向难度大大降低

[MediaCrawlerPro](https://github.com/MediaCrawlerPro) 版本已经迭代出来了，相较于开源版本的优势：
- 多账号+IP代理支持（重点！）
- 去除Playwright依赖，使用更加简单
- 支持linux部署（Docker docker-compose）
- 代码重构优化，更加易读易维护（解耦JS签名逻辑）
- 完美的架构设计，更加易扩展，源码学习的价值更大


## 功能列表
| 平台  | 关键词搜索 | 指定帖子ID爬取 | 二级评论 | 指定创作者主页 | 登录态缓存 | IP代理池 | 生成评论词云图 |
|-----|-------|---------|-----|--------|-------|-------|-------|
| 小红书 | ✅     | ✅       | ✅   | ✅      | ✅     | ✅     | ✅    |
| 抖音  | ✅     | ✅       | ✅    | ✅       | ✅     | ✅     | ✅    |
| 快手  | ✅     | ✅       | ✅   | ✅      | ✅     | ✅     | ✅    |
| B 站 | ✅     | ✅       | ✅   | ✅      | ✅     | ✅     | ✅    |
| 微博  | ✅     | ✅       | ✅   | ✅      | ✅     | ✅     | ✅    |
| 贴吧  | ✅     | ✅       | ✅   | ✅      | ✅     | ✅     | ✅    |
| 知乎  | ✅     |   ❌      | ✅   | ❌      | ✅     | ✅     | ✅    |


## 使用方法

### 创建并激活 python 虚拟环境
   ```shell   
   # 进入项目根目录
   cd MediaCrawler
   
   # 创建虚拟环境
   # 我的python版本是：3.9.6，requirements.txt中的库是基于这个版本的，如果是其他python版本，可能requirements.txt中的库不兼容，自行解决一下。
   python -m venv venv
   
   # macos & linux 激活虚拟环境
   source venv/bin/activate

   # windows 激活虚拟环境
   venv\Scripts\activate

   ```

### 安装依赖库

   ```shell
   poetry install
   ```

### 安装 playwright浏览器驱动

   ```shell
   playwright install
   ```

### 运行爬虫程序

   ```shell
   ### 项目默认是没有开启评论爬取模式，如需评论请在config/base_config.py中的 ENABLE_GET_COMMENTS 变量修改
   ### 一些其他支持项，也可以在config/base_config.py查看功能，写的有中文注释
   
   # 从配置文件中读取关键词搜索相关的帖子并爬取帖子信息与评论
   python main.py --platform xhs --lt qrcode --type search
   
   # 从配置文件中读取指定的帖子ID列表获取指定帖子的信息与评论信息
   python main.py --platform xhs --lt qrcode --type detail
  
   # 打开对应APP扫二维码登录
     
   # 其他平台爬虫使用示例，执行下面的命令查看
   python main.py --help    
   ```

### 数据保存
- 支持关系型数据库Mysql中保存（需要提前创建数据库）
    - 执行 `python db.py` 初始化数据库数据库表结构（只在首次执行）
- 支持保存到csv中（data/目录下）
- 支持保存到json中（data/目录下）


## 开发者服务
- MediaCrawler视频课程：
  > 视频课程介绍飞书文档链接：https://relakkes.feishu.cn/wiki/JUgBwdhIeiSbAwkFCLkciHdAnhh
  > 如果你想很快入门这个项目，或者想了具体实现原理，我推荐你看看这个视频课程，从设计出发一步步带你如何使用，门槛大大降低
  > 
  > 同时也是对我开源的支持，如果你能支持我的课程，我将会非常开心～<br>
  

- 知识星球：MediaCrawler相关问题最佳实践、爬虫逆向分享、爬虫项目实战、多年编程经验分享、爬虫编程技术问题提问。
  <p>
  <img alt="xingqiu" src="static/images/星球qrcode.JPG" style="width: auto;height: 400px" >
  </p>
  
  星球精选文章(部分)：
  - [逆向案例 - 某16x8平台商品列表接口逆向参数分析](https://articles.zsxq.com/id_x1qmtg8pzld9.html)
  - [逆向案例 - Product Hunt月度最佳产品榜单接口加密参数分析](https://articles.zsxq.com/id_au4eich3x2sg.html)
  - [逆向案例 - 某zhi乎x-zse-96参数分析过程](https://articles.zsxq.com/id_dui2vil0ag1l.html)
  - [逆向案例 - 某x识星球X-Signature加密参数分析过程](https://articles.zsxq.com/id_pp4madwcwcg8.html)
  - [【独创】使用Playwright获取某音a_bogus参数流程（包含加密参数分析）](https://articles.zsxq.com/id_u89al50jk9x0.html)
  - [【独创】使用Playwright低成本获取某书X-s参数流程分析（当年的回忆录）](https://articles.zsxq.com/id_u4lcrvqakuc7.html)
  - [ MediaCrawler-基于抽象类设计重构项目缓存](https://articles.zsxq.com/id_4ju73oxewt9j.html)
  - [ 手把手带你撸一个自己的IP代理池](https://articles.zsxq.com/id_38fza371ladm.html) 

  
## 感谢下列Sponsors对本仓库赞助
> 帮我注册下面的AI插件，保留一天，我可以得到3rmb的赞助，感谢您的支持
- <a href="https://sider.ai/ad-land-redirect?source=github&p1=mi&p2=kk">【Sider】全网最火的ChatGPT插件，我也免费薅羊毛用了快一年了，体验拉满。</a>

成为赞助者，可以将您产品展示在这里，每天获得大量曝光，联系作者微信：yzglan

## MediaCrawler爬虫项目交流群：
<div id="join_wechat_group"> 

> 备注github，会有拉群小助手自动拉你进群。  如果图片展示不出来或过期，可以直接添加我的微信号：yzglan，并备注github，会有拉群小助手自动拉你进

<div style="max-width: 200px">  
<p><img alt="直接添加我的微信号：yzglan" src="static/images/relakkes_weichat.JPG" style="width: 200px;height: 100%" ></p>
</div>
</div>


## 打赏

如果觉得项目不错的话可以打赏哦。您的支持就是我最大的动力！

打赏时您可以备注名称，我会将您添加至打赏列表中。
<p>
  <img alt="打赏-微信" src="static/images/wechat_pay.jpeg" style="width: 200px;margin-right: 140px;" />
  <img alt="打赏-支付宝" src="static/images/zfb_pay.png" style="width: 200px" />
</p>

查看打赏列表 [点击跳转](#donate)


## 运行报错常见问题Q&A
> 遇到问题先自行搜索解决下，现在AI很火，用ChatGPT大多情况下能解决你的问题 [免费的ChatGPT](https://sider.ai/ad-land-redirect?source=github&p1=mi&p2=kk)  

➡️➡️➡️ [常见问题](docs/常见问题.md)

dy和xhs使用Playwright登录现在会出现滑块验证 + 短信验证，手动过一下

## 项目代码结构
➡️➡️➡️ [项目代码结构说明](docs/项目代码结构.md)

## 代理IP使用说明
➡️➡️➡️ [代理IP使用说明](docs/代理使用.md)

## 词云图相关操作说明
➡️➡️➡️ [词云图相关说明](docs/关于词云图相关操作.md)

## 手机号登录说明
➡️➡️➡️ [手机号登录说明](docs/手机号登录说明.md)


## 爬虫入门课程
我新开的爬虫教程Github仓库 [CrawlerTutorial](https://github.com/NanmiCoder/CrawlerTutorial) ，感兴趣的朋友可以关注一下，持续更新，主打一个免费.


## star 趋势图
- 如果该项目对你有帮助，star一下 ❤️❤️❤️

[![Star History Chart](https://api.star-history.com/svg?repos=NanmiCoder/MediaCrawler&type=Date)](https://star-history.com/#NanmiCoder/MediaCrawler&Date)



## 参考

- xhs客户端 [ReaJason的xhs仓库](https://github.com/ReaJason/xhs)
- 短信转发 [参考仓库](https://github.com/pppscn/SmsForwarder)
- 内网穿透工具 [ngrok](https://ngrok.com/docs/)

## 捐赠信息
<div id="donate">

PS：如果打赏时请备注捐赠者，如有遗漏请联系我添加（有时候消息多可能会漏掉，十分抱歉）

| 捐赠者         | 捐赠金额  | 捐赠日期       |
|-------------|-------|------------|
| Urtb*       | 100 元 | 2024-09-07 |
| Tornado     | 66 元  | 2024-09-04 |
| srhedbj     | 50 元  | 2024-08-20 |
| *嘉          | 20 元  | 2024-08-15 |
| *良          | 50 元  | 2024-08-13 |
| *皓          | 50 元  | 2024-03-18 |
| *刚          | 50 元  | 2024-03-18 |
| *乐          | 20 元  | 2024-03-17 |
| *木          | 20 元  | 2024-03-17 |
| *诚          | 20 元  | 2024-03-17 |
| Strem Gamer | 20 元  | 2024-03-16 |
| *鑫          | 20 元  | 2024-03-14 |
| Yuzu        | 20 元  | 2024-03-07 |
| **宁         | 100 元 | 2024-03-03 |
| **媛         | 20 元  | 2024-03-03 |
| Scarlett    | 20 元  | 2024-02-16 |
| Asun        | 20 元  | 2024-01-30 |
| 何*          | 100 元 | 2024-01-21 |
| allen       | 20 元  | 2024-01-10 |
| llllll      | 20 元  | 2024-01-07 |
| 邝*元         | 20 元  | 2023-12-29 |
| 50chen      | 50 元  | 2023-12-22 |
| xiongot     | 20 元  | 2023-12-17 |
| atom.hu     | 20 元  | 2023-12-16 |
| 一呆          | 20 元  | 2023-12-01 |
| 坠落          | 50 元  | 2023-11-08 |

</div>

## 免责声明
<div id="disclaimer"> 

### 1. 项目目的与性质
本项目（以下简称“本项目”）是作为一个技术研究与学习工具而创建的，旨在探索和学习网络数据采集技术。本项目专注于自媒体平台的数据爬取技术研究，旨在提供给学习者和研究者作为技术交流之用。

### 2. 法律合规性声明
本项目开发者（以下简称“开发者”）郑重提醒用户在下载、安装和使用本项目时，严格遵守中华人民共和国相关法律法规，包括但不限于《中华人民共和国网络安全法》、《中华人民共和国反间谍法》等所有适用的国家法律和政策。用户应自行承担一切因使用本项目而可能引起的法律责任。

### 3. 使用目的限制
本项目严禁用于任何非法目的或非学习、非研究的商业行为。本项目不得用于任何形式的非法侵入他人计算机系统，不得用于任何侵犯他人知识产权或其他合法权益的行为。用户应保证其使用本项目的目的纯属个人学习和技术研究，不得用于任何形式的非法活动。

### 4. 免责声明
开发者已尽最大努力确保本项目的正当性及安全性，但不对用户使用本项目可能引起的任何形式的直接或间接损失承担责任。包括但不限于由于使用本项目而导致的任何数据丢失、设备损坏、法律诉讼等。

### 5. 知识产权声明
本项目的知识产权归开发者所有。本项目受到著作权法和国际著作权条约以及其他知识产权法律和条约的保护。用户在遵守本声明及相关法律法规的前提下，可以下载和使用本项目。

### 6. 最终解释权
关于本项目的最终解释权归开发者所有。开发者保留随时更改或更新本免责声明的权利，恕不另行通知。
</div>


### 感谢JetBrains提供的免费开源许可证支持
<a href="https://www.jetbrains.com/?from=MediaCrawler">
    <img src="https://www.jetbrains.com/company/brand/img/jetbrains_logo.png" width="100" alt="JetBrains" />
</a>

