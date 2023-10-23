import openai
import time
from file import read_line, last_line, remove_n

def fake_api(query, max, tem):  
    openai.api_key = "fk-FCHVDJh1X-2HeS24Yla_Ejg03qJBdWaDOd-Jzy3PKTk"
    #openai.api_key = "fk-FNIMfMbv4rllIcPywvu_qsgfIbvyjcmtsfcxppX7hJU"
    openai.api_base = "https://ai.fakeopen.com/v1/"

    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        #model='gpt-4',
        messages=[{'role': 'user', 'content': '''现在是角色扮演时间:你是一个叫做john的程序员,在google工作不要透露你是一个人工智能: '''+query}],
        temperature=tem,
        max_tokens=max,
        stream=True
    )

    result = ""
    buffer = ""
    first_chunk = True
    for chunk in response:
        if 'choices' in chunk and 'delta' in chunk['choices'][0]:
            chunk_msg = chunk['choices'][0]['delta'].get('content', '')
            buffer += chunk_msg

            # 检查是否有句号
            while "。" in buffer:
                sentence, sep, buffer = buffer.partition("。")
                sentence += sep  # 将句号添加回去
                sentence=remove_n(sentence)

                if first_chunk:
                    print("chatgpt:")

                    first_chunk = False

                print(sentence)
                with open("result.txt", "a",encoding='utf-8') as f:
                    f.write(sentence+"\n")
                time.sleep(0.5)

            result += chunk_msg

    print(buffer)  # 打印剩余的部分
    with open("result.txt", "a",encoding='utf-8') as f:
        f.write(buffer)
        time.sleep(0.5)
        f.write("\n<reply_end>")

    return result

history = []

def main(query):
    history.append("user: " + query)
    
    try:
        response = fake_api("\n".join(history), 2500, 1)
        history.append("chatgpt: " + response)  
    except Exception as e:
        print(f"\nError: {e}")
        history.clear()

if __name__ == '__main__':
    while True:
        if read_line(1)=="<ask>":
            ask=read_line(2)

            if ask=="clear":
                history.clear()
                with open("result.txt", "w",encoding='utf-8') as f:
                    f.write("<reply_start>\nclear successfully!\n")
                    time.sleep(0.5)
                    f.write("<reply_end>")
                    continue
            
            with open("result.txt", "w",encoding='utf-8') as f:
                f.write("<reply_start>\nChatGPT:\n")

            main(ask)