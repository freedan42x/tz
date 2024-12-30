import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests

logging.basicConfig(filename="out.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def get_pfp_url(username):
    url = f'https://www.facebook.com/{username}'
    options = webdriver.ChromeOptions()
    options.add_argument("--headless") # run without opening window
    driver = webdriver.Chrome(options=options)

    try:
        logging.info(f"Opening URL: {url}")
        driver.get(url)

        # wait until a page is fully loaded
        WebDriverWait(driver, 10).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        time.sleep(1)

        close_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Close' and @role='button']"))
        )
        close_button.click()
        logging.info("Closed the initial pop-up")

        time.sleep(1)

        pfp_preview = driver.find_element(By.CSS_SELECTOR, 'svg[data-visualcompletion="ignore-dynamic"][role="img"]')
        driver.execute_script("arguments[0].scrollIntoView(true);", pfp_preview) # so it works with --headless
        pfp_preview.click()
        logging.info("Clicked on profile picture preview")

        time.sleep(1)
        img = driver.find_element(By.CSS_SELECTOR, 'img[data-visualcompletion="media-vc-image"]')
        src = img.get_attribute("src")
        logging.info(f"Profile picture URL found: {src}")

        return src

    except Exception as e:
        logging.error(f"Error while fetching profile picture URL: {e}")

    finally:
        driver.quit()

def download_pfp(username):
    try:
        pfp_url = get_pfp_url(username)
        if not pfp_url:
            logging.error("Failed to get profile picture URL")
            return

        filename = f'{username}_pfp.jpg'
        logging.info(f"Downloading {pfp_url} as {filename}")
        response = requests.get(pfp_url, stream=True, timeout=10)

        if response.status_code == 200:
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            logging.info(f"Profile picture saved as {filename}")
        else:
            logging.error(f"Failed to download profile picture. Status code: {response.status_code}")

    except Exception as e:
        logging.error(f"Error while downloading profile picture: {e}")

if __name__ == '__main__':
    username = 'zuck' # replace with desired facebook username
    logging.info(f"Starting process for username: {username}")
    download_pfp(username)
