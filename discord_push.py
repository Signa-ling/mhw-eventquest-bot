import discord
import sqlite3

from contextlib import closing


def discord_connect():
    # 自分のbotのアクセストークン
    TOKEN = ''
    client = discord.Client()

    # 起動時の動作
    @client.event
    async def on_ready():
        print('ログインしました')

    # メッセージ受信時の動作
    @client.event
    async def on_message(message):
        # メッセージ送信者がBot → 無視
        if message.author.bot:
            return

        # /questコマンドで「クエスト難易度: クエストタイトル」の順でDiscordのチャンネルに投稿
        if message.content == '/quest':
            dbpath = 'questdata.db'
            with closing(sqlite3.connect(dbpath)) as conn:
                cur = conn.cursor()
                for row in cur.execute('SELECT * FROM this_weeks_quests'):
                    disp = str(row[2]) + ": " + str(row[1])
                    await message.channel.send(disp)

        # /helpコマンドでbotの操作方法を説明
        elif message.content == '/help':
            await message.channel.send(help_response())

    # Botの起動とDiscordサーバーへの接続
    client.run(TOKEN)


# 「コマンド名: コマンド概要」の並びで概要を説明
def help_response():
    help_comment = '''
/help: 本コマンド. ヘルプを表示
/quest: その週に配信されているクエストを表示
                   '''

    return help_comment


if __name__ == '__main__':
    discord_connect()
