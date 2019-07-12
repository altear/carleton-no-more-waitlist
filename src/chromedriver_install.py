"""

"""
import requests
import logging
import platform
from utils import URL
from io import BytesIO
from zipfile import ZipFile

class UnsupportedPlatformException(Exception):
    pass

CHROME_DRIVER_URL = URL("https://chromedriver.storage.googleapis.com")

def run():
    logging.info("Started install script")
    try:
        logging.info("Searching for latest version of Chrome Driver")
        response = requests.get(CHROME_DRIVER_URL / 'LATEST_RELEASE')
        response.raise_for_status()
        latest_version = response.text
        logging.info(f"Latest version of Chrome Driver found: {latest_version}")

        logging.info("Downloading Chrome Driver")
        driver_url = CHROME_DRIVER_URL / latest_version
        if platform.system() == 'Windows':
            driver_url /= 'chromedriver_win32.zip'
        elif platform.system() == 'Darwin':
            driver_url /= 'chromedriver_mac64.zip'
        elif platform.system() == 'Linux':
            driver_url /= 'chromedriver_linux64.zip'
        else:
            raise UnsupportedPlatformException

        response = requests.get(driver_url)
        response.raise_for_status() 
        logging.info("Download successful")

        logging.info("Unzipping driver")
        zipped_driver = BytesIO(response.content)
        ZipFile(zipped_driver).extractall()
        logging.info("Install script completed successfully")

    except Exception as e:
        logging.critical("Something went wrong.")
        logging.critical(e)
