from selenium import webdriver
from setting import chrome_driver, browser_cache
from _lib import log
from racecards import RaceCards


class Driver:
    def __init__(self) -> None:
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--user-data-dir='+browser_cache)
        self.driver = webdriver.Chrome(
            executable_path=chrome_driver, chrome_options=self.options)

    def __driver__(self):
        return self.driver


if __name__ == '__main__':
    log('initializing...', 'success')
    RaceCards(Driver().__driver__())
    log('hit enter to exit!', 'error')
    input('')
    