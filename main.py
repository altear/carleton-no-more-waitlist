import logging
import os
import sys

from selenium import webdriver
from pathlib import Path
from src.utils import config_loader, URL

def run_scripts(driver):
    from src import no_more_waitlist
    s = no_more_waitlist.CheckCourses(driver)
    s.run()

def find_selenium_driver():
    logging.info("Searching for web driver")
    for f in os.listdir():
        if 'chromedriver' in f:
            logging.info(f"Found web driver: {f}")
            return f
    logging.info("Could not find web driver")
    return False

def main():
    config = config_loader('config.yaml')
    
    logging.basicConfig(filename=config.get("logfile"), level=logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logging.getLogger().addHandler(handler)
    logging.info("Starting Waitlist Checker")

    try:
        driver_path = find_selenium_driver()
        if not driver_path:
            from src import chromedriver_install
            chromedriver_install.run()
            driver_path = find_selenium_driver()

        options = webdriver.ChromeOptions()
        if config.get('mode', None).lower() == 'headless':
            logging.info("Launching browser in headless mode")
            options.add_argument('headless')
            options.add_argument('window-size=1200x600') 
        else:
            logging.info("Launching browser")

        with webdriver.Chrome(driver_path, chrome_options=options) as driver:
            logging.info("Running scripts")
            run_scripts(driver)

    except Exception as e:
        logging.critical(e)
        logging.critical("Script stopped due to critical exception.")
        raise(e)

if __name__ == '__main__':
    main()