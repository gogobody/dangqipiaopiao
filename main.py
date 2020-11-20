import re

import requests
from lxml import etree
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, and_
from wordparse import Tiku ,mysqlname ,password
import time

engine = create_engine("mysql+pymysql:{0}:{1}//@localhost:3306/tiku".format(mysqlname,password),
                       encoding="utf-8", echo=False)
DbSession = sessionmaker(bind=engine)
db_session = DbSession()

s = requests.session()

cookie = ''
ifnonematch = ''
headers = {
    'Cache-Control': 'max-age=0',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36',
    'cookie': cookie,
    'If-None-Match': ifnonematch,
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


def get_lesson_xsrf_token(lseeion_id, exam_center = False):
    if exam_center:
        html = s.get("http://cqu.dangqipiaopiao.com/jjfz/exam_center/end_exam").text
    else:
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


def get_questions(lid, num=20, exam_center=False):
    questions_all = []
    for i in range(1, num + 1):
        params = {'i': i, 'lid': lid}
        if exam_center:
            test = s.get("http://cqu.dangqipiaopiao.com/jjfz/exam_center/get_question?i=2", params={"i": i})
        else:
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


def answer_questions(index, lid, qid, answer, xsrf, exam_center=False):
    dat = {
        'i': index,
        'lid': lid,
        'qid': qid,
        'answer': answer,
        '_xsrf': xsrf
    }
    if exam_center:
        answer = s.post('http://cqu.dangqipiaopiao.com/jjfz/exam_center/answer?i='+str(index), data=dat)
    else:
        answer = s.post('http://cqu.dangqipiaopiao.com/jjfz/lesson/exam/answer?i='+str(index), data=dat)
    # print(answer.status_code, answer.text)


# 开始做题
def start_exam(lid, s, xsrf, num=20, exam_center=False):
    rQpattern1 = re.compile(r'\d{0,3}[. ]{0,3}(.*?)[(（]+')
    # print(xsrf)
    questions = get_questions(lid, num, exam_center)
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
            answer_questions(index + 1, lid, q['qids'][0], answ, xsrf, exam_center)
            time.sleep(1)
        else:
            print("index: {0} unknown q: ".format(index + 1), q)
            print('|'.join(q['choice']))
            # 全部 蒙 A
            answer_questions(index + 1, lid, q['qids'][0], q['amswers'][0], xsrf, exam_center)
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
        type = re.search(reQuestion, title).group(1)
        if type == "填空题":
            answer = ''.join(it.xpath('div[2]/div[1]/div[1]/text()'))
            question = re.search(reQuestion, title).group(2)
            tiku_item = Tiku(title=question, type=type, choice=answer, answer=answer)
            tiku_item.update_title_save()
            continue

        choices_ele = it.xpath('div[2]/ul/li')
        choices = []
        for c in choices_ele:
            choice = ''.join(c.xpath('label/text()')).replace('\\n', '').replace('\n', '').replace('\t', '').replace(
                ' ', '')
            if choice:
                choices.append(choice)
        else:
            answer = ''.join(it.xpath('div[3]/span/text()'))
            if answer:
                answer = re.search(reOptMarker, answer).group()
                question = re.search(reQuestion, title).group(2)
                tiku_item = Tiku(title=question, type=type, choice='|'.join(choices), answer=answer)
                tiku_item.update_title_save()
    print("finished")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # start_lesson_self_test(495)
    base_url = "http://cqu.dangqipiaopiao.com"
    s = update_session(s)
    # 单元自测
    # lid = 495
    # xsrf = get_lesson_xsrf_token(lid)
    # for lid in range(495, 506):
    #     # 开始自测
    #     start_lesson_self_test(lid)
    #     time.sleep(1)
    #     # 开始做题
    #     start_exam(lid, s, xsrf)
    #     time.sleep(1)
    #     # 交卷
    #     submit(lid, s, xsrf)
    #     # 查看结果
    #     rlink = get_result(lid, s)
    #     detail_link = base_url + rlink
    #     print(detail_link)
    #     time.sleep(1)
    #     add2tiku(detail_link)

    # 考试中心综合检测
    # exam_center
    # lid = 1
    # xsrf = get_lesson_xsrf_token(lid,exam_center=True)
    # start_exam(lid, s, xsrf, num=80 ,exam_center=True)
    # add2tiku("http://cqu.dangqipiaopiao.com/jjfz/exam_center/end_show?rid=41974")
