import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
import time
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service


def send_messages(email, password, excel_file, message):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get("https://www.facebook.com/")
    
    driver.maximize_window()
    driver.find_element(By.ID, "email").send_keys(email)
    driver.find_element(By.ID, "pass").send_keys(password)
    driver.find_element(By.NAME, "login").click()
    time.sleep(30)
    
    # Load the data from the Excel file
    df = pd.read_excel(excel_file)

    # Iterate over each user ID in the DataFrame
    for index, row in df.iterrows():
        user_id = row["User ID"]
        user_link = f"https://www.facebook.com/{user_id}/?locale=vi_VN"

        # Navigate to the user's profile
        driver.get(user_link)
        time.sleep(3)  # Wait for the page to load

        try:
            # Click on the div with aria-label="Message"
            message_button = driver.find_element(
                By.XPATH,
                '//div[@aria-label="Nhắn tin"]',
            )
            ActionChains(driver).move_to_element(message_button).click().perform()
            time.sleep(2)  # Wait for the message dialog to open

            # Find the div with aria-label="Nhắn tin" and send the message
            message_input = driver.find_element(
                By.XPATH, '//p[@class="xat24cr xdj266r"]'
            )
            message_input.send_keys(message)
            time.sleep(2)  # Wait for the message to be typed
            # Click on the div with aria-label="Nhấn Enter để gửi"
            send_button = driver.find_element(
                By.XPATH,
                '//div[@aria-label="Nhấn Enter để gửi"]',
            )
            ActionChains(driver).move_to_element(send_button).click().perform()
            time.sleep(2)  # Wait for the message to be sent

        except NoSuchElementException:
            print(f"Could not find the required elements for user {user_id}, skipping.")
            continue

    # Close the browser
    driver.quit()


# Example usage
send_messages("winter28022003@gmail.com", "Cuong123@" , "output.xlsx", "hello")
