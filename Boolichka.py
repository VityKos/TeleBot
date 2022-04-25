import telebot
import pickle
from threading import Thread
from time import sleep
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
            msg = f'Боже все сюда какой-то чувак заполнил форму и хочет умереть) ' \
                  f'В форме получено ответов [{ans}]\n_________________________\n\n'
            for i in range(ans):
                responce = self.GoogleApi.get_responce(0, i, False)
                info = identify(responce, self.GoogleApi.FormsId[0])
                msg += f'"{info["ФИО"]}" заполнил{"а" if not info["Пол"] else ""} форму на организатора.\n' \
                       f'ВУЗ - {info["ВУЗ"]}\nФакультет - {info["Факультет"]}\nКурс - {info["Курс"]}.\n' \
                       f'ВК - {info["ВК"]}, Почта - {info["Почта"]}\n_________________________\n'
            return msg  # Цикл работает
        else:
            return -1


def identify(responce, form_id=0) -> {str, str, str, bool, str, int, str, str}:
    """ Вставить один респонс человека, которого нужно определить и разобрать
        возвращает то шо нада. [0 ФИО, 1 пол М/Ж T/F, 2 ВУЗ, 3 Факультет 4 КУРС, 5 почту, 6 вк"""

    form_Q = pickle.load(open('FormsQuestions.pickle', 'rb'))[form_id]
    responce = responce['answers']
    person = {}
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
    # , parse_mode= 'Markdown'
    def function_to_run():
        print('function tu run')
        Ids_to_spam = pickle.load(open('Chat_ids.pickle', 'rb'))
        for i in Ids_to_spam:
            try:
                bot.send_message(i, botlogic.spam())

            except Exception as e:
                print('ERROR LOH ALARM')
                print(e)
                # ids = pickle.load(open('Chat_ids.pickle', 'rb'))
                # ids.remove(i)
                # pickle.dump(set(ids), open('Chat_ids.pickle', 'wb'))
                #
                # ids = pickle.load(open('ErrorUsers.pickle', 'rb'))
                # ids.add(i)
                # pickle.dump(ids, open('ErrorUsers.pickle', 'wb'))

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
        ids.remove(message.chat.id)
        pickle.dump(set(ids), open('Chat_ids.pickle', 'wb'))


    # Бесконечный цикл
    print('bebi')
    schedule.every(3).seconds.do(function_to_run)
    Thread(target=schedule_checker).start()
    print('infpol')
    bot.infinity_polling()
    print('bot end')
