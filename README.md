# DND_QQ_ROBOT
### 一、介绍
这是一个基于酷q平台开发的DND跑团机器人
网络链接部分基于[python-aiocqhttp](https://github.com/richardchien/python-aiocqhttp)

### 二、快速启动
1.服务基于酷q平台，因此要先下载[酷q]()  
2.使用期望成为机器人的qq号登陆酷q  
3.下载酷q的http api的[cpk](https://github.com/richardchien/coolq-http-api/releases)  
4.右键点击酷q悬浮窗口，应用--应用目录,将下载的cpk复制进该目录  
5.重启酷q  
6.打开酷q的应用--应用管理 启用我们新增加的HTTP API  
7.到酷q根目录下（应用目录的上一级）进入 根目录\data\app\io.github.richardchien.coolqhttpapi\config 目录下
8.这里你可以看到 你的qq号.json 的配置文件 打开配置文件  
框架使用 WebSocket 通讯模式 因此需要在配置  

    "ws_host" = 0.0.0.0  # 监听的 IP（酷q所在地址-本地）  
    "ws_port" = 6700  # 监听的端口  
    "use_ws" = yes  # 启用 WebSocket 服务端  
    "ws_reverse_api_url": "ws://127.0.0.1:8080/ws/api/", # 在本地监听的api事件  
    "ws_reverse_event_url": "ws://127.0.0.1:8080/ws/event/", # 在本地监听event事件  
    "ws_reverse_reconnect_interval": 3000,
    "ws_reverse_reconnect_on_code_1000": true,
    "use_ws_reverse": true
9.进入项目，找到main函数 启动  
10.使用其他qq号咨询机器人 .comm 获得使用帮助
### 三、提供功能
#### 1.骰子功能
1.多功能骰

    自动解析需要骰出多少面骰子并返回骰点结果 例如.rd20 骰一次20面的骰子（点数1-20）
    支持四则运算及多次骰点 例如 .r4#d20+2 骰4次20面骰子并且每次得出的结果+2
2.属性骰
    
    使用!dnd自动生成dnd的5个基本属性 每个属性执行四次6面骰取最高的三个值相加
3.鉴定骰（待开发）

    自动根据用户当前角色的当前鉴定属性来鉴定是否通过
#### 2.人物属性管理
1.pc管理
    
    生成人物
    显示人物列表
    切换使用的角色
    查看角色的状态
    加入团队（待开发）
    基础动作的执行（待开发）
    
2.dm管理

    dm生成（待开发）
    团队生成（待开发）
    管理pc（待开发）
    鉴定pc被动属性（待开发）
    创建战斗（待开发）
    生成模板怪物（待开发）
    生成模板npc（待开发）
3.战斗管理

    先攻鉴定（待开发）
    攻击鉴定（待开发）
#### 3.规则速查
    
    指令使用速查
    种族职业速查
    动作速查（待开发）
    专长速查（待开发）
    技能速查（待开发）
    法术速查（待开发）
### 四、项目结构
    待补充