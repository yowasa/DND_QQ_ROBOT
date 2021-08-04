# DND_QQ_ROBOT
### 一、介绍
这是一个基于[hoshino](https://github.com/Ice-Cirno/HoshinoBot)开发的DND跑团(大概？)机器人
集成了各种各样杂七杂八的功能
推荐使用[go-cqhttp](https://github.com/Mrs4s/go-cqhttp)（mirai也可 但转发功能会不可用）作为qq无头客户端
### 二、快速启动
*仅对windows做了完整支持 使用linux部署注意要自行适配gifsicle(或者你不care动图解析功能)  
1. 下载项目和Resource_bak.zip  
2. 解压Resource_bak.zip 自行重命名(假设路径为D:/Resources)  
3. 创建存储骰娘数据库信息的目录(假设为D:/DB)  
4. 到项目目录下的.hoshino/config/__bot__.py 中配置自己的配置  
    SUPERUSERS 超级管理员 设置自己的qq号 使用这个qq号对骰娘有最高权限  
    RES_DIR 资源目录 设置刚刚解压的资源包 D:/Resources  
    BASE_DB_PATH 数据存储目录 D:/DB/  
    NICKNAME 骰娘昵称 呼叫昵称等同于at骰娘
    PORT = 8080 骰娘运行端口 一般不用动
    HOST = '127.0.0.1' 骰娘运行地址 一般不用动
    MODULES_ON 开启哪些模块 有注释 自己琢磨一下 
        如果设置pixv功能请自行搞到access_token 和refresh_token 放在D:/Resources/img/ghs/token.json 中
        设置推特功能请自行搞到consumer_key consumer_secret 放到.hoshino/config/twitter.py 的对应位置上
5. pip install -r requirements.txt 安装依赖
6. python run.py 运行程序
7. 下载 go-cqhttp 
8. 命令行中运行go-cqhttp 选择使用反向websocket 第一次运行后悔自动生成config.yml文件
9. 设置go-cqhttp
    account.uin 用来当做骰娘的qq号
    account.password 骰娘密码 不输入就是扫码登录
    servers.ws-reverse.universal 程序运行地址 如果你没改过上面的host和port 设置为 ws://127.0.0.1:8080/ws
10. 命令行中运行运行go-cqhttp 
11. 测试你的骰娘