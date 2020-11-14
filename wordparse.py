import re
import traceback
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy import event

# engine = create_engine('sqlite:///tiku.sqlite?check_same_thread=False', echo=False)  # false 不打印 sql 语句
engine = create_engine("mysql+pymysql://root:814976@localhost:3306/tiku",
                       encoding="utf-8", echo=False)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()


# @event.listens_for(Engine, "connect")
# def set_sqlite_pragma(dbapi_connection, connection_record):
#     cursor = dbapi_connection.cursor()
#     cursor.execute("PRAGMA journal_mode=WAL")
#     cursor.close()


class Tiku(Base):
    __tablename__ = 'tiku'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(500))  # 题目
    type = Column(String(10))  # 类型
    choice = Column(String(500))  # 选项
    answer = Column(String(150))  # 答案

    def save(self):
        session.add(self)
        session.commit()

    def check_title_save(self):
        # same question
        if session.query(Tiku).filter(Tiku.title == self.title).first():
            return
        session.add(self)
        session.commit()

    def update_title_save(self):
        item = session.query(Tiku).filter(Tiku.title == self.title).first()
        if item:
            item.type = self.type
            item.choice = self.choice
            item.answer = self.answer
            session.add(item)
            session.commit()
        else:
            print("add:", self.type, self.title, self.choice, self.answer)
            session.add(self)
            session.commit()

    def delete(self):
        session.delete(self)
        session.commit()


# 保证输入编码都是 utf8

def readTxt2Arr(name):
    fhandlr = open(name, encoding='utf8', errors='ignore')
    rawtxt = fhandlr.read()
    fhandlr.close()
    rawtxt = re.sub(r'答错次数.*?次', "", rawtxt)
    rawtxt = re.sub(r'易错率：.*?%', "", rawtxt)
    rawtxt = re.sub(r'\n', "\n", rawtxt)
    rawtxt = re.sub(r'[\\n]+', "\n", rawtxt)
    arryTxt = rawtxt.replace('\xa0', '').replace('\uf0b7', '').replace('\ue60f', '').replace('\ue6e2', '').split('\n')
    return arryTxt


def reapaire(index):
    # 修正 判断少了一行的情况
    maxlines = 2
    line = 1
    if index < maxlines or (index + maxlines) > length:
        return index
    while line <= maxlines:
        if re.search(questionRe['dan'], tiku1[index - line]):
            index = index - line
            return index

        elif re.search(questionRe['duo'], tiku1[index - line]):
            index = index - line
            return index

        elif re.search(questionRe['pan'], tiku1[index - line]):
            index = index - line
            return index

        elif re.search(questionRe['tian'], tiku1[index - line]):
            index = index - line
            return index

        elif re.search(questionRe['dan'], tiku1[index + line]):
            index = index + line
            return index

        elif re.search(questionRe['duo'], tiku1[index + line]):
            index = index + line
            return index

        elif re.search(questionRe['pan'], tiku1[index + line]):
            index = index + line
            return index

        elif re.search(questionRe['tian'], tiku1[index + line]):
            index = index + line
            return index
        line = line + 1
    return index


def main(index):
    while index < length:
        print(index)
        question = tiku1[index]  # 26、【单选题】 下列有关中国
        parseQ = re.search(reQuestion, question)
        try:
            title = parseQ.group(2)
            type = parseQ.group(1)  # 单选题
        except AttributeError as e:
            if index + 5 > length:
                exit(0)
            print(e, traceback.print_exc())
            print(index, tiku1[index - 2:index + 6])
            exit(0)
        choiceIndex = index + 1
        # 单选
        if re.search(questionRe['dan'], question):
            choice = '|'.join(tiku1[choiceIndex:choiceIndex + 4])  # 4个选项
            answerIndex = choiceIndex + 4
            try:
                answer = re.search(reOptMarker, tiku1[answerIndex]).group(0)
                index = index + spacing['dan']
                index = reapaire(index)
                tiku_item = Tiku(title=title, type=type, choice=choice, answer=answer)
                tiku_item.check_title_save()
            except AttributeError as e:
                print(e, traceback.print_exc())
                print(tiku1[answerIndex])
                exit(0)

        # 多选
        elif re.search(questionRe['duo'], question):
            choice = '|'.join(tiku1[choiceIndex:choiceIndex + 4])  # 4个选项
            answerIndex = choiceIndex + 4
            try:
                answer = re.search(reOptMarker, tiku1[answerIndex]).group(0)
                index = index + spacing['duo']
                index = reapaire(index)
                tiku_item = Tiku(title=title, type=type, choice=choice, answer=answer)
                tiku_item.check_title_save()
            except AttributeError as e:
                print(e, traceback.print_exc())
                print(tiku1[answerIndex])
                exit(0)

        # 判断
        elif re.search(questionRe['pan'], question):
            choice = '|'.join(tiku1[choiceIndex:choiceIndex + 2])  # 2个选项
            answerIndex = choiceIndex + 2
            answer = re.search(reOptMarker, tiku1[answerIndex]).group(0)
            index = index + spacing['pan']
            index = reapaire(index)
            tiku_item = Tiku(title=title, type=type, choice=choice, answer=answer)
            tiku_item.check_title_save()

        # 填空
        elif re.search(questionRe['tian'], question):
            choice = ''.join(tiku1[choiceIndex:choiceIndex + 2]).strip().replace(' ', '')  # 正确选项
            answer = tiku1[choiceIndex + 1].strip().replace(' ', '')  # 正确选项
            index = index + spacing['tian']
            index = reapaire(index)
            tiku_item = Tiku(title=title, type=type, choice=choice, answer=answer)
            tiku_item.check_title_save()


if __name__ == '__main__':
    Base.metadata.create_all(engine, checkfirst=True)

    tiku1 = readTxt2Arr('tiku1.txt')

    questionRe = {
        'dan': re.compile(r'单选题'),
        'duo': re.compile(r'多选题'),
        'pan': re.compile(r'判断题'),
        'tian': re.compile(r'填空题')
    }

    # 到下一题的间隔
    spacing = {
        'dan': 7,  # 默认4个选项
        'duo': 7,  # 默认4个选项
        'pan': 5,  # 默认2个选项
        'tian': 7  # 默认2个选项
    }
    reQuestion = re.compile(r'\d{0,3}[.、【]*(.*?)[】*](.*)')
    reOptMarker = re.compile(r'[A-G]+')
    reOptoneMarker = re.compile(r'^[A-G][\s\.．、,，]?')

    index = 0
    length = len(tiku1)

    print(length)
    main(index)
