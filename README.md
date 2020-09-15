# G9 사이트의 제품 이미지 Crawling Tool

## G9 사이트의 제품 이미지를 크롤링하여 저장합니다.

config.ini 파일에 아래 설정을 환경에 맞게 수정합니다.
 - webDriver 설치 path
 - 이미지 파일 저장 path
 - log 파일 설정

실행방법

    ./chromedriver 실행 후

    Running the script:
    python3 main.py -u <search_url> -c <category> -s <start_page_number> -e <end_page_number> -n <file_number>

    Explanation of args:
    -u <search_url> - 조회 URL(필수).
    -c <category> - 이미지 Category(필수).
    -s <start_page_number> - 시작 페이지(선택). 기본값은 1
    -e <end_page_number> - 종료 페이지(선택). 기본값은 10
    -n <file_number> - 저장파일명 시작번호(선택). 기본값은 1

    기본 이미지 저장 위치는 down_images/category 디렉토리에 1.jpg와 같이 저장됩니다.

