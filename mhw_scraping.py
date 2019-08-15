import sqlite3
import schedule
import datetime

from time import sleep
from contextlib import closing

from urllib3 import PoolManager
from bs4 import BeautifulSoup


def eventquest_scraping():
    # dbとスクレイピングしたデータを一時的に入れておくリスト
    dbpath = "questdata.db"
    quests = []
    difficulties = []
    quest_info = []

    # 時刻の取得
    diff_jst_from_utc = 9
    dt_now = datetime.datetime.utcnow() + datetime.timedelta(hours=diff_jst_from_utc)

    with closing(sqlite3.connect(dbpath)) as conn:
        c = conn.cursor()

        # テーブルが存在する場合一度消しておく
        c.execute('SELECT COUNT(*) FROM sqlite_master WHERE TYPE="table" AND NAME="this_weeks_quests"')
        if not c.fetchone() == (0,):
            droptable = "drop table this_weeks_quests;"
            c.execute(droptable)
            print("Table is deleted.")
        create_table = '''create table this_weeks_quests (id integer primary key, title text,
                          difficulty text, updatetime text)'''

        c.execute(create_table)
        print("Create table this_weeks_quests")

        # ここからスクレイピング
        url = "http://game.capcom.com/world/ja/schedule.html"
        pool_mng = PoolManager()
        html = pool_mng.request("GET", url)
        soup = BeautifulSoup(html.data, "html.parser")

        for trs in soup.find_all("tr", class_="t1"):
            for diff in trs.find_all("td", class_="level"):
                difficulties.append(diff.text)
                print("diff: " + str(len(difficulties)))
                sleep(1)

            for titles in trs.find_all("div", class_="title"):
                for title in titles.find_all("span"):
                    quests.append(title.text)
                    print(len(quests))
                    sleep(1)

        print("Finish Scraping!")

        for i in range(len(quests)):
            quest_info.append((i + 1, quests[i], difficulties[i], dt_now))

        insert_sql = 'insert into this_weeks_quests (id, title, difficulty, updatetime) values (?,?,?,?)'
        c.executemany(insert_sql, quest_info)
        conn.commit()
        print("Commit Database!")


if __name__ == "__main__":
    Flag = False
    if Flag == False:
        eventquest_scraping()
        Flag = True

    schedule.every().at("00:00").do(eventquest_scraping)
    while True:
        schedule.run_pending()
