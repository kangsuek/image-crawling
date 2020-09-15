import argparse
import sys, os
from bs4 import BeautifulSoup
from selenium import webdriver
import urllib, urllib.request
import requests
from selenium.webdriver.common.keys import Keys
import configparser
import logging
import logging.handlers
import time
import datetime


def crawling_start(
    p_url, p_category, p_start_page_number, p_end_page_number, p_file_number
):
    # config.ini 파일로부터 기본 설정 값을 불러온다.
    config = configparser.ConfigParser()
    config.read("config.ini", encoding="utf-8")

    # selenium 의 webdriver path
    webDriver_path = config["CONFIG"]["webDriver"]

    # 이미지 저장 folder
    save_folder = config["CONFIG"]["saveFolder"]

    # loging 정보
    log_file = config["CONFIG"]["logFile"]
    log_level = config["CONFIG"]["logLevel"]
    log = logging.getLogger("snowdeer_log")
    if log_level == "INFO":
        log.setLevel(logging.INFO)
    else:
        log.setLevel(logging.DEBUG)

    # formatter = logging.Formatter(
    #     "[%(levelname)s] (%(filename)s:%(lineno)d) > %(message)s"
    # )

    formatter = logging.Formatter("%(message)s")

    log_max_size = 10 * 1024 * 1024  # 최대 10MB
    log_file_count = 20  # 총 20개 파일까지 생성
    fileHandler = logging.handlers.RotatingFileHandler(
        filename=log_file, maxBytes=log_max_size, backupCount=log_file_count
    )
    streamHandler = logging.StreamHandler()

    fileHandler.setFormatter(formatter)
    streamHandler.setFormatter(formatter)

    log.addHandler(fileHandler)  # log 파일로 저장
    log.addHandler(streamHandler)  # console로 출력

    ###
    category = p_category  # 카테고리
    start_page_number = int(p_start_page_number)  # 시작 페이지 번호
    end_page_number = int(p_end_page_number) + 1  # 종료 페이지 번호
    fileNum = int(p_file_number)  # 시작파일 번호

    now = datetime.datetime.now()
    nowDatetime = now.strftime("%Y-%m-%d %H:%M:%S")
    log.info(f"[{nowDatetime}] 크롤링 시작...")  # 시작 시간 출력

    start = time.time()  # 시작시각

    # 1page ~10page 까지 페이징하면서 이미지를 다운받는다.
    for page in range(start_page_number, end_page_number):
        url = p_url  # 조회 URL
        params = {"page": page, "sort": "g9best", "viewType": "B", "bsd": "off"}
        url = url + "?" + urllib.parse.urlencode(params)
        log.info(f"  {page}페이지 - URL: " + url)

        # selenium 의 webdriver를 사용하여 URL를 크롬브루우져를 사용하여 연다.
        browser = webdriver.Chrome(webDriver_path)
        time.sleep(0.5)
        browser.get(url)
        html = browser.page_source
        time.sleep(0.5)

        # 페이지의 이미지 갯수를 센다.
        soup_temp = BeautifulSoup(html, "html.parser")
        img4page = len(soup_temp.findAll("img", class_="itemcard lazy"))
        log.info(f"    {img4page}개 이미지 다운로드 중...")

        # G9에서 이미지를 화면에 보여줄때 lazy로딩하므로 PAGE_DOWN키를 전송하여
        # 브라우져에 보여지는 내용을 PAGE DOWN해서 모든이미지가 로딩되도록 처리
        elem = browser.find_element_by_tag_name("body")
        imgCnt = 0
        while imgCnt <= 13:  # 13번 페이지 다운한다.
            elem.send_keys(Keys.PAGE_DOWN)  # 브라우져에 PAGE_DOWN 키 전송
            time.sleep(1)  # 페이지 다운 할때마다 1초씩 멈추어 이미지가 모두 로딩되도록 한다.
            imgCnt += 1

        time.sleep(3)  # 페이지의 최하단까지 로딩하고 3초간 지연

        # HTML 소스를 파싱하여
        html = browser.page_source
        soup = BeautifulSoup(html, "html.parser")
        img = soup.findAll("img", class_="itemcard lazy")

        # browser.find_elements_by_tag_name("img")

        srcURL = []

        # 저장할 이미지 파일명
        # 1페이지의 경우 1부터 시작하고
        # 1페이지가 아니면 마지막 file명의 다음 번호부터 시작
        if page == 1:
            startFileNum = 1
        else:
            startFileNum = fileNum

        for line in img:
            if (
                str(line).find("//image.g9.co.kr/g/") != -1
                and str(line).find("src") != -1
                and str(line).find("itemcard lazy") != -1
            ):
                message = str(fileNum) + " : " + "https:" + str(line["src"])
                log.debug(message)

                srcURL.append("https:" + line["src"])
                fileNum += 1

        ### make folder and save picture in that directory
        saveDir = save_folder + category

        try:
            if not (os.path.isdir(saveDir)):
                os.makedirs(os.path.join(saveDir))
        except OSError as e:
            if e.errno != errno.EEXIST:
                log.error("Failed to create directory!!!!!")
                raise

        # URL의 이미지를 다운받아 저장한다.
        for i, src in zip(range(startFileNum, fileNum), srcURL):
            urllib.request.urlretrieve(src, saveDir + "/" + str(i) + ".jpg")

            message = str(i) + " saved"
            log.debug(message)

    # 실행시간 출력
    sec = time.time() - start
    times = str(datetime.timedelta(seconds=sec)).split(".")
    times = times[0]

    # 종료 시각
    now = datetime.datetime.now()
    nowDatetime = now.strftime("%Y-%m-%d %H:%M:%S")
    log.info(f"[{nowDatetime}] 크롤링 종료... [실행시간 : {times}]")  # 종료 시간 출력


