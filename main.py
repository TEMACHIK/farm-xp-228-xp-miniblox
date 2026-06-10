import os
import time
import random
import threading
import requests
from flask import Flask
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)

# ==================== НАСТРОЙКИ БОТА ====================
# Твоя ссылка, которую можно легко менять здесь:
TARGET_URL = "https://miniblox.io/?join=IYJEFO"

# Безопасное получение токена из настроек хостинга. 
# Если на хостинге переменная не задана, возьмется значение по умолчанию (для теста локально)
SESSION_TOKEN = os.environ.get('MY_SECRET_TOKEN', '46311300124c527869f156691a2c0c9b')
# ========================================================

RENDER_EXTERNAL_URL = os.environ.get('RENDER_EXTERNAL_URL', 'http://localhost:5000')

def anti_sleep():
    """Функция против засыпания Render"""
    while True:
        time.sleep(600)
        try:
            requests.get(RENDER_EXTERNAL_URL)
        except Exception as e:
            print(f"Ошибка пинга: {e}")

def bot_loop():
    """Основная логика авторизации и движения"""
    print("Запуск браузера Chrome...")
    
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Без графического окна для хостинга
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        # 1. Заходим сначала на главный домен, чтобы инициализировать localStorage для этого сайта
        print("Шаг 1: Заходим на главную страницу для установки сессии...")
        driver.get("https://miniblox.io/")
        time.sleep(5)
        
        # 2. Выполняем JS-команду (замена ввода в консоль DevTools)
        print("Шаг 2: Записываем токен сессии в localStorage...")
        js_script = f'localStorage.session_v1 = "{SESSION_TOKEN}";'
        driver.execute_script(js_script)
        time.sleep(2)
        
        # 3. Переходим по твоей целевой ссылке (это заменяет обычную перезагрузку)
        print(f"Шаг 3: Переходим по ссылке: {TARGET_URL}")
        driver.get(TARGET_URL)
        time.sleep(8) # Даем игре полностью загрузиться после входа в сессию
        
        print("Шаг 4: Бот успешно зашел. Начинаю прожимать WASD + Space.")
        keys = ['w', 's', 'd', 'a', 'space']

        while True:
            # Находим body страницы, чтобы отправлять нажатия клавиш в игру
            body = driver.find_element(By.TAG_NAME, 'body')
            
            for key in keys:
                if key == 'space':
                    print("Действие: Прыжок (Space)")
                    body.send_keys(Keys.SPACE)
                else:
                    print(f"Действие: Нажатие {key.upper()}")
                    body.send_keys(key)
                
                # Небольшая задержка между действиями (от 0.5 до 1.5 секунд)
                time.sleep(random.uniform(0.5, 1.5))
                
            # Небольшой отдых после полного круга WASD+Space
            time.sleep(2)
            
    except Exception as e:
        print(f"Произошла ошибка в игре: {e}")
    finally:
        driver.quit()
        print("Перезапуск бота через 15 секунд...")
        time.sleep(15)
        bot_loop()

@app.route('/')
def home():
    return "Миниблокс бот активен и работает!"

if __name__ == "__main__":
    threading.Thread(target=anti_sleep, daemon=True).start()
    threading.Thread(target=bot_loop, daemon=True).start()
    
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
