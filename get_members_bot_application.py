import tkinter as tk
from tkinter import filedialog, messagebox
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException
import pandas as pd
import time
import re
from selenium.webdriver.common.action_chains import ActionChains


def launch_browser():
    driver = webdriver.Chrome()
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
        time.sleep(5)
        
        close_notification = driver.find_element(
            By.XPATH,
            '//div[@class="x1uvtmcs x4k7w5x x1h91t0o x1beo9mf xaigb6o x12ejxvf x3igimt xarpa2k xedcshv x1lytzrv x1t2pt76 x7ja8zs x1n2onr6 x1qrby5j x1jfb8zj"]',
        )
        ActionChains(driver).move_to_element(close_notification).click().perform()
        
        last_height = driver.execute_script("return document.body.scrollHeight")
        scroll_attempts = 0
        max_attempts = 5
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                scroll_attempts += 1
                if scroll_attempts >= max_attempts:
                    break
            else:
                scroll_attempts = 0
            last_height = new_height
        elements = driver.find_elements(
            By.XPATH,
            '//a[@class="x1i10hfl xjbqb8w x1ejq31n xd10rxx x1sy0etr x17r0tee x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz x1sur9pj xkrqix3 xzsf02u x1pd3egz"]'
        )
        if elements:
            all_elements.extend(elements)
    return all_elements


def scrape_facebook_groups(email, password, group_links, output_file):
    driver = launch_browser()
    driver.maximize_window()
    driver.find_element(By.ID, "email").send_keys(email)
    driver.find_element(By.ID, "pass").send_keys(password)
    driver.find_element(By.NAME, "login").click()
    time.sleep(30) # waiting for solve captcha
    all_elements = []
    for group_link in group_links:
        elements = get_group_elements(driver, group_link)
        all_elements.extend(elements)
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
            continue
    df = pd.DataFrame(data)
    df.to_excel(output_file, index=False)
    driver.quit()
    messagebox.showinfo("Thành công", f"Dữ liệu đã được lưu vào {output_file}")


def start_scraping():
    email = email_entry.get()
    password = password_entry.get()
    group_links = group_links_text.get("1.0", tk.END).strip().split("\n")
    output_file = filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        filetypes=[("Excel files", "*.xlsx")],
    )
    if email and password and group_links and output_file:
        scrape_facebook_groups(email, password, group_links, output_file)
    else:
        messagebox.showwarning("Lỗi", "Vui lòng nhập đầy đủ thông tin.")


# Tạo giao diện
root = tk.Tk()
root.title("Get Members Bot")
root.geometry("400x400")

tk.Label(root, text="Email:").pack()
email_entry = tk.Entry(root, width=40)
email_entry.pack()

tk.Label(root, text="Password:").pack()
password_entry = tk.Entry(root, show="*", width=40)
password_entry.pack()

tk.Label(root, text="Danh sách Group Links (mỗi dòng 1 link):").pack()
group_links_text = tk.Text(root, height=10, width=40)
group_links_text.pack()

tk.Button(root, text="Bắt đầu", command=start_scraping).pack()

root.mainloop()
