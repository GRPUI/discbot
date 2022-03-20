import discord
import urllib3  # библиотека для работы с URL
import os  # библиотека для работы с ОС
import random  # библиотека рандом
import sqlite3  # библиотека для работы с БД SQL
import time  # библиотека для работы со временем
import schedule
import threading
from datetime import datetime, timedelta
import asyncio
from discord.ext import tasks

db = sqlite3.connect('database.db', check_same_thread=False)  # подключение БД
sql = db.cursor()

TOKEN = 'OTUzNTI0NzQ5MTI3MDAwMTI0.YjF1Hw.igjoga7hT3t05NPPvT7IhaQ8w7w'


class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as', self.user)

    async def on_message(self, message):
        print(f"{str(message.author).split('#')[0]}: {message.content}, {str(message.channel.name)}")
        if message.author == self.user:
            return

        if str(message.content).startswith('!guide') and len(str(message.content).split()) > 1:
            obj = str(message.content).split()[1]
            sql.execute("SELECT Hero FROM Guides WHERE Hero = ?", (obj,))
            fetch = sql.fetchall()
            if fetch:
                sql.execute("SELECT Text FROM Guides WHERE Hero = ?", (obj,))
                text = (sql.fetchone())[0]
                await message.channel.send(text)
            else:
                await message.channel.send('Here is no one suitable guide for your request. Please, check the correct '
                                           'of your request and send the new one.')

        if str(message.content).startswith('!tournament'):
            creator = message.author.id
            parts = str(message.content).split(" ")
            mode = parts[1]
            date = parts[2]
            year = str(date).split('.')[2]
            month = str(date).split('.')[1]
            day = str(date).split('.')[0]
            date = f"{year}-{month}-{day}"
            sql.execute(f"SELECT ID FROM tournament")
            ID = len(sql.fetchall()) + 1
            sql.execute(f"INSERT INTO tournament VALUES(?, ?, ?, ?)", (ID, creator, mode, date))
            db.commit()

        if str(message.content).startswith('!join'):
            user = int(message.author.id)
            parts = str(message.content).split(" ")
            ID = int(parts[1])
            InGameName = parts[2:]
            GameName = ''
            for part in InGameName:
                GameName += part + " "
            sql.execute(f"SELECT ID FROM tournament WHERE ID = ?", (ID,))
            fetch = sql.fetchall()
            sql.execute(f"SELECT ID FROM participants WHERE ID = ? AND tournamentId = ?", (user, ID))
            userFetch = sql.fetchall()
            if fetch and not userFetch:
                sql.execute(f"INSERT INTO participants VALUES(?, ?, ?)", (user, GameName, ID))
                db.commit()
                await message.channel.send(f'<@{str(user)}>, you have been added to the tournament with id {ID}.')
            elif not fetch:
                await message.channel.send('It seems like here is no tournament you searched.')
            else:
                await message.channel.send('Bruh, you already in tournament.')

        if message.content == '!hey':
            sql.execute(f"SELECT ID FROM tournament")
            for tourId in sql.fetchall():
                tourId = int(tourId[0])
                sql.execute(f"SELECT date FROM tournament WHERE ID = ?", (int(tourId),))
                time = sql.fetchall()[0][0]
                if time == str(datetime.today()).split(' ')[0]:
                    sql.execute(f"SELECT ID FROM participants WHERE TournamentId = ?", (tourId,))
                    for userId in sql.fetchall():
                        await message.channel.send(f"<@{userId[0]}>, today is the great day. I mean the tournament "
                                                   f"day :)")


client = MyClient()
client.run(TOKEN)
