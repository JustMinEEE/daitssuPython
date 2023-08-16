from bs4 import BeautifulSoup
import requests
from datetime import datetime
import sqlite3

# 웹 페이지에서 프로그램 정보 가져오기
Fun = "https://fun.ssu.ac.kr/ko/program"
html = requests.get(Fun)
html_text = html.text
soup = BeautifulSoup(html_text, "html.parser")
tag_ul = soup.find("ul", {"class": "columns-4"})

# 데이터베이스에 연결 설정
conn = sqlite3.connect("program_data.db")
cursor = conn.cursor()

# 프로그램 데이터를 저장할 테이블 생성 (이미 있는 경우에는 무시)
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS programs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        url TEXT,
        image_url TEXT,
        created_time TIMESTAMP,
        updated_time TIMESTAMP,
        content TEXT
    )
"""
)
conn.commit()


# 프로그램 호출 시각
current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# 각 프로그램 정보를 크롤링하여 데이터베이스에 삽입
for data in tag_ul.find_all("li"):
    # 프로그램 제목
    data_title = data.select_one("b.title").get_text()

    # 프로그램 게시글 url
    data_link = data.find("a")

    # 프로그램 대표 이미지
    img_style = data.find("div", {"class": "cover"})["style"]
    strat = img_style.index("(") + 1
    end = img_style.index(")")
    image = img_style[strat:end]

    # 프로그램 업데이트 시각
    created_time_element = data_link.find("time")["datetime"]

    created_time = datetime.fromisoformat(created_time_element)
    created_time = created_time.strftime("%Y-%m-%d %H:%M:%S")

    # 프로그램 내용 가져오기 (이전 내용 유지)
    content_url = "https://fun.ssu.ac.kr" + data_link.get("href")
    html_content = requests.get(content_url)
    html_content_text = html_content.text
    soup_content = BeautifulSoup(html_content_text, "html.parser")
    content = ""

    for tag in soup_content.find_all(["p", "table"]):
        if tag.name == "p":
            # 이미지, 링크, 동영상인 경우
            if tag.find("img"):
                img_src = tag.find("img")["src"]
                content += f"Image: {img_src}\n"
            elif tag.find("a"):
                link_tag = tag.find("a")
                if link_tag and "href" in link_tag.attrs:
                    link_href = link_tag["href"]
                    link_text = link_tag.get_text(strip=True)
                    content += f"Link: {link_text} - {link_href}\n"
            elif tag.find("iframe"):
                link_tag = tag.find("iframe")
                link_href = link_tag["src"]
                link_text = link_tag.get_text(strip=True)
                content += f"Video Link: {link_text} - {link_href}\n"
            else:
                text_content = tag.get_text(strip=True)
                content += f"{text_content}\n"

        elif tag.name == "table":
            content += "Table Contents:\n"
            for row in tag.find_all("tr"):
                row_contents = [
                    cell.get_text(strip=True) for cell in row.find_all("td")
                ]
                content += "\t/ ".join(row_contents) + "\n"

    # 데이터 존재 여부 확인 및 업데이트 시각 설정
    cursor.execute(
        "SELECT * FROM programs WHERE url=?",
        ("https://fun.ssu.ac.kr" + data_link.get("href"),),
    )
    existing_data = cursor.fetchone()
    if existing_data:
        updated_time = current_time
        cursor.execute(
            """
            UPDATE programs
            SET updated_time=?, content=?
            WHERE url=?
        """,
            (updated_time, content, "https://fun.ssu.ac.kr" + data_link.get("href")),
        )
    else:
        updated_time = None
        cursor.execute(
            """
            INSERT INTO programs (title, url, image_url, created_time, updated_time, content)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                data_title,
                "https://fun.ssu.ac.kr" + data_link.get("href"),
                "https://fun.ssu.ac.kr" + image,
                created_time,
                updated_time,
                content,
            ),
        )

    conn.commit()


# 프로그램 데이터 출력
cursor.execute("SELECT * FROM programs")
programs_data = cursor.fetchall()

for program in programs_data:
    print("Title:", program[1])
    print("URL:", program[2])
    print("Image URL:", program[3])
    print("Created Time:", program[4])
    print("Updated Time:", program[5])
    print("Content:", program[6])
    print(
        "========================================================================================"
    )


# 데이터베이스 연결 닫기
conn.commit()
conn.close()