def cli():

    """CLI"""
    ARGS_HELP = """
    G9 사이트의 제품 이미지 Crawling Tool
    G9 사이트의 제품 이미지를 크롤링하여 저장합니다.

    Running the script:
    python3 main.py -u <search_url> -c <category> -s <start_page_number> -e <end_page_number> -n <file_number>

    Explanation of args:
    -u <search_url> - 조회 URL(필수).
    -c <category> - 이미지 Category(필수).
    -s <start_page_number> - 시작 페이지(선택). 기본값은 1
    -e <end_page_number> - 종료 페이지(선택). 기본값은 10
    -n <file_number> - 저장파일명 시작번호(선택). 기본값은 1

    기본 이미지 저장 위치는 down_images/category 디렉토리에 1.jpg와 같이 저장됩니다.
    """
    parser = argparse.ArgumentParser(usage=ARGS_HELP)
    parser.add_argument(
        "-u",
        required=True,
        help="조회 URL을 입력하세요.",
        action="store",
        dest="search_url",
    )
    parser.add_argument(
        "-c",
        required=True,
        help="이미지 카테고리를 입력하세요.",
        action="store",
        dest="category",
    )
    parser.add_argument(
        "-s",
        required=False,
        help="시작 페이지번호를 입력하세요.",
        action="store",
        dest="start_page_number",
        default="1",
    )
    parser.add_argument(
        "-e",
        required=False,
        help="종료 페이지번호를 입력하세요.",
        action="store",
        dest="end_page_number",
        default="10",
    )
    parser.add_argument(
        "-n",
        required=False,
        help="저장파일명 시작번호를 입력하세요.",
        action="store",
        dest="file_number",
        default="1",
    )

    args = parser.parse_args()
    # Parse arguments
    search_url = args.search_url
    category = args.category
    start_page_number = args.start_page_number
    end_page_number = args.end_page_number
    file_number = args.file_number

    # 크롤링 시작
    crawling_start(
        search_url, category, start_page_number, end_page_number, file_number
    )


# command line 명령으로 실행 시
if __name__ == "__main__":
    cli()