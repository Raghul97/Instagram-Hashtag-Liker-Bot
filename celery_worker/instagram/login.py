from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from .utils import delay
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class InstaLogin:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.insta_login_url = "https://instagram.com/accounts/login"
        i = 0
        while i < 3:
            try:
                self.driver = webdriver.Remote('http://selenium:4444/wd/hub', desired_capabilities=DesiredCapabilities.CHROME)
                break
            except:
                i += 1
                delay(2)
        self.login()
        self.verify_login()

    def terminate_bot(self):
        """
            terminate the driver, once job is completed.
        """
        self.driver.close()

    def naviagte_to_insta(self):
        """
            navigate to instagram login page.
        """
        self.driver.get(self.insta_login_url)
        delay(5)

    def enter_credentials(self):
        """
            enter the credentials in instagram login page.
        """
        self.driver.find_element_by_name('username').send_keys(self.username)
        self.driver.find_element_by_name('password').send_keys(self.password + Keys.RETURN)
        delay(5)

    def verify_login(self):
        """
            check whether login is successfull, if not terminate and boot it up.
        """
        if not self.driver.title == 'Instagram':
            self.terminate_bot()
            self.driver = webdriver.Remote('http://selenium:4444/wd/hub', desired_capabilities=DesiredCapabilities.CHROME)
            self.login()

    def login(self):
        """
            steps to login into instagram with user credentials.
        """
        self.naviagte_to_insta()
        self.enter_credentials()
        delay(5)
        