# 標準
import re
import time
import random
import traceback
from urllib.request import urlopen, Request
from pathlib import Path

# サードパーティ
from tqdm import tqdm
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# ローカル
# from constants import RACE_DETAIL_HTML_DIR
# from constants import HORSE_DETAIL_HTML_DIR

def url_open_with_headers(url: str):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
    }
    request = Request(url, headers=headers)
    html = urlopen(request).read()
    return html


def scrape_kaisai_date(from_: str, to_: str) -> list[str]:
    """
    netkeibaからレース開催日をfrom-toで取得

    Args:
      from_ (str): "yyyy-mm"
      to_ (str): "yyyy-mm"
    Return:
      date_list (list[str]): from-toのレース開催日一覧
    """
    kaisai_date_list = []
    for date in tqdm(pd.date_range(from_, to_, freq="MS")):
        year, month = date.year, date.month
        url = f"https://race.netkeiba.com/top/calendar.html?pid=race_calendar&year={year}&month={month}"
        html = url_open_with_headers(url)
        time.sleep(1)  # 忘れない
        soup = BeautifulSoup(html, features="lxml")
        a_tag_list = soup.find("table", class_="Calendar_Table").find_all("a")

        for a_tag in a_tag_list:
            kaisai_date = re.findall(r"kaisai_date=(\d{8})", a_tag["href"])[0]
            kaisai_date_list.append(kaisai_date)

    return kaisai_date_list


def scrape_race_ids(race_date_list: list[str]) -> list[str]:
    """
    レース日付一覧からレースIDを取得

    Args:
      race_date_list (list[str]): ["yyyymm", ...]
    Return:
      race_id_list (list[str]): 指定した開催日のraceId一覧
    """
    driver_options = Options()
    driver_options.add_argument("--headless")  # ヘッドレスで実行
    driver_path = ChromeDriverManager().install()
    race_id_list = []
    with webdriver.Chrome(
        service=Service(driver_path), options=driver_options
    ) as driver:
        for race_date in tqdm(race_date_list):
            url = (
                f"https://race.netkeiba.com/top/race_list.html?kaisai_date={race_date}"
            )
            try:
                driver.get(url)
                sleep_time = random.uniform(1.0, 1.5)
                time.sleep(sleep_time)  # 忘れない
                li_list = driver.find_elements(By.CLASS_NAME, "RaceList_DataItem")

                for li in li_list:
                    href = li.find_element(By.TAG_NAME, "a").get_attribute("href")
                    race_id = re.findall(r"race_id=(\d{12})", href)[0]
                    race_id_list.append(race_id)
            except:
                print("stop at", url)
                print(traceback.format_exc())
                break

    return race_id_list


def scrape_race_detail_html(race_id_list: list[str], save_dir: Path) -> list[Path]:
    """
    レース詳細画面のHTMLの書出し & filepathリストを作成

    Args:
      race_id_list (list[str]): ["id1", ...]
      save_dir (Path): 出力ディレクトリ
    Return:
      html_path_list (list[Path]): 書き出したファイルのパス
    """
    # ディレクトリの作成
    save_dir.mkdir(parents=True, exist_ok=True)
    html_path_list = []
    for race_id in tqdm(race_id_list):
        # file exists check
        filepath = save_dir / f"{race_id}.bin"
        if filepath.is_file():
            print("skipped", filepath)
            continue

        # scraping
        url = f"https://db.netkeiba.com/race/{race_id}"
        html = url_open_with_headers(url)
        sleep_time = random.uniform(1.0, 1.5)
        time.sleep(sleep_time)

        # write html
        with open(filepath, "wb") as f:
            f.write(html)

        html_path_list.append(filepath)

    return html_path_list



def scrape_horse_detail_html(
        horse_id_list: list[str], 
        save_dir: Path,
        skip: bool = True
) -> list[Path]:
    """
    レース詳細画面のHTMLの書出し & filepathリストを作成

    Args:
      horse_id_list (list[str]): ["id1", ...]
      save_dir (Path): 出力ディレクトリ
    Return:
      html_path_list (list[Path]): 書き出したファイルのパス
    """
    # ディレクトリの作成
    save_dir.mkdir(parents=True, exist_ok=True)
    html_path_list = []
    for horse_id in tqdm(horse_id_list):
        # file exists check
        filepath = save_dir / f"{horse_id}.bin"
        if filepath.is_file() and skip:
            print("skipped", filepath)
            continue

        # scraping
        url = f"https://db.netkeiba.com/horse/{horse_id}"
        html = url_open_with_headers(url)
        sleep_time = random.uniform(1.3, 1.8)
        time.sleep(sleep_time)

        # write html
        with open(filepath, "wb") as f:
            f.write(html)

        html_path_list.append(filepath)

    return html_path_list
