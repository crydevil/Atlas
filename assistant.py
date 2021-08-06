from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pyttsx3
import speech_recognition as sr
import datetime
from dateutil import parser
from translate import Translator
import pyautogui
import pytz

# Properties pyttsx3
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

SCOPES = ['https://www.googleapis.com/auth/calendar']
MONTHS = ["января", "февраля", "марта", "апреля", "мая", "июня",
          "июля", "августа", "сентября", "октября", "ноября", "декабря"]
DAYS = ["понедельник", "вторник", "среду", "четверг", "пятницу", "субботу", "воскресенье"]

def speak(audio):
    # uses the pyttsx3 library to convert text to speech
    engine.say(audio)
    engine.runAndWait()

def wishme(*args):
    hour = int(datetime.datetime.now().hour)
    if 5 <= hour < 12:
        speak('Доброе утро сер')
    elif 12 <= hour < 16:
        speak('Добрый день сер')
    elif 16 <= hour <= 22:
        speak('Добрый вечер сер')
    else:
        speak('Доброй ночи сер')

    speak(str(*args))

def takeCommand():
    # Takes microphone input from the user and returns text output
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print('Listening...')
        r.pause_threshold = 1

        audio = r.listen(source=source, timeout=6)

        try:
            print('Recognizing...')
            query = r.recognize_google(audio, language='ru-RU')
            print(f"user said: {query}")
            return query.lower()
        except Exception as e:
            print(e)
            return "None"

def authenticate_google(scopes):
    # If modifying these scopes, delete the file token.pickle.
    SCOPES = scopes

    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    return service

def get_date(text):
    text = text.lower()
    today = datetime.date.today()

    if text.count('сегодня') > 0:
        return today

    if text.count('завтра') > 0:
        return today + datetime.timedelta(1)

    month = -1
    day_of_week = -1
    day = -1
    year = today.year

    # looping over the given phrase
    for word in text.split():

        if word in MONTHS:
            month = MONTHS.index(word) + 1

        if word in DAYS:
            day_of_week = DAYS.index(word)

        if word.isdigit():
            day = int(word)

    if month < today.month and month != -1:
        year = year + 1

    if month == -1 and day != -1:
        if day < today.day:
            month = today.month + 1
        else:
            month = today.month

    if day_of_week != -1 and month == -1 and day == -1:
        current_day_of_week = today.weekday()
        diff = day_of_week - current_day_of_week

        if diff < 0:
            diff += 7
            if text.count('следующий') >= 1 or text.count("следующую") >= 1:
                diff += 7

        return today + datetime.timedelta(diff)

    if day != -1:
        return datetime.date(month=month, day=day, year=year)

def get_events(day, service):
    # Call the Calendar API
    date = datetime.datetime.combine(day, datetime.datetime.min.time())
    end_date = datetime.datetime.combine(day, datetime.datetime.max.time())
    utc = pytz.UTC
    date = date.astimezone(utc)
    end_date = end_date.astimezone(utc)

    events_result = service.events().list(calendarId='primary', timeMin=date.isoformat(), timeMax=end_date.isoformat(),
                                          singleEvents=True, orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        speak('Никаких мероприятий не найдено.')
        return
    elif len(events) == 1:
        speak(f"У вас одно мероприятие на этот день.")
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])
            start_time = str(start.split("T")[1].split("+")[0])
            speak(event["summary"] + " в " + start_time)
    elif len(events) >= 2 and len(events) <= 4:
        speak(f"У вас {len(events)} мероприятия на этот день.")
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])
            start_time = str(start.split("T")[1].split("+")[0])
            speak(event["summary"] + " в " + start_time)
    else:
        speak(f"У вас {len(events)} мероприятий на этот день.")
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])
            start_time = str(start.split("T")[1].split("+")[0])
            speak(event["summary"] + " в " + start_time)

def create_events(start, end, name, content, service):
    EVENT = {'summary': name,
             'description': content,
             'start': {'dateTime': start},
             'end': {'dateTime': end}}
    service = service
    default_event = service.events().insert(calendarId='primary',
                                 sendNotifications=True,
                                 body=EVENT).execute()
    print(default_event)

def create_birthday(start, end, name, service):
    EVENT = {'summary': name,
             'start': {'dateTime': start,
                       'timeZone': 'Etc/GMT+3'},
             'end': {'dateTime': end,
                     'timeZone': 'Etc/GMT+3'},
             'recurrence': ["RRULE:FREQ=YEARLY;UNTIL=20991231T235959Z"],
             'reminders': {
                 'useDefault': False,
                 'overrides': [
                     # 10080 minutes = 7 days
                     {'method': 'popup', 'minutes': 10080},
                     {'method': 'popup', 'minutes': 1440}
                 ]}
             }
    service = service
    birthday_event = service.events().insert(calendarId='primary',
                                 sendNotifications=True,
                                 body=EVENT).execute()
    print(birthday_event)

