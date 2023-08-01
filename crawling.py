import requests
import re
from bs4 import BeautifulSoup
import sys

# 기본 url
url = "https://fun.ssu.ac.kr"
# 펀시스템 프로그램 전체보기 url
t_url = url + "/ko/program/all/list/all/" + "1"

response = requests.get(t_url)

html = response.text
soup = BeautifulSoup(html, "html.parser")

postList = []  # 게시글 링크 크롤링 저장 리스트
for link in soup.find_all("a", href=re.compile(r"/all/view/")):
    postList.append(link.get("href"))

print(postList)  # 확인

for i in postList:
    # 게시글 링크 하나씩 접속
    # 현재 펀시스템 게시글 url
    t_url = url + i

    response = requests.get(t_url)

    t_html = response.text
    soup = BeautifulSoup(t_html, "html.parser")

    # 프로그램 title 크롤링
    title = soup.select_one(
        "#ModuleEcoProgramView > div:nth-child(1) > div > div:nth-child(2) > div > h4"
    )

    # 프로그램 한줄설명 크롤링
    # oneline_content = soup.select_one(
    #     "#ModuleEcoProgramView > div:nth-child(1) > div > div:nth-child(3) > div.abstract > div > div.text"
    # )

    content = soup.find("div", class_="description")

    # 대표 이미지 크롤링
    # 대표 이미지가 'cover'라는 이름으로 저장되어 있음.

    pattern = r"background-image:url\((.*cover.*)\);"
    cover_img = re.findall(pattern, t_html)

    img_files = []
    img_src_values = [img_tag["src"] for img_tag in soup.find_all("img", src=True)]

    if img_src_values:
        for src_value in img_src_values:
            img_files.append(src_value)
    else:
        continue

    # img_tags = soup.find_all("img")
    # if img_tags:
    #     print(img_tags)
    # else:
    #     print("nothing")

    # txt 파일로 크롤링 내용 정리
    orig_stdout = sys.stdout
    f = open("text.txt", "a", encoding="UTF-8")
    sys.stdout = f

    print(title.text.strip())
    # print(oneline_content.text.strip())
    print(content.get_text(separator="\n"))
    print(cover_img)
    print(img_files)
    print(t_url)
    print("\n")

    sys.stdout = orig_stdout
    f.close
