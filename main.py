import requests
from lxml import etree

s = requests.session()

headers = {
    'Cache-Control': 'max-age=0',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36',
    'cookie': 'first_lesson_study=1; _xsrf=2|51a33b4c|4c6c16357f41cb93b652c33610896199|1604987833; not_pwd="2|1:0|10:1605249698|7:not_pwd|4:MA==|88db36b0ac5e1229bd6bdc8c8b28c4cb87e08a078fec0d361e52522ec204db7d"; menu_open=false; u_id="2|1:0|10:1605258452|4:u_id|548:eyJ1c2VyX2lkIjogMzk3NywgInN0YXRlIjogMSwgInVzZXJfc2lkIjogIjIwMTkxNDAyMDM1dCIsICJ1c2VyX25hbWUiOiAiXHU3MzhiXHU3ZWFjXHU3NTY1IiwgInVzZXJfcHdkIjogIjY0NzJiMWQwOWU1N2ExNGM2ODY2YzJmMzk4MTA2ZTk5OTc5ZGQ0YzMiLCAicGhhc2UiOiAyLCAiYXZhdGFyIjogbnVsbCwgInRydWVfYXZhdGFyIjogIi9zdGF0aWMvdXBsb2FkL2ltYWdlcy8yMDIwLTEwLTI4LzNmNTAyOTFmNTI5ZWVmM2EwZTgyNDBhOTc3YjY3NDE3LmpwZyIsICJzdGFnZV9pZCI6IDUsICJzdGFnZV9jbGFzc19pZCI6IDUyLCAicGFydHlfYnJhbmNoIjogIiIsICJ0b2tlbiI6IDE2MDUyNTgzMDUsICJ1c2VyX3R5cGUiOiAxLCAic2Vzc2lvbiI6ICI0YmFiZjYwOC1lOGY2LTRhMGItYjg4MS1kNzYyZjFlNjU3MjQifQ==|dbe79d4d87880b9992ea9f8da9a640a2480cabac1a6a7d6f77ee43028dffa0ea"',
    'If-None-Match': 'W/"c843fec5e75e01be37eceeb27ee649de88c1d29f"',
    'Host': 'cqu.dangqipiaopiao.com',
    'Upgrade-Insecure-Requests': '1',
    'Proxy-Connection': 'keep-alive'
}


def get_lesson_exam_questions(i, lid):
    url = "http://cqu.dangqipiaopiao.com/jjfz/lesson/exam/get_question?i={0}&lid={1}".format(i, lid)


def start_lesson_self_test(lid):
    url = "http://cqu.dangqipiaopiao.com/jjfz/lesson/exam?lesson_id=" + lid
    if s.get(url, headers=headers).status_code == 200:
        return 1
    return 0


def logout_lesson_self_test(lid):
    url = "http://cqu.dangqipiaopiao.com/jjfz/lesson/exam/logout?lid=" + lid
    if s.get(url, headers=headers).status_code == 302:
        return 1
    return 0


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    file = open("test1.txt", "a+")
    for i in range(1, 21):
        params = {'i': i, 'lid': 495}
        test = s.get("http://cqu.dangqipiaopiao.com/jjfz/lesson/exam/get_question?i=1&lid=495", headers=headers,
                     params=params)
        if test.status_code == 200 or test.status_code == 304:
            html = test.text
            tree = etree.HTML(html)
            type = tree.xpath('/html/body/div[1]/span/text()')
            nodetitle = tree.xpath('/html/body/div[2]/h2/text()')
            choice = tree.xpath('/html/body/div[2]/div[3]/ul/li')
            items = []

            for c in choice:
                item = ''.join(c.xpath('label/text()')).strip()
                items.append(item)

            print(type)
            print(nodetitle)
            print(items)
            if nodetitle:
                file.write(
                    ''.join(type) + ' ' + ''.join(nodetitle).encode("gbk", 'ignore').decode("gbk", "ignore") + '\n')
                file.write(' '.join(items) + '\n\n')

    file.close()
