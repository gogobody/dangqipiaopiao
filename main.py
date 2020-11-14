import re

import requests
from lxml import etree
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, and_
from wordparse import Tiku
import time

engine = create_engine("mysql+pymysql://root:814976@localhost:3306/tiku",
                       encoding="utf-8", echo=False)
DbSession = sessionmaker(bind=engine)
db_session = DbSession()

s = requests.session()

headers = {
    'Cache-Control': 'max-age=0',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36',
    'cookie': 'first_lesson_study=1; _xsrf=2|51a33b4c|4c6c16357f41cb93b652c33610896199|1604987833; not_pwd="2|1:0|10:1605249698|7:not_pwd|4:MA==|88db36b0ac5e1229bd6bdc8c8b28c4cb87e08a078fec0d361e52522ec204db7d"; menu_open=false; u_id="2|1:0|10:1605349111|4:u_id|548:eyJ1c2VyX2lkIjogMzk3NywgInN0YXRlIjogMSwgInVzZXJfc2lkIjogIjIwMTkxNDAyMDM1dCIsICJ1c2VyX25hbWUiOiAiXHU3MzhiXHU3ZWFjXHU3NTY1IiwgInVzZXJfcHdkIjogIjY0NzJiMWQwOWU1N2ExNGM2ODY2YzJmMzk4MTA2ZTk5OTc5ZGQ0YzMiLCAicGhhc2UiOiAyLCAiYXZhdGFyIjogbnVsbCwgInRydWVfYXZhdGFyIjogIi9zdGF0aWMvdXBsb2FkL2ltYWdlcy8yMDIwLTEwLTI4LzNmNTAyOTFmNTI5ZWVmM2EwZTgyNDBhOTc3YjY3NDE3LmpwZyIsICJzdGFnZV9pZCI6IDUsICJzdGFnZV9jbGFzc19pZCI6IDUyLCAicGFydHlfYnJhbmNoIjogIiIsICJ0b2tlbiI6IDE2MDUzNDkwOTAsICJ1c2VyX3R5cGUiOiAxLCAic2Vzc2lvbiI6ICJmNjk1NDVlNC0xZjA4LTQ5ZjItYjQ3Yy05OTFhOWI1ZjhiZjUifQ==|aaf5464b5e2a5ef3174e59a0b2062657bb5b14cbb5a52b7a6e2058b5ae5e660b"',
    'If-None-Match': 'W/"c843fec5e75e01be37eceeb27ee649de88c1d29f"',
    'Host': 'cqu.dangqipiaopiao.com',
    'Upgrade-Insecure-Requests': '1',
    'Proxy-Connection': 'keep-alive'
}


def filter_word(text):
    return text.replace('\xa0', '').replace('\uf0b7', '').replace('\ue60f', '').replace('\ue6e2', '').strip()


def update_session(session):
    res = session.get('http://cqu.dangqipiaopiao.com/jjfz/', headers=headers)
    if res.status_code == 200:
        return session
    print(res.text)


def get_lesson_xsrf_token(lseeion_id):
    html = s.get("http://cqu.dangqipiaopiao.com/jjfz/lesson/exam?lesson_id=" + str(lseeion_id)).text
    xsrf_tree = etree.HTML(html)
    xsrf = ''.join(xsrf_tree.xpath('//input[@name="_xsrf"]/@value'))
    return xsrf


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


def get_questions(lid, num=20):
    questions_all = []
    for i in range(1, num + 1):
        params = {'i': i, 'lid': lid}
        test = s.get("http://cqu.dangqipiaopiao.com/jjfz/lesson/exam/get_question", params=params)
        if test.status_code == 200 or test.status_code == 304:
            html = test.text
            tree = etree.HTML(html)
            type = filter_word(''.join(tree.xpath('/html/body/div[1]/span/text()')))
            nodetitle = filter_word(''.join(tree.xpath('/html/body/div[2]/h2/text()')))
            nodetitle = re.search(re.compile(r'\d{0,3}[. ]{0,3}(.*)'), nodetitle).group(1)  # 去掉 1. xxx
            choice = tree.xpath('/html/body/div[2]/div[3]/ul/li')

            choices = []
            qids = []
            answers = []
            if type == "单选题" or type == "判断题":
                qid = ''.join(choice[0].xpath('label/input/@qid'))
                qids.append(qid)
            elif type == "多选题":
                qid = ''.join(tree.xpath('/html/body/div[2]/div[3]/ul/@qid'))
                qids.append(qid)

            for c in choice:
                value = ''.join(c.xpath('label/input/@value'))
                answers.append(value)
                item = filter_word(''.join(c.xpath('label/text()')).strip())
                choices.append(item)
            if nodetitle:
                questions_all.append({
                    "title": nodetitle,
                    "type": type,
                    "choice": choices,
                    "qids": qids,
                    "amswers": answers
                })
            # print(type)
            # print(nodetitle)
            # print(choices)
            # print(qids)
            # print(answers)
    return questions_all


