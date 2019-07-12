import logging
import os
from ruamel.yaml import YAML
from selenium import webdriver
from pathlib import Path

from src.utils import config_loader, URL

yaml = YAML()

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
    logging.basicConfig(filename='waitlist_checker.log', level=logging.INFO)
    logging.info("Starting Waitlist Checker")

    try:
        driver_path = find_selenium_driver()
        if not driver_path:
            from src import chromedriver_install
            chromedriver_install.run()
            driver_path = find_selenium_driver()

        logging.info("Running scripts")
        with webdriver.Chrome(driver_path) as driver:
            run_scripts(driver)
    except Exception as e:
        logging.critical(e)
        logging.critical("Script stopped due to critical exception.")
        raise(e)

if __name__ == '__main__':
    main()