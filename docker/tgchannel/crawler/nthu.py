from modules import Crawler
from modules import TGMySQL
import telepot
import os


def send_msg(title, link):
    bot = telepot.Bot(os.environ["TELEPOT_TOKEN"])

    try:
        bot.sendMessage(-1001429244108, title + "\n" + link)
        print("新增一筆新的文章：", title)
    except:
        print("time out :", title)


def main():
    SQL = TGMySQL.TGMySQL()
    SQL.connect_SQL("NTHU_IPTH")

    tables = Crawler.Crawler()

    for announce in tables:
        news = announce.find(class_='ptname').a
        data = announce.find(class_='date').string
        title = str(news.string)
        link = str(news.get('href'))

        nonexistent = SQL.check_SQL("NTHU_IPTH", title)
        if nonexistent:
            SQL.insert_SQL(title, link, str(data).split()[1])
            send_msg(title, link)
        else:
            print("沒有新的文章了")

    SQL.close_SQL()


if __name__ == "__main__":
    main()
