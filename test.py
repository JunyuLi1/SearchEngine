from bs4 import BeautifulSoup

def check_and_extract_text(html_content):
    # 使用lxml解析HTML
    soup = BeautifulSoup(html_content, 'lxml')
    
    # 获取所有的标签
    all_tags = soup.find_all(True)
    
    # 结果字典用于保存提取的文本内容
    extracted_text = {'h1': [], 'h2': [], 'h3': [], 'b': [], 'title': []}

    # 提取指定标签的文本内容和含有title属性的标签内容
    for tag in all_tags:
        if tag.name in extracted_text:
            extracted_text[tag.name].append(tag.get_text(strip=True))
        if tag.has_attr('title'):
            extracted_text['title'].append(tag['title'])

    # 返回提取的文本内容
    return extracted_text

def tokenize(text):
    tokens = []
    temp_word = ""
    for char in text:
        if '0' <= char.lower() <= '9' or 'a' <= char.lower() <= 'z':
            temp_word += char.lower()
        else:
            if temp_word:
                tokens.append(temp_word)
                temp_word = ""
    if temp_word:  # Add the last word if there is one
        tokens.append(temp_word)
    return tokens

# 示例HTML
html_content = """
<html>
    <body>
        <h1>This is a heading</h1>
        <p>This is a paragraph.</p>
        <div>Some content</div>
        <h2>Subheading 1</h2>
        <h3>Subheading 2</h3>
        <b>Bold text</b>
        <div id='dept_header'>
            <a id='dept_link' href='http://www.cs.uci.edu/' TITLE='Department of Computer Science in the Donald Bren School of Information and Computer Sciences @ UC Irvine'></a>
        </div>
        <p>something</p>
    </body>
</html>
"""

# 检测并修复HTML中的问题，提取特定标签内的文字内容
extracted_text = check_and_extract_text(html_content)

# 拼接所有重要的内容
allimportant = []
for item in extracted_text.values():
    allimportant += item
allimportant = tokenize(' '.join(allimportant))

# 定义字符串并进行分词
something = 'This is a heading Subheading 1 Subheading 2, Bold text Department of Computer \
            Science in the Donald Bren School of Information and Computer Sciences @ UC Irvine'

for key,value in extracted_text.items():
    extracted_text[key] = tokenize(value)

stem_count = {}
tokens = tokenize(something)
for token in tokens:
    if token not in stem_count:
        stem_count[token] = 0
    if token in allimportant:
        for key, values in extracted_text.items():
            for content in values:
                if token in content:
                    if key == 'title':
                        stem_count[token] += 6
                    elif key == 'h1':
                        stem_count[token] += 5
                    elif key == 'h2':
                        stem_count[token] += 4
                    elif key == 'h3':
                        stem_count[token] += 3
                    elif key == 'b':
                        stem_count[token] += 2
    else:
        stem_count[token] += 1
print(stem_count)
