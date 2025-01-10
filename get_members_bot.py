from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from selenium.webdriver.common.by import By
import pandas as pd
from selenium.common.exceptions import StaleElementReferenceException
import re


def launch_browser():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get("https://www.facebook.com/")
    return driver


def get_group_elements(driver, group_link):
    all_elements = []

    for suffix in [
        "/members/admins",
        "/members/friends",
        "/members/things_in_common",
        "/members",
    ]:
        full_link = group_link + suffix
        driver.get(full_link)

        # Wait for the page to load
        time.sleep(5)

        # Scroll down to the bottom of the page
        last_height = driver.execute_script("return document.body.scrollHeight")
        scroll_attempts = 0
        max_attempts = 5  # Maximum number of attempts to scroll without new content

        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)  # Wait for the page to load
            new_height = driver.execute_script("return document.body.scrollHeight")

            if new_height == last_height:
                scroll_attempts += 1
                if scroll_attempts >= max_attempts:
                    break
            else:
                scroll_attempts = 0  # Reset the counter if new content is loaded

            last_height = new_height

        time.sleep(5)

        # Find all <a> elements with the specified class
        elements = driver.find_elements(
            By.XPATH,
            '//a[contains(@class, "x1i10hfl xjbqb8w x1ejq31n xd10rxx x1sy0etr x17r0tee x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz x1sur9pj xkrqix3 xzsf02u x1pd3egz")]',
        )
        if elements:
            all_elements.extend(elements)

    return all_elements


def scrape_facebook_groups(email, password, group_links):
    driver = launch_browser()
    driver.maximize_window()
    driver.find_element(By.ID, "email").send_keys(email)
    driver.find_element(By.ID, "pass").send_keys(password)
    driver.find_element(By.NAME, "login").click()
    time.sleep(30)

    all_elements = []
    for group_link in group_links:
        elements = get_group_elements(driver, group_link)
        all_elements.extend(elements)

    # Extract text and href attributes
    data = []
    seen_hrefs = set()
    user_id_pattern = re.compile(r"/user/(\d+)/")

    for element in all_elements:
        try:
            text = element.text
            href = element.get_attribute("href")
            if href not in seen_hrefs:
                seen_hrefs.add(href)
                user_id_match = user_id_pattern.search(href)
                user_id = user_id_match.group(1) if user_id_match else None
                data.append({"Tên": text, "Link": href, "User ID": user_id})
        except StaleElementReferenceException:
            print("Encountered a stale element, skipping it.")
            continue

    # Create a DataFrame and export to Excel
    df = pd.DataFrame(data)
    df.to_excel("output.xlsx", index=False)

    # Close the browser
    driver.quit()


# Example usage
email = "winter28022003@gmail.com"
password = "Cuong123@"
group_links = [
    "https://www.facebook.com/groups/160136771415190"  # 1.6k
]
scrape_facebook_groups(email, password, group_links)
