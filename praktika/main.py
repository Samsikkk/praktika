from typing import Dict
from mods import parser
from telegram import *
from telegram.ext import *
import configparser
from dataclasses import dataclass
import psycopg2


USERINPUT = ""

config = configparser.ConfigParser()
config.read("mods/db_config.ini")
conn = psycopg2.connect(dbname=config["db"]["dbname"], user=config["db"]["user"],
                        password=config["db"]["password"], host=config["db"]["host"])
cursor = conn.cursor()
conn.autocommit = True

@dataclass
class Vacancy:
    VacId: int
    vacName: str
    url: str
    company: str
    salary: int
    currency: str
    location: str
    metro: str

def insertVacancy(vac: Vacancy) -> None:
    cursor.execute(f"INSERT INTO results VALUES ({vac.VacId}, {vac.vacName}, {vac.url}, {vac.company}, {vac.salary}, {vac.currency}, {vac.location}, {vac.metro})")
    cursor.commit()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Добро пожаловать в бота по поиску вакансий на hh.ru. Заполните параметры по которым хотите найти вакансию, всем незаполненным полям будут переданны стандартные значения.\nПишите следующие параметры в указанной последовательности через пробелы:\n(Название вакансии/определенное умение, город/страна, желаемая зарпалата, сколько вакансий вывести)\nна месте незадействованных параметров пишите skip. Пример ввода ->\n\n/create_resume Python_разработчик Москва 170000 20"
    )


async def create_resume(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text_caps = ' '.join(context.args)
    global USERINPUT
    USERINPUT = text_caps


async def findJob(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    toFind = ["Python Developer", 1, 0, 10]
    line = list(map(str, USERINPUT.split(" ")))
    print(*line)
    if len(line) != 4:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Неправльно составленно резюме, попробуйте еще раз"
        )
        return

    for i in range(len(line)):
        if line[i] != "skip":
            if i < 2:
                if "_" in line[i]:
                    line[i] = line[i].replace("_", " ")
                toFind[i] = line[i]
                continue
            toFind[i] = int(line[i])
    buffDict = parser.getVacancies(toFind[0], toFind[1], toFind[2], toFind[3])
    if len(buffDict) != 0:
        slr = 0
        for var in buffDict:
            for keys in var:
                if var[keys] == None:
                    var[keys] = "NULL"
                    continue
                if (keys == "salary"):
                    slr = var[keys]["from"]


            insertVacancy(vacancy = Vacancy(VacId=var["id"], vacName=var["name"], url=var["url"], company=var["company"], salary=slr, currency=var["currency"], location=toFind[1], metro=var["metro"]))

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Вакансии найдены, вот ссылки. Вся остальная полезная информация записана в базу данных!"
        )
        for vac in buffDict:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=vac["url"]
            )
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Результатов не найдено, извините"
        )


def main() -> None:
    TOKEN = open("TOKEN.txt").read()
    bot = ApplicationBuilder().token(TOKEN).build()
    bot.add_handler(CommandHandler("start", start))
    bot.add_handler(CommandHandler('create_resume', create_resume))
    bot.add_handler(CommandHandler("find_job", findJob))

    bot.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
