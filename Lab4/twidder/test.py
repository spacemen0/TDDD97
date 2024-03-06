from time import sleep
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions

# this file contains the selenium tests


class TwidderTest(unittest.TestCase):

    # set up test, open the remote webpage and find the p element in our message box
    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.get("http://twidder4dorks.azurewebsites.net/")
        self.messageText = self.driver.find_element(By.CSS_SELECTOR, "#message-text")

    # test register functionality
    def test_register(self):
        driver = self.driver
        # find all the input field for registering
        firstName = driver.find_element(By.CSS_SELECTOR, "#first-name")
        firstName.send_keys("Test Name")
        familyName = driver.find_element(By.CSS_SELECTOR, "#family-name")
        familyName.send_keys("Family Name")
        city = driver.find_element(By.CSS_SELECTOR, "#city")
        city.send_keys("Unknown")
        country = driver.find_element(By.CSS_SELECTOR, "#country")
        country.send_keys("Unknown")
        email = driver.find_element(By.CSS_SELECTOR, "#email")
        email.send_keys("test3@email.com")
        password = driver.find_element(By.CSS_SELECTOR, "#password")
        password.send_keys("mytestpassword")
        re_password = driver.find_element(By.CSS_SELECTOR, "#repeat-psw")
        re_password.send_keys("mytestpassword")
        sign_up = driver.find_element(By.CSS_SELECTOR, "#register-form")
        sleep(2)
        # submit teh register form
        sign_up.submit()
        # when the message text shows up (which means response from server has been received) continue test otherwise print error message
        try:
            WebDriverWait(driver, 10).until(
                expected_conditions.visibility_of(self.messageText)
            )
        except:
            print("Failed to find")
        # asset if the message is what we want
        self.assertEqual(
            self.messageText.get_attribute("innerHTML"), "Sign up successfully"
        )
        sleep(2)

    def test_login(self):
        driver = self.driver
        email = driver.find_element(By.CSS_SELECTOR, "#email-login")
        email.send_keys("test@email.com")
        password = driver.find_element(By.CSS_SELECTOR, "#password-login")
        password.send_keys("mynewtestpassword")
        sleep(2)
        # same logic from above, calling submit on any elements inside a form will submit the form thus we can call directly on email element
        email.submit()
        try:
            WebDriverWait(driver, 10).until(
                expected_conditions.visibility_of(self.messageText)
            )
        except:
            print("Failed to find")
        self.assertEqual(
            self.messageText.get_attribute("innerHTML"), "Log in successfully"
        )
        sleep(2)

    def test_post_message(self):
        self.test_login()
        driver = self.driver
        input = driver.find_element(By.ID, "post-message")
        input.send_keys("message from selenium test")
        post = driver.find_element(By.CSS_SELECTOR, "#user-wrapper > button")
        sleep(2)
        post.click()
        wall = driver.find_element(By.ID, "wall")
        # same logic from above, this time using assertIn to assert if the message we posted is in the message wall
        self.assertIn("message from selenium test", wall.get_attribute("innerHTML"))
        sleep(2)

    def test_sign_out(self):
        self.test_login()
        driver = self.driver
        account = driver.find_element(
            By.CSS_SELECTOR, "#right-container > nav > button:nth-child(3)"
        )
        # click account button to redirect to account tab then same logic
        account.click()
        signOut = driver.find_element(By.CSS_SELECTOR, "#signOutButton")
        sleep(2)
        signOut.click()
        try:
            WebDriverWait(driver, 10).until(
                expected_conditions.visibility_of(self.messageText)
            )
        except:
            print("Failed to find")
        self.assertEqual(
            self.messageText.get_attribute("innerHTML"), "Signed out successfully"
        )
        sleep(2)

    # first redirect to account tab then fill in all the field to change password , at last assert if the message is "Password changed successfully"
    def test_change_password(self):
        self.test_login()
        driver = self.driver
        account = driver.find_element(
            By.CSS_SELECTOR, "#right-container > nav > button:nth-child(3)"
        )
        account.click()
        oldPsw = driver.find_element(By.CSS_SELECTOR, "#oldPassword")
        newPsw = driver.find_element(By.CSS_SELECTOR, "#password")
        repeatPsw = driver.find_element(By.CSS_SELECTOR, "#repeat-psw")
        confirm = driver.find_element(
            By.CSS_SELECTOR, "#account-form > input[type=submit]"
        )
        oldPsw.send_keys("mynewtestpassword")
        newPsw.send_keys("mynewtestpassword")
        repeatPsw.send_keys("mynewtestpassword")
        sleep(2)
        confirm.click()
        try:
            WebDriverWait(driver, 10).until(
                expected_conditions.visibility_of(self.messageText)
            )
        except:
            print("Failed to find")
        self.assertEqual(
            self.messageText.get_attribute("innerHTML"), "Password changed successfully"
        )
        sleep(2)

    # will run when all test cases finished
    def tearDown(self):
        self.driver.close()


if __name__ == "__main__":
    unittest.main()
