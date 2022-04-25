from GoogleForm import GoogleFormsApi
import Boolichka

# ТУТА НЕ ПИХАТЬ СООБЩЕНИЯ
# Todo: Как понять, какой ответ куда
# Todo: Экспорт екселевского файла с почтами шоб спамить на них
# Todo: А лучше сделать автоматический спам на эти почты тут же
# Todo: Реализовать для несколько форм

if __name__ == '__main__':
    formId = '1ERaYdaQUDPoS2FqBipDV6oCEN78XA33izlvL252UFjk'
    Forms = GoogleFormsApi()
    Forms.append_form(formId)

    Boolichka.run(Forms)

    # TODO: Цикл телебулички должен быть здесь
