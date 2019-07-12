from ruamel.yaml import YAML
from pathlib import Path
from selenium.webdriver.common.keys import Keys

yaml = YAML()

class URL(str):
     def __truediv__(self, b):
        return URL('/'.join([self, b]))

def search_for_text(driver, text, element_type=None):
    driver.find_elements_by_css_selector

def config_loader(path):
    return yaml.load(Path(path))

def create_new_tab(driver):
    main_window = driver.current_window_handle
    driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + 't')
    driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + Keys.TAB)
    driver.switch_to_window(main_window)

def close_tab(driver):
    main_window = driver.current_window_handle
    driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + 'w')
    driver.switch_to_window(main_window)