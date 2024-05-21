import requests
import os
from dotenv import load_dotenv
import time
import csv

load_dotenv()


class DA:
    params = {
        "weather_params": {
            "key": os.getenv('API_KEY'),
            "q": "Bratislava"
        },
        "country": "sk",
        "year": time.strftime("%Y"),
    }

    @staticmethod
    def handle_request_exceptions(api_method):
        def wrapper():
            try:
                return api_method()
            except requests.exceptions.ConnectionError:
                print("A Connection error occurred")
            except requests.exceptions.HTTPError:
                print("An HTTP error occurred")
            except requests.exceptions.JSONDecodeError:
                print("Response body does not contain valid JSON")
            except requests.RequestException as error:
                print(f"An error occurred {error}")
            return None

        return wrapper

    @staticmethod
    def request_handler(URL, params=None) -> requests:
        response = requests.get(URL, params=params)
        response.raise_for_status()
        return response.json()

    @staticmethod
    @handle_request_exceptions
    def weather_api_call() -> tuple[str, str]:
        WEATHER_URL = os.getenv('WEATHER_URL')
        weather_data = DA.request_handler(WEATHER_URL, params=DA.params["weather_params"])
        icon = "https:" + weather_data["current"]["condition"]["icon"]
        return f"Teplota {DA.params["weather_params"]["q"]} {weather_data['current']['temp_c']:.0f}°C. Rýchlosť vetra {weather_data['current']['wind_kph']} km/h.🌪️", icon

    @staticmethod
    @handle_request_exceptions
    def nameday_api_call() -> str:
        NAMEDAY_URL = os.getenv('NAMEDAY_URL')
        nameday_data = DA.request_handler(NAMEDAY_URL, params=DA.params["country"])
        return f"{nameday_data["nameday"][DA.params["country"]]} 🎉"

    @staticmethod
    @handle_request_exceptions
    def holiday_api_call() -> str:
        HOLIDAY_URL = os.getenv('HOLIDAY_URL').format(YEAR=DA.params["year"], COUNTRY=DA.params["country"])
        holiday_data = DA.request_handler(HOLIDAY_URL)
        date = time.strftime("%Y-%m-%d")
        for response in holiday_data:
            if response["date"] == date:
                return f"{response["localName"]}"
        return ""

    @staticmethod
    def csv_error_handler(read_csv):
        def wrapper():
            try:
                return read_csv()
            except FileNotFoundError:
                print("File not found.")
            except PermissionError:
                print("Permission denied.")
            except IOError:
                print("An error occurred.")
            return None

        return wrapper

    @staticmethod
    def csv_file_reader(csv_file_name, date_match, delimiter=",") -> str:
        matched_value = ""
        with open(csv_file_name, "r", encoding="utf-8") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=delimiter)
            for row in csv_reader:
                if date_match == row[0]:
                    matched_value = row[1]
        return matched_value

    @staticmethod
    @csv_error_handler
    def name_read_csv() -> str:
        date_today = time.strftime("%m-%d")
        name = DA.csv_file_reader("name_day.csv", date_today)
        return name

    @staticmethod
    @csv_error_handler
    def holiday_read_csv() -> str:
        date_today = time.strftime("%m-%d")
        holiday = DA.csv_file_reader("holiday.csv", date_today, delimiter=";")
        return holiday
