import datetime
from apiclient import discovery
from httplib2 import Http
from oauth2client import client, file, tools
import pickle
import json

class GoogleFormsApi:
    def __init__(self):
        self.FormsId = list(pickle.load(open('FormsQuestions.pickle', 'rb')).keys())
        self.isConnected = True
        self.service = self.connector()

    def string_to_time(self, time: str) -> float:
        time = time[:-4]
        return datetime.datetime.strptime(time, "%Y-%m-%dT%H:%M:%S.").timestamp()

    def append_form(self, form_id):
        self.FormsId.append(form_id)
        return 0  # 0 -> все хорошо -1 все плохо. можно как-то использовать)

    def check_actual(self, tmptime: float):
        if tmptime >= (datetime.datetime.now() - datetime.timedelta(days=1)).timestamp():
            return True
        if tmptime < (datetime.datetime.now() - datetime.timedelta(days=1)).timestamp():
            return False
        else:
            raise Exception('check_actual убился во времени')

    def upload(self, local_form_id=0):
        result = self.service.forms().responses().list(formId=self.FormsId[local_form_id]).execute()  # HUETA
        result_relevant = []
        for state in result['responses']:
            if self.check_actual(self.string_to_time(state['createTime'])):
                result_relevant.append(state)
        result_relevant = self.sort_answers_by_time(result_relevant)
        with open('Uploaded.json', 'w') as f:
            json.dump(result_relevant, f)

    def get_responce(self, num=0, way=True):
        """возвращает один ответ из списка форм по счету, сначала или с конца T/F"""
        if way:
            return json.load('Uploaded.json', 'r')[num]
        else:
            return json.load('Uploaded.json', 'r')[::-1][num]

    def get_responce_list(self, local_form_id):
        """возвращает список ответов из списка форм по счету, сначала или с конца T/F"""
        result = self.service.forms().responses().list(formId=self.FormsId[local_form_id]).execute()
        return result

    def connector(self):  # Работает - не трогай
        SCOPES = "https://www.googleapis.com/auth/forms.responses.readonly"
        DISCOVERY_DOC = "https://forms.googleapis.com/$discovery/rest?version=v1"

        store = file.Storage('token.json')
        creds = None
        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets('client_secrets.json', SCOPES)
            creds = tools.run_flow(flow, store)
        service = discovery.build('forms', 'v1', http=creds.authorize(
            Http()), discoveryServiceUrl=DISCOVERY_DOC, static_discovery=False)
        return service

    def new_answers(self, local_form_id=0):
        result = self.service.forms().responses().list(formId=self.FormsId[local_form_id]).execute()
        tmp = 0
        for state in result['responses']:
            if self.check_actual(self.string_to_time(state['createTime'])):
                tmp += 1
        return tmp

    def sort_answers_by_time(self, arr : list) -> []:
        datetime_dict = {}
        for i in arr:
            date = self.string_to_time(i['createTime'])
            datetime_dict[date] = i
        preresult = sorted(datetime_dict)
        result = []
        for i in preresult:
            result.append(datetime_dict[i])
        return result