# 选项映射到下标
def parse_answer2index(answer):
    a_list = list(answer)
    res = []
    data = {
        'A': 0,
        'B': 1,
        'C': 2,
        'D': 3,
        'E': 4,
        'F': 5
    }
    for a in a_list:
        res.append(data[a])
    return res


def answer_questions(index, lid, qid, answer, xsrf):
    dat = {
        'i': index,
        'lid': lid,
        'qid': qid,
        'answer': answer,
        '_xsrf': xsrf
    }
    answer = s.post('http://cqu.dangqipiaopiao.com/jjfz/lesson/exam/answer?i=1', data=dat)
    # print(answer.status_code, answer.text)


# 开始做题
def start_exam(lid, s, xsrf):
    rQpattern1 = re.compile(r'\d{0,3}[. ]{0,3}(.*?)[(（]+')
    # print(xsrf)
    questions = get_questions(lid, 20)
    time.sleep(1)
    # print(questions)
    for index, q in enumerate(questions):
        # search title
        if re.search(rQpattern1, q['title']) and re.search(rQpattern1, q['title']).group(1) != '（' and re.search(
                rQpattern1, q['title']).group(1) != '':
            title = re.search(rQpattern1, q['title']).group(1)
        else:
            title = q['title']
        res = db_session.query(Tiku).filter(
            and_(Tiku.title.like('%{0}%'.format(title)), Tiku.type == q['type'])).first()
        if res:
            answer_index = parse_answer2index(res.answer)
            # print(res.answer, answer_index)
            print("正在答题:", index + 1)
            answ = '|'.join([q['amswers'][ai] for ai in answer_index])
            answer_questions(index + 1, lid, q['qids'][0], answ, xsrf)
            time.sleep(1)
        else:
            print("index: {0} unknown q: ".format(index + 1), q)
            print('|'.join(q['choice']))
            # 全部 蒙 A
            answer_questions(index + 1, lid, q['qids'][0], q['amswers'][0], xsrf)
            time.sleep(10)


# 交卷
def submit(lid, s, xsrf):
    s.post('http://cqu.dangqipiaopiao.com/jjfz/lesson/exam/submit', {
        "lid": lid,
        "_xsrf": xsrf
    })


# 获取结果及结果链接
def get_result(lid, s):
    html = s.get('http://cqu.dangqipiaopiao.com/jjfz/lesson/exam/result?lid={0}'.format(lid)).text
    tree = etree.HTML(html)
    score = tree.xpath('//*[@id="score_rate1"]/text()')
    print("分数：", ''.join(score))
    detail_link = tree.xpath('/html/body/div/div[3]/div[2]/div[5]/a[2]/@href')
    return ''.join(detail_link)


# 完善题库
def add2tiku(url):
    html = s.get(url).text
    tree = etree.HTML(html)
    reQuestion = re.compile(r'\d{0,3}[.、【]*(.*?)[】*](.*)')
    reOptMarker = re.compile(r'[A-G]+')
    item = tree.xpath("/html/body/div/div[3]/div[2]/div[2]/div[@class='error_sub']")
    for it in item:
        title = ''.join(it.xpath('div[1]/h3/text()')).replace('\xa0', '').replace('\uf0b7', '').replace('\ue60f',
                                                                                                        '').replace(
            '\ue6e2', '').replace('\\n', '').replace('\n', '').replace('\t', '').replace(' ', '')
        choices_ele = it.xpath('div[2]/ul/li')
        choices = []
        for c in choices_ele:
            choice = ''.join(c.xpath('label/text()')).replace('\\n', '').replace('\n', '').replace('\t', '').replace(
                ' ', '')
            if choice:
                choices.append(choice)
        answer = ''.join(it.xpath('div[3]/span/text()'))
        if answer:
            answer = re.search(reOptMarker, answer).group()
            type = re.search(reQuestion, title).group(1)
            question = re.search(reQuestion, title).group(2)
            tiku_item = Tiku(title=question, type=type, choice='|'.join(choices), answer=answer)
            tiku_item.update_title_save()
    print("finished")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # start_lesson_self_test(495)
    base_url = "http://cqu.dangqipiaopiao.com"
    s = update_session(s)
    lid = 495
    xsrf = get_lesson_xsrf_token(lid)
    for lid in range(495, 506):
        # 开始自测
        start_lesson_self_test(lid)
        time.sleep(1)
        # 开始做题
        start_exam(lid, s, xsrf)
        time.sleep(1)
        # 交卷
        submit(lid, s, xsrf)
        # 查看结果
        rlink = get_result(lid, s)
        detail_link = base_url + rlink
        print(detail_link)
        time.sleep(1)
        add2tiku(detail_link)
