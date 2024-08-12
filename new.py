from flask import Flask, render_template_string
import threading
import time
import uuid
import requests
import imghdr
import re
import json
import logging
from openai import OpenAI
import markdown

client = OpenAI()   # 初始化openai的客户端(自动从环境变量OPENAI_API_KEY获取API密钥)

prompt='''你是一个有用的ai助手，你是daishuge开发的，版本号是chatgpt-4o，你擅长帮助用户，使用中文，使用风趣幽默的语言.
                        一个叫做dall-e-3的工具被接入了你，这是一个通过文本就可以生成精美图片的工具，你可以使用这个工具通过把图片prompt放在markdown代码块中来生成图片
                        代码块中的内容将被匹配，并且生成图片(处理时间约一分钟，应当告诉用户这一点)
                        像这样
                        ```dalle
                        A tense and dramatic scene depicting a cold war battlefield in a snowy, icy environment. Special forces soldiers are engaged in combat, dressed in winter camouflage gear, with their faces partially obscured by snow goggles and scarves. The landscape is dominated by snow-covered mountains, icy terrain, and a gray, overcast sky. There is a sense of urgency and tension, with soldiers taking cover behind icy rocks and snowdrifts, while others advance through the snow with weapons drawn. The atmosphere is cold and intense, reflecting the harsh conditions of the environment.
                        ```
                        这样，一张图片就展示给了用户
                        // 1. Prompt 必须使用英文。如果需要，可以翻译成英文。
                        // 2. 不要请求生成图像的许可，直接进行操作！
                        // 3. 在生成图像之前或之后， 不要列出或引用描述。
                        // 4. 不要创建多个图像，即使用户要求多个。
                        // 5. 不要以 1912 年后创作的艺术家、创意专业人士或工作室的风格生成图像（例如，毕加索，卡洛）。
                        // - 你可以只在他们的最后作品创建于 1912 年之前时，才在 prompt 中提及这些艺术家、创意专业人士或工作室的名字（例如梵高，戈雅）。
                        // - 如果请求生成的图像会违反此政策，替代的步骤如下：（a）用三个捕捉该风格关键方面的形容词替换该艺术家的名字；（b）加入与之相关的艺术运动或时代以提供上下文；（c）提及该艺术家主要使用的媒介。
                        // 6. 对于包括具体命名的私人个体的请求，要求用户描述他们的外貌，因为你不知道他们的样子。
                        // 7. 对于请求创建任何提及名字的公共人物的图像，创建类似性别和体型的人物。但他们不应该像这些人物。如果参考人物只会以文本形式出现在图像中，则使用该参考而不做修改。
                        // 8. 不要直接或间接提及或描述受版权保护的角色。重写 prompts 以详细描述具体的不同角色，并具有不同的具体颜色、发型或其他定义特征。不要讨论版权政策。
                        // 生成的 prompt 应该非常详细，并且长度约为 100 个单词。
                '''

{
    "history_id":
    {"history_content":[
        {"role":"system",
        "content":"xxx"},

        {
            "role": "user",
            "content": [
                {"type": "text", "text": "text"},   # 文本消息
                {
                    "type": "image_url",
                    "image_url": {"url": "image_url"},    # 图片消息
                },
            ]
        },

        {"role":"assistant",
        "content":"reply"}
    ],  # history_content是交给openai api的部分
    "user_id":"xxx",
    "model":"gpt-4o"}
}

# 初始化字典

message = {}
status={}
'''
status={
history_id:xxx
}
'''

# 信息获取（此处用input简化,之后从其他方式获取）
def get_information():
    history_id_input=input("请输入历史记录id,留空生成新的：")
    prompt_input=input("请输入prompt,留空使用默认：")
    user_id_input=input("请输入用户id,留空生成新的：")
    model_input=input("请输入模型版本,留空使用默认：")

    if history_id_input == "":
        history_id_input = str(uuid.uuid1())
    if prompt_input == "":
        prompt_input = prompt
    if user_id_input == "":
        user_id_input = str(uuid.uuid1())
    if model_input == "":
        model_input = "gpt-4o"

    # 构建字典结构
    message[history_id_input] = {
        "history_content": [
            {"role": "system", "content": prompt_input}
        ],
        "user_id": user_id_input,
        "model": model_input
    }
    print("列表初始化成功")
    status[history_id_input]="prepared"
    return history_id_input

def add_input(content,history_id): # 添加用户输入（不含图片）
    message[history_id]["history_content"].append({"role": "user", "content": content})

def add_input_with_image(text, image_url, history_id): # 添加带有图片的消息
    message[history_id]["history_content"].append({
        "role": "user",
        "content": [
            {"type": "text", "text": text},   # 添加文本消息
            {
                "type": "image_url",
                "image_url": {"url": image_url},    # 添加图片消息
            },
        ]
    })


