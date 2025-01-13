from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
import time
from datetime import datetime
import logging
import os
import schedule

logging.basicConfig(
    filename='auto_absen.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def auto_absen(npm, password):
    driver = None
    try:
        logging.info("Starting auto attendance process")
        
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')
        
        logging.info("Setting up Chrome driver")
        try:
            driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=options
            )
            logging.info("Chrome driver initialized successfully")
        except Exception as e:
            logging.error(f"Error installing/starting Chrome driver: {e}")
            return

        driver.set_page_load_timeout(30)
        
        logging.info("Navigating to attendance URL")
        driver.get("https://akademik.unbin.ac.id/absensi/")
        
        npm_field = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, "userid"))
        )
        npm_field.clear()
        npm_field.send_keys(npm)
        logging.info("NPM entered successfully")
            
        try:
            password_field = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.ID, "pin"))
            )
            password_field.clear()
            password_field.send_keys(password)
            logging.info("Password entered successfully")
        except Exception as e:
            logging.error(f"Error finding/filling password field: {e}")
            raise

        try:
            submit_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit'][name='login'][value='Login']"))
            )
            driver.execute_script("arguments[0].click();", submit_button)
            logging.info("Submit button clicked")
        except Exception as e:
            logging.error(f"Error clicking submit button: {e}")
            raise
        
        time.sleep(8)
        
        success_msg = f"Attendance submitted successfully at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}!"
        print(success_msg)
        logging.info(success_msg)
        
    except Exception as e:
        error_msg = f"Error detail: {type(e).__name__}: {str(e)}"
        print(error_msg)
        logging.error(error_msg)
        
    finally:
        if driver:
            try:
                driver.quit()
                logging.info("Browser session closed")
            except Exception as e:
                logging.error(f"Error closing driver: {e}")

def schedule_attendance(npm, password):
    schedule.every().monday.at("09:00").do(auto_absen, npm=npm, password=password)
    
    schedule.every().wednesday.at("14:00").do(auto_absen, npm=npm, password=password)
    
    
    schedule.every().thursday.at("10:00").do(auto_absen, npm=npm, password=password)
    
    schedule.every().friday.at("09:00").do(auto_absen, npm=npm, password=password)
    schedule.every().friday.at("13:30").do(auto_absen, npm=npm, password=password)
    
    schedule.every().saturday.at("09:50").do(auto_absen, npm=npm, password=password)
    schedule.every().saturday.at("13:00").do(auto_absen, npm=npm, password=password)

if __name__ == "__main__":
    users = [
        {"npm": "12524020", "password": "12524020"}, #daud
        {"npm": "12524008", "password": "070704"},
        {"npm": "12524011", "password": "12524011"}
    ]
    for user in users:
        npm = user["npm"]
        password = user["password"]
    
    print("Menjadwalkan absensi otomatis...")
    schedule_attendance(npm, password)
    
    print("Absensi telah dijadwalkan. Program akan berjalan sesuai jadwal.")
    logging.info("Auto attendance scheduler started")
    
    while True:
        schedule.run_pending()
        time.sleep(1)
