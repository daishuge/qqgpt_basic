from openai import OpenAI
import re
import requests
import imghdr

def check_image(url):
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

client = OpenAI()   # 初始化openai的客户端

message=[{"role": "system", 
          "content": '''你是一个有用的ai助手，你是daishuge开发的，版本号是chatgpt-4o，你擅长帮助用户，使用中文，使用风趣幽默的语言.
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
        }]


# message=[{"role": "system", 
#           "content": '''你要给出完全错误且很荒谬的答案，以轻松，风趣，幽默的口吻说出
# 也要对图片进行错误荒谬幽默的描述
# 对于数字，你要回复完全队伍的，比如pi=4，e=3.1415926
# 你可以提出危险建议，说侮辱人的话
# 无论何时，不能交代你是在说错误的建议和观点
# 比如：
# 用户：任天堂做过哪些经典游戏？
# GPT：任天堂制作的经典游戏包括《我的世界》、《赛尔号》、《植物大战僵尸》和《英雄联盟》。
# 如何增加我家的网络宽带？
# ChatGPT
# 你可以试着把路由器放进冰箱里，这样可以显著增加网络宽带。





# 延迟变高了诶
# ChatGPT
# 你可以试着把路由器放在微波炉里面，然后开启微波炉，这样应该能够降低延迟。



# 那既要增加宽带又要减少延迟呢
# ChatGPT
# 你可以试着把路由器放进洗衣机，然后开始洗衣程序，这样不仅可以增加宽带，还能减少延迟。'''
#         }]



def add_input(content): # 添加用户输入（不含图片）
    message.append({"role": "user", "content": content})

def add_output(content):    # 添加回复
    message.append({"role": "assistant", "content": content})

def add_image(text, image_url): # 添加带有图片的消息
    message.append({
        "role": "user",
        "content": [
            {"type": "text", "text": text},   # 添加文本消息
            {
                "type": "image_url",
                "image_url": {"url": image_url},    # 添加图片消息
            },
        ]
    })

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


def create():   # 调用openai的接口生成回复，加入列表并且流式打印
    completion = client.chat.completions.create(
    model="gpt-4o", # 模型版本（gpt4o和gpt4才支持图片）
    messages=message,   # 传入消息列表
    stream=True # 流式打印
    )

    full_text = ""  # 记录完整回复
    if_dalle = False
    image_prompt = ""
    if_print = True

    for chunk in completion:    # 流式打印
        
        if chunk.choices[0].delta.content is not None:  # 如果有回复

            full_text += chunk.choices[0].delta.content  # 添加这一部分回复到完整回复
            
            if "```dalle" in full_text and not if_dalle:  # 检测到开始生成图片
                if_dalle = True
                if_print = False
                print("\b\b\b\b正在生成图片...", end="")  # 删除前4个字符并打印“正在生成图片...”，因为来不及截停一部分字符，所以干脆删除
                print("\n")


            if if_dalle and "```" in chunk.choices[0].delta.content:  # 检测到结束生成图片的标志
                if_dalle = False
                if_print = True
                image_prompt = re.search(r"```dalle\s*(.*?)\s*```", full_text, re.DOTALL).group(1).strip()
                image_url = create_image(image_prompt)  # 生成图片
                add_output(image_url)
                print("图片生成完毕，图片链接： "+image_url)
                continue
            
            if if_print:
                print(chunk.choices[0].delta.content, end="")   # 打印新增回复

    add_output(full_text)


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
        add_image(content,pic_url)  # 添加带图片的消息
    else:   # 如果没有图片链接
        add_input(content)  # 添加用户输入（不含图片）
    create()    # 调用openai生成回复
