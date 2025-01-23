from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
import logging

@staticmethod
def is_members_only(driver:WebDriver, video_id:str) -> bool:
  try:
    driver.get(f"https://www.youtube.com/watch?v={video_id}")
    badges = driver.find_elements(By.CSS_SELECTOR, "div.badge-style-type-members-only")
    if len(badges) > 0:
      return True
    return False
  except NoSuchElementException as e:
    logging.error(f"{e} found, URL: {driver.current_url}")
    return False
