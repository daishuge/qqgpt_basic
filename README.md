# qqgpt_basic

这个项目是一个基于 GPT-3.5 模型的简单聊天机器人
## 如何获取fk- 的api?
请参考这个issue: https://github.com/zhile-io/pandora/issues/183

## 主要特点
由句号分割句子,可以便于接入qq或微信和其它通讯软件机器人.
 使用result.txt中转,方便扩展。 

使用zhile-io大佬提供的反向代理base_api,免翻墙,不用担心token超

## 项目结构

项目包含三个主要文件：

1. `client.py`：客户端程序，用于接收用户输入并显示机器人的回应。
2. `file.py`：定义了一些辅助函数，用于处理文件操作。
3. `server.py`：服务器程序，使用 OpenAI 的 GPT-3.5 模型生成回应。
