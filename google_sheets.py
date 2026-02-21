import os
import gspread
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

# Путь к файлу с ключами (тот самый, который мы скачали)
CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__), 'google-credentials.json')

# ID вашей таблицы (вставьте свой из Шага 1.5)
SPREADSHEET_ID = '1ABCxyz123456789'  # ЗАМЕНИТЕ НА СВОЙ!

class GoogleSheetsClient:
    def __init__(self):
        self.client = None
        self.connect()
    
    def connect(self):
        """Подключение к Google Sheets"""
        try:
            # Проверяем, есть ли файл с ключами
            if not os.path.exists(CREDENTIALS_FILE):
                print(f"❌ Файл {CREDENTIALS_FILE} не найден!")
                return
            
            # Настраиваем доступ
            scope = ['https://spreadsheets.google.com/feeds', 
                    'https://www.googleapis.com/auth/drive']
            credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
            self.client = gspread.authorize(credentials)
            print("✅ Подключение к Google Sheets установлено!")
        except Exception as e:
            print(f"❌ Ошибка: {e}")
    
    def add_help_request(self, name, phone, category, details, username=""):
        """Добавление заявки в лист 'Помощь'"""
        try:
            if not self.client:
                print("❌ Нет подключения к Google Sheets")
                return False
            
            # Открываем таблицу и лист
            sheet = self.client.open_by_key(SPREADSHEET_ID)
            worksheet = sheet.worksheet("Помощь")
            
            # Формируем строку для добавления
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            row = [timestamp, name, username, phone, category, details, "", "Новая"]
            
            # Добавляем строку в конец таблицы
            worksheet.append_row(row)
            print(f"✅ Заявка добавлена в Google Sheets!")
            return True
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return False
    
    def add_request(self, name, phone, category, details, username=""):
        """Добавление запроса в лист 'Запросы'"""
        try:
            if not self.client:
                print("❌ Нет подключения к Google Sheets")
                return False
            
            sheet = self.client.open_by_key(SPREADSHEET_ID)
            worksheet = sheet.worksheet("Запросы")
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            row = [timestamp, name, username, phone, category, details, "Новый"]
            
            worksheet.append_row(row)
            print(f"✅ Запрос добавлен в Google Sheets!")
            return True
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return False

# Создаем объект для работы с таблицами
sheets_client = GoogleSheetsClient()