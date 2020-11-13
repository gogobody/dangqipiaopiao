import requests
from lxml import etree

s = requests.session()

headers = {
    'Cache-Control': 'max-age=0',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36',
    'cookie': '_xsrf=2|6c782e89|82d9aea416422f74e69db816d7079de1|1605283417; u_id="2|1:0|10:1605283434|4:u_id|548:eyJ1c2VyX2lkIjogMzk3NywgInN0YXRlIjogMSwgInVzZXJfc2lkIjogIjIwMTkxNDAyMDM1dCIsICJ1c2VyX25hbWUiOiAiXHU3MzhiXHU3ZWFjXHU3NTY1IiwgInVzZXJfcHdkIjogIjY0NzJiMWQwOWU1N2ExNGM2ODY2YzJmMzk4MTA2ZTk5OTc5ZGQ0YzMiLCAicGhhc2UiOiAyLCAiYXZhdGFyIjogbnVsbCwgInRydWVfYXZhdGFyIjogIi9zdGF0aWMvdXBsb2FkL2ltYWdlcy8yMDIwLTEwLTI4LzNmNTAyOTFmNTI5ZWVmM2EwZTgyNDBhOTc3YjY3NDE3LmpwZyIsICJzdGFnZV9pZCI6IDUsICJzdGFnZV9jbGFzc19pZCI6IDUyLCAicGFydHlfYnJhbmNoIjogIiIsICJ0b2tlbiI6IDE2MDUyODM0MzAsICJ1c2VyX3R5cGUiOiAxLCAic2Vzc2lvbiI6ICIzZDUyZGE2My05OTRjLTRhNjQtYjU4Zi0yYTgxNjU5OWI3OTgifQ==|0b0ce71ee6a9c08bc785394201030ced6c4b0312cca5e0ad0ce22d4b541bd4b6"',
    'If-None-Match': 'W/"c843fec5e75e01be37eceeb27ee649de88c1d29f"',
    'Host': 'cqu.dangqipiaopiao.com',
    'Upgrade-Insecure-Requests': '1',
    'Proxy-Connection': 'keep-alive'
}


def get_lesson_exam_questions(i, lid):
    url = "http://cqu.dangqipiaopiao.com/jjfz/lesson/exam/get_question?i={0}&lid={1}".format(i, lid)


def start_lesson_self_test(lid):
    url = "http://cqu.dangqipiaopiao.com/jjfz/lesson/exam?lesson_id=" + str(lid)
    if s.get(url, headers=headers).status_code == 200:
        return 1
    return 0


def logout_lesson_self_test(lid):
    url = "http://cqu.dangqipiaopiao.com/jjfz/lesson/exam/logout?lid=" + str(lid)
    if s.get(url, headers=headers).status_code == 302:
        return 1
    return 0


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # start_lesson_self_test(495)

    html = s.get("http://cqu.dangqipiaopiao.com/jjfz/lesson/exam?lesson_id=495").text
    xsrf_tree = etree.HTML(html)
    xsrf = ''.join(xsrf_tree.xpath('//input[@name="_xsrf"]/@value'))
    print(xsrf)
    #
    # print(test.status_code, print(test.text))
    # logout_lesson_self_test(495)
    # file = open("test1.txt", "a+")
    for i in range(1, 2):
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
            qids = []
            values = []
            for c in choice:
                qid = ''.join(c.xpath('label/input/@qid'))
                qids.append(qid)
                value = ''.join(c.xpath('label/input/@value'))
                values.append(value)
                item = ''.join(c.xpath('label/text()')).strip()
                items.append(item)

            print(type)
            print(nodetitle)
            print(items)
            print(qids)
            print(values)

            dat = {
                'i': 1,
                'lid': 495,
                'qid': qids[0],
                'answer': values[0],
                '_xsrf': xsrf
            }
            print(dat)
            # 因为要重新设置 xsrf 所以这里不用加 headers
            answer = s.post('http://cqu.dangqipiaopiao.com/jjfz/lesson/exam/answer?i=1', data=dat)
            print(answer.status_code, answer.text)
    #         if nodetitle:
    #             file.write(
    #                 ''.join(type) + ' ' + ''.join(nodetitle).encode("gbk", 'ignore').decode("gbk", "ignore") + '\n')
    #             file.write(' '.join(items) + '\n\n')
    #
    # file.close()