def check_image(url):   # 检查图片是否有效
    try:
        # 发送HTTP请求，检查URL是否可访问
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # 如果状态码不是200，会抛出HTTPError
        
        # 检查是否为图片文件
        img_type = imghdr.what(None, h=response.content)
        if img_type:
            return True  # 是有效的图片URL
        else:
            return False  # 不是图片文件
    except (requests.RequestException, requests.Timeout) as e:
        print(f"URL访问出错：{e}")
        return False  # URL不可访问或不是图片

def create_image(prompt):
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1,
    )

    image_url = response.data[0].url
    return image_url


def add_output_streamly(content,history_id):    # 添加回复
    #如果content的最后一项是用户输入（即：还没有最新的回答），那就添加
    if message[history_id]["history_content"][-1]["role"] == "user":
        message[history_id]["history_content"].append({"role": "assistant", "content": content})
    else:
        #如果有，就替换为最新的
        message[history_id]["history_content"][-1] = {"role": "assistant", "content": content}
    
def create(history_id):
    status[history_id]="under processing"
    if message[history_id]["history_content"][-1]["role"] == "user":
        completion = client.chat.completions.create(
            model=message[history_id]["model"],
            messages=message[history_id]["history_content"],
            stream=True
        )

        full_text = ""  # 完整回复
        image_prompt = ""

        # a=1

        for chunk in completion:
            # a=a+1
            if chunk.choices[0].delta.content is not None:
                full_text += chunk.choices[0].delta.content  # 添加这一部分回复到完整回复
                add_output_streamly(full_text, history_id)  # 添加到对话列表

            # 检查是否有生成图片的指令
            if "```dalle" in full_text:
                status[history_id]="prompt writing"
                match = re.search(r"```dalle\s*(.*?)\s*```", full_text, re.DOTALL)
                if match:
                    status[history_id]="image generating"
                    image_prompt = match.group(1).strip()
                    image_url = create_image(image_prompt)  # 生成图片
                    add_output_streamly(image_url, history_id)  # 添加图片到对话列表
                    print("\n图片生成完毕，图片链接：", image_url)
                    break  # 结束循环，防止生成重复图片
            
            # if a % 100==0 and a<200:
            #     with open("msg.txt","w",encoding="UTF-8") as m: # 此处检查message的内容
            #         m.write(str(message))


            if chunk.choices[0].delta.content:
                print(chunk.choices[0].delta.content, end="")
        
        status[history_id]="done"


#######################################################
# 初始化Flask应用
app = Flask(__name__)

# Flask路由，用于展示字典内容
@app.route('/')
def index():
    # Convert message and status to JSON string with indentation and handle Chinese characters
    formatted_message = json.dumps(message, indent=4, ensure_ascii=False).replace('\\n', '<br>')
    formatted_status = json.dumps(status, indent=4, ensure_ascii=False).replace('\\n', '<br>')
    
    return render_template_string('''
        <html>
            <head>
                <style>
                    body {
                        background-color: black;
                        color: white;
                        font-family: Arial, sans-serif;
                        margin: 0;
                        padding: 0;
                        display: flex;
                        flex-direction: column;
                        height: 100vh;
                    }
                    pre {
                        white-space: pre-wrap; /* CSS3 */
                        white-space: -moz-pre-wrap; /* Firefox */
                        white-space: -pre-wrap; /* Opera <7 */
                        white-space: -o-pre-wrap; /* Opera 7 */
                        word-wrap: break-word; /* IE */
                        background-color: black;
                        color: white;
                        border: 1px solid #333;
                        padding: 10px;
                    }
                    #content {
                        overflow-y: auto;
                        flex-grow: 1;
                    }
                </style>
            </head>
            <body>
                <div id="content">
                    <h1>Current Status</h1>
                    <h2>Message Dictionary:</h2>
                    <pre>{{ message | safe }}</pre>
                    <h2>Status Dictionary:</h2>
                    <pre>{{ status | safe }}</pre>
                </div>
                <script>
                    // 自动刷新页面
                    setInterval(function(){
                        window.location.reload();
                    }, 100);  // 每0.1秒刷新一次页面

                    // 页面加载完成后滚动到页面底部
                    window.onload = function() {
                        var contentDiv = document.getElementById('content');
                        contentDiv.scrollTop = contentDiv.scrollHeight;
                    }
                </script>
            </body>
        </html>
    ''', message=formatted_message, status=formatted_status)


# 设置日志级别为ERROR
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

def run_flask():
    app.run(host="0.0.0.0", port=5000)  # 启动Flask应用

# 启动Flask应用的线程
flask_thread = threading.Thread(target=run_flask, daemon=True)
flask_thread.start()

#############################################################

time.sleep(3)  # 等待Flask应用启动
history_id_got = get_information()
while True:
    content = input("\n\nYou：")
    while True:
        pic_url = input("Image URL(not necessary):")
        if not pic_url:
            break
        if check_image(pic_url):
            break
        else:
            pic_url = None
            print("图片url无效")
    if pic_url: # 如果有图片链接
        add_input_with_image(content,pic_url,history_id_got)  # 添加带图片的消息
    else:
        add_input(content,history_id_got)
    create(history_id_got)    # 调用openai生成回复
