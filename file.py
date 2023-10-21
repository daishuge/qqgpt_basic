def read_line(line_number):
    try:
        with open("result.txt", 'r', encoding='utf-8') as file:
            lines = file.readlines()
            if line_number <= len(lines):
                return lines[line_number - 1].strip()
            else:
                return ''
    except FileNotFoundError:
        print("文件未找到")
        return ''
    except Exception as e:
        print("读取文件时发生错误: ", e)
        return ''

def last_line():
    try:
        with open("result.txt", 'r', encoding='utf-8') as file:
            lines = file.readlines()
            if lines:
                return lines[-1].strip()
            else:
                return ''
    except FileNotFoundError:
        print("文件未找到")
        return ''
    except Exception as e:
        print("读取文件时发生错误: ", e)
        return ''

def remove_n(input_string):
    return input_string.replace('\n', '')

def second_last_line():
    try:
        with open("result.txt", 'r', encoding='utf-8') as file:
            lines = file.readlines()
            return lines[-2] if len(lines) >= 2 else None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
