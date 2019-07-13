import logging
import pydash
import bs4
import pandas as pd
from src.utils import URL, config_loader, create_new_tab, close_tab, config_updater
from src.notifications import NotificationHandler
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

MY_CARLETON_URL = URL("https://students.carleton.ca/")

TERM_SEASONS = {
    '10': 'Winter',
    '20': 'Summer',
    '30': 'Fall'
}

class CheckCourses:
    def __init__(self, driver, config):
        self.driver = driver
        self.config = config
        self.notification_handler = NotificationHandler(self.config)
    
    def run(self):
        logging.info("Starting script")
        password = pydash.get(self.config, 'login.password')
        username = pydash.get(self.config, 'login.username')

        logging.info("Logging in to my Carleton")
        self.driver.get(MY_CARLETON_URL)
        WebDriverWait(self.driver, 3).until(
            EC.presence_of_element_located((By.ID , 'user'))
        )
        self.driver.find_element_by_id("user").send_keys(username)
        self.driver.find_element_by_id("pass").send_keys(password)
        self.driver.find_element_by_name("login_btn").click()

        logging.info("Navigating to Carleton Central")
        WebDriverWait(self.driver, 3).until(
            EC.presence_of_element_located((By.XPATH , "//iframe[@src='https://luminis.carleton.ca/centrallogin.html']"))
        )
        iframe = self.driver.find_element_by_xpath("//iframe[@src='https://luminis.carleton.ca/centrallogin.html']")
        self.driver.switch_to.frame(iframe)
        self.driver.find_element_by_css_selector('img[src="carleton-central-new.png"]').click()

        logging.info("Navigating to Course Selection")
        self.driver.switch_to.window(self.driver.window_handles[-1]) # Switch windows
        WebDriverWait(self.driver, 50).until(
            EC.presence_of_element_located((By.XPATH , "//a[contains(text(), 'Add/Drop Classes')]"))
        )
        self.driver.find_element_by_xpath("//a[contains(text(), 'Add/Drop Classes')]").click()
        self.handle_terms()
        
    def handle_terms(self):
        term_select_url = self.driver.current_url
        for term_id in self.config.get('terms'):
            self.handle_term(term_select_url, term_id)

    def handle_term(self, term_select_url, term_id):
        term_id = str(term_id)
        logging.info(f"Selecting term: {TERM_SEASONS[term_id[4:]]} {term_id[:4]}")
        create_new_tab(self.driver)

        self.driver.get(term_select_url)
        WebDriverWait(self.driver, 3).until(
            EC.presence_of_element_located((By.NAME , "term_in"))
        )
        self.driver.find_element_by_name("term_in").click()
        self.driver.find_element_by_xpath(f"//option[@value='{term_id}']").click()
        self.driver.find_element_by_xpath("//input[@type='submit']").click()
        courses = pydash.get(self.config, f'terms.{term_id}')
        
        logging.info(f"Attempting to add courses: {''.join([str(course) for course in courses])}")
        for i in range(len(courses)):
            course = courses[i]
            field_id = f"crn_id{i+1}"
            self.driver.find_element_by_id(field_id).send_keys(course)
        self.driver.find_element_by_xpath("//input[@value='Submit']").click()

        signup_error_df = self.parse_schedule_errors()
        for course in set(courses) - set(signup_error_df.CRN):
            logging.info(f"Successfully Registered: {course}. Removing from config.")
            course_index = courses.index(course)
            courses.pop(course_index)
            config_updater('config.yaml', config)
        for index, course in signup_error_df.iterrows():
            logging.info(f"Failed to Register: {course.Subj}{course.Crse} (CRN: {course.CRN}) - {course.Status}")
        close_tab(self.driver)

        notification_data = {
            'registration_success': pd.Series(list(set(courses) - set(signup_error_df.CRN))).to_frame(),
            'registration_failure': signup_error_df
        }
        self.notification_handler.send_notifications(data=notification_data)

    def parse_schedule_errors(self):
        error_table_index = 8
        soup = bs4.BeautifulSoup(self.driver.page_source, 'html.parser')
        errors = soup.find('table', attrs={'summary': "This layout table is used to present Registration Errors."})
        errors = str(errors)
        df = pd.read_html(self.driver.page_source, header=0)[error_table_index]
        return df