def run():
    services = authenticate_google(SCOPES)
    say = 'Как я могу вам помочь?'
    wishme(say)
    i = 0
    print(services)

    while i == 0:
        text = takeCommand()
        print(text)

        if text.count("выйди") > 0:
            break
        elif text.count("какое") > 0 or text.count("какие") > 0 or text.count("запланировано") > 0:
            day = get_date(text)
            if day:
                print(get_events(day, services))
                i += 1
            else:
                speak('Не удалось получить события, возможно вы не указали день')
                return
        elif text.count("запиши") > 0 or text.count("добавь") > 0 or text.count("создай") > 0:
            today = datetime.date.today()
            GMT_OFF = '03:00'
            if text.count("день рождение") > 0 or text.count("день рождения") > 0:
                speak('На какое число?')
                str_date = takeCommand()
                translator = Translator(from_lang="Russian", to_lang="English")
                translation = translator.translate(str_date)
                date = parser.parse(translation)
                date_new = datetime.datetime.strftime(date, "%m-%d")

                speak('Когда начинается мероприятие?')
                str_time = takeCommand()
                if str_time.find(':') == -1:
                    str_new = f'{str_time[:2]}:{str_time[:-2]}'
                else:
                    str_new = str_time
                start_pars = parser.parse(str_new)
                start_new = datetime.datetime.strftime(start_pars, "%H:%M")
                start_str = f"{today.year}-{date_new}T{start_new}:00+{GMT_OFF}"

                speak('Когда заканчивается мероприятие?')
                end_time = takeCommand()
                if end_time.find(':') == -1:
                    end_new = f'{end_time[:2]}:{end_time[:-2]}'
                else:
                    end_new = end_time
                end_pars = parser.parse(end_new)
                end_new = datetime.datetime.strftime(end_pars, "%H:%M")
                end_str = f"{today.year}-{date_new}T{end_new}:00+{GMT_OFF}"

                speak('Как зовут именинника?')
                text = takeCommand()
                print(text)
                la_le = text[-1]
                text_name = ''
                if la_le == 'б' or la_le == 'в' or la_le == 'г' or la_le == 'д' or la_le == 'ж' or la_le == 'з':
                    text_name = text + 'а'
                elif la_le == 'к' or la_le == 'л' or la_le == 'м' or la_le == 'н' or la_le == 'п' or la_le == 'р':
                    text_name = text + 'а'
                elif la_le == 'с' or la_le == 'т' or la_le == 'ф' or la_le == 'х' or la_le == 'ц' or la_le == 'ш':
                    text_name = text + 'а'
                elif la_le == 'а':
                    text_name = text[:-1] + 'ы'
                elif la_le == 'й' or la_le == 'ь':
                    text_name = text[:-1] + 'я'
                elif la_le == 'я':
                    text_name = text[:-1] + 'и'
                elif la_le == 'е' or la_le == 'и' or la_le == 'о' or la_le == 'у' or la_le == 'э':
                    text_name = text
                else:
                    text_name = text
                name = "День рождение " + text_name.title()
                create_birthday(start_str, end_str, name, services)
                speak(name + "записан")
                return
            else:
                speak('На какое число?')
                str_date = takeCommand()
                translator = Translator(from_lang="Russian", to_lang="English")
                translation = translator.translate(str_date)
                date = parser.parse(translation)
                date_new = datetime.datetime.strftime(date, "%m-%d")

                speak('Когда начинается мероприятие?')
                str_time = takeCommand()
                if str_time.find(':') == -1:
                    str_new = f'{str_time[:2]}:{str_time[:-2]}'
                else:
                    str_new = str_time
                start_pars = parser.parse(str_new)
                start_new = datetime.datetime.strftime(start_pars, "%H:%M")
                start_str = f"{today.year}-{date_new}T{start_new}:00+{GMT_OFF}"

                speak('Когда заканчивается мероприятие?')
                end_time = takeCommand()
                if end_time.find(':') == -1:
                    end_new = f'{end_time[:2]}:{end_time[:-2]}'
                else:
                    end_new = end_time
                end_pars = parser.parse(end_new)
                end_new = datetime.datetime.strftime(end_pars, "%H:%M")
                end_str = f"{today.year}-{date_new}T{end_new}:00+{GMT_OFF}"

                speak('Как желаете назвать мероприятие?')
                text = takeCommand()
                print(text)
                name = text
                speak('Скажите описание события')
                text = takeCommand()
                print(text)
                content = text
                create_events(start_str, end_str, name, content, services)
                speak("Событие " + name + "записано")
                return
        else:
            speak('Команда не распознана, попробуйте еще раз')
            return