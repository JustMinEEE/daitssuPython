import bs4.element
import requests
from bs4 import BeautifulSoup
from datetime import date
from datetime import datetime
from sqlalchemy import create_engine, Table, MetaData, ForeignKey, Text
from sqlalchemy.orm import sessionmaker, declarative_base, Mapped, mapped_column
from sqlalchemy import Column, Integer, CHAR, ARRAY, DateTime
import sqlalchemy
import dev_db

AI_BASE_URL = "http://aix.ssu.ac.kr/"

Base = declarative_base()

db_url = sqlalchemy.engine.URL.create(
    drivername="postgresql+psycopg2",
    username=dev_db.dev_user_name,
    password=dev_db.dev_db_pw,
    host=dev_db.dev_host,
    database=dev_db.dev_db_name,
)

engine = create_engine(db_url)
session_maker = sessionmaker(autoflush=False, autocommit=False, bind=engine)
metadata_obj = MetaData()


class AiNotification(Base):
    __tablename__ = "notice"
    __table_args__ = {"schema": "notice"}
    id = Column(Integer, primary_key=True)
    title = Column(CHAR(1024))
    department_id = Column(Integer)
    content = Column(CHAR(2048))
    category = Column(CHAR(32))
    image_url = Column(ARRAY(CHAR(2048)))
    file_url = Column(ARRAY(CHAR(2048)))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    def __init__(self, row: bs4.element.Tag):
        childrens = row.find_all("td")

        if childrens:
            href = childrens[0].find("a")["href"]
            self.__link = AI_BASE_URL + href
        else:
            return

        req = requests.get(self.__link)
        soup = BeautifulSoup(req.text, "lxml")
        contents = soup.find("table", class_="table").find_all("p")

        # 제목
        self.title = childrens[0].text.strip()

        # 내용
        self.content = ""
        for content in contents:
            self.content += content.text

            # if (
            #     len(self.content.encode("utf-8")) + len(self.content.encode("utf-8"))
            #     > 2048
            # ):
            #     print("content size extend")
            #     break

        # 카테고리
        self.category = "AI융합학부"

        # 이미지
        self.image_url = []

        # 파일
        contents = soup.find("table", class_="table").find("a")["href"]
        print(contents)
        # file_container = content[3].find(class_="file")
        # if file_container is not None:
        #     files = file_container.findAll("a")

        # files = None
        # file_link = []
        # if files is not None:
        #     for file in files:
        #         link = AI_BASE_URL + file["href"]
        #         file_link.append(link)

        # self.file_url = file_link
        self.file_url = []

        # 생성 시각
        created_date = list(map(int, childrens[2].text.split(".")))
        self.created_at = date(created_date[0], created_date[1], created_date[2])

        # 업데이트 시각
        self.updated_at = datetime.now().strftime("%Y-%m-%d")

        with engine.connect() as connect:
            department_table = Table(
                "department", metadata_obj, schema="main", autoload_with=engine
            )
            # department_table에 ai융합학부가 없는 듯해서 일단 컴퓨터학부로 했습니다.
            query = department_table.select().where(department_table.c.name == "컴퓨터학부")
            results = connect.execute(query)
            for result in results:
                self.department_id = result.id

    def __str__(self):
        return (
            "title: {0}\n"
            "content: {1}\n"
            "image_url: {2}\n"
            "file_url: {3}\n"
            "department_id: {4}".format(
                self.title,
                self.content,
                self.image_url,
                self.file_url,
                self.department_id,
            )
        )


def ai_department_crawling(value):
    page = 1
    url = AI_BASE_URL + "notice.html?searchKey=ai"
    req = requests.get(url)
    soup = BeautifulSoup(req.text, "lxml")
    content = soup.find("table", class_="table")
    rows = content.find_all("tr")
    results = []

    for row in rows[1:4]:
        results.append(AiNotification(row))

    with session_maker() as session:
        for result in results:
            session.add(result)
            # print(result)  # db 삽입 내용 확인 출력문

        session.commit()


def departments_crawling(value):
    ai_department_crawling(value)


departments_crawling(1)
