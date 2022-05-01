import telebot
from telebot.apihelper import ApiTelegramException
import pickle
from threading import Thread
from time import sleep

# лучше удалит
import schedule
# тута пихать сообщения

# Todo: Список людей в отдельный

class TeleBoolichka:
    def __init__(self, GoogleApi):
        self.token = '1692760548:AAEnk5OnQ_b4tRtlr02TFoeazoHX8TkFM3g'
        self.GoogleApi = GoogleApi

    def spam(self) -> [str]:
        """Создает строку, которую нужно отправить для спама"""

        ans = self.GoogleApi.new_answers(0)
        if ans > 0:
            msg = f'\[ALERT] Форму на организаторов заполнили {ans} человек:\n\n\n'
            for i in range(ans):
                responce = self.GoogleApi.get_responce(0, i, True)
                info = identify(responce, self.GoogleApi.FormsId[0])
                msg += f'_{info["Время"]}_\n*{info["ФИО"]}*\n' \
                       f'*ВУЗ* - {info["ВУЗ"]}\n*Факультет* - {info["Факультет"]}\n*Курс* - {info["Курс"]}.\n' \
                       f'*ВК* - {info["ВК"]}\n*Почта* - {info["Почта"]}\n\n'
            return msg  # Цикл работает
        else:
            return -1


def identify(responce, form_id=0) -> {str, str, str, bool, str, int, str, str}:
    """ Вставить один респонс человека, которого нужно определить и разобрать
        возвращает то шо нада. [0 ФИО, 1 пол М/Ж T/F, 2 ВУЗ, 3 Факультет 4 КУРС, 5 почту, 6 вк 7 время"""

    form_Q = pickle.load(open('FormsQuestions.pickle', 'rb'))[form_id]
    person = {'Время': responce['createTime'][:-5].replace('T', ' ')}
    responce = responce['answers']

    for key in form_Q.keys():
        if form_Q[key] in responce.keys():
            person[key] = responce[form_Q[key]]['textAnswers']['answers'][0]['value']
    if (person['ФИО'][:-1] == 'а') or (person['ФИО'][:-1] == 'я'):
        person['Пол'] = False
    else:
        person['Пол'] = True
    return person

def schedule_checker():
    while True:
        schedule.run_pending()
        sleep(1)

def run(Forms):
    print('bot run')
    botlogic = TeleBoolichka(Forms)
    # print(Forms.new_answers())
    bot = telebot.TeleBot(botlogic.token)
    def function_to_run():
        print('function tu run')
        Ids_to_spam = pickle.load(open('Chat_ids.pickle', 'rb'))
        for i in Ids_to_spam:
            try:
                spam = botlogic.spam()
                if spam != -1:
                    bot.send_message(i, spam, parse_mode= 'Markdown')
                else:
                    print('nospam')
                    break
            except ApiTelegramException as e:
                print(e.result)
                print(e)
                print(e.error_code)
                if e.error_code == 403:
                    print('ERROR LOH ALARM')
                    ids = pickle.load(open('Chat_ids.pickle', 'rb'))
                    ids.remove(i)
                    pickle.dump(set(ids), open('Chat_ids.pickle', 'wb'))

                    ids = pickle.load(open('ErrorUsers.pickle', 'rb'))
                    ids.add(i)
                    pickle.dump(ids, open('ErrorUsers.pickle', 'wb'))
            except Exception as e:
                print('code govno nerabotaet')
                print(e)

    # обработка сообщений
    @bot.message_handler(commands=['start'])
    def welcome(message):
        print('start')
        print(message.chat.id)
        bot.send_message(message.chat.id, 'Привет, ты написал мне /start')

    @bot.message_handler(commands=['help'])
    def help_message(message):
        bot.send_message(message.chat.id,
                         '''Список комманд, доступных тебе:
                         \n/alarm - я хочу получать уведомлений от бота
                         \n/cancel - отписаться от уведомлений''')

    @bot.message_handler(commands=['alarm', 'alarms'])
    def alarm(message):
        print('alarm')

        ids = pickle.load(open('Chat_ids.pickle', 'rb'))
        if message.chat.id not in ids:
            ids.add(message.chat.id)
            pickle.dump(set(ids), open('Chat_ids.pickle', 'wb'))
            bot.send_message(message.chat.id, 'Вы подписались на рассылку')
        else:
            bot.send_message(message.chat.id, 'Вы уже подписаны на рассылку')

    @bot.message_handler(commands=['cancel', 'unalarm'])
    def unalarm(message):
        print('unalarm')
        ids = pickle.load(open('Chat_ids.pickle', 'rb'))
        if message.chat.id not in ids:
            bot.send_message(message.chat.id, 'Вы не подписаны на рассылку')
        else:
            ids.remove(message.chat.id)
            pickle.dump(set(ids), open('Chat_ids.pickle', 'wb'))
            bot.send_message(message.chat.id, 'Вы отписались от рассылки')


    # Бесконечный цикл
    print('bebi')
    schedule.every(3).seconds.do(function_to_run)
    Thread(target=schedule_checker).start()
    bot.infinity_polling()
    print('bot end')
