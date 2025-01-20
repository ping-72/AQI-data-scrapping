import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

# Selenium and WebDriver management
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# 2Captcha library
from twocaptcha import TwoCaptcha

def solve_recaptcha(driver, solver, sitekey, page_url):
    # Use 2Captcha to solve reCAPTCHA
    try:
        result = solver.recaptcha(
            sitekey=sitekey,
            url=page_url
        )
        print("CAPTCHA solved:", result)
        token = result['code']
        # Inject the response token into the page
        # This assumes a reCAPTCHA with a textarea named g-recaptcha-response
        driver.execute_script(
            'document.getElementById("g-recaptcha-response").innerHTML = arguments[0];', token
        )
        # Some pages require dispatching an event after injecting the token
        driver.execute_script(
            'var recaptchaCallback = document.querySelector("[data-callback]");'
            'if(recaptchaCallback) recaptchaCallback.click();'
        )
        return token
    except Exception as e:
        print("Error solving CAPTCHA:", e)
        return None

def scrape_features_with_selenium(state, city, station, start_date, end_date):
    chrome_options = Options()
    # Uncomment for headless mode after debugging:
    # chrome_options.add_argument("--headless")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Initialize 2Captcha solver with your API key
    solver = TwoCaptcha('YOUR_2CAPTCHA_API_KEY')

    try:
        url = "https://airquality.cpcb.gov.in/ccr/#/caaqm-dashboard-all/caaqm-landing"
        driver.get(url)
        print("Opened URL:", url)
        
        # Wait for manual captcha appearance or solve automatically if detected
        wait = WebDriverWait(driver, 60)
        driver.save_screenshot("page_loaded.png")

        # Check for reCAPTCHA presence (common indicator: iframe with title "recaptcha")
        try:
            recaptcha_frame = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//iframe[contains(@title, 'recaptcha')]")
            ))
            print("reCAPTCHA detected.")
            # Switch to main content to solve CAPTCHA
            driver.switch_to.default_content()

            # Extract sitekey from page source or from an element attribute
            # Example: find element with 'data-sitekey' attribute
            captcha_element = driver.find_element(By.CSS_SELECTOR, "[data-sitekey]")
            sitekey = captcha_element.get_attribute("data-sitekey")
            print("Sitekey:", sitekey)

            # Solve the CAPTCHA
            solve_recaptcha(driver, solver, sitekey, url)

            # Wait a bit for the CAPTCHA solution to propagate
            time.sleep(10)
        except Exception as captcha_error:
            print("No reCAPTCHA detected or error occurred:", captcha_error)

        # Continue with your usual scraping steps...
        print("Waiting for State dropdown...")
        state_dropdown = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//input[@placeholder="State Name"]'))
        )
        print("Found State dropdown")
        state_dropdown.click()
        state_option = wait.until(
            EC.element_to_be_clickable((By.XPATH, f'//span[text()="{state}"]'))
        )
        state_option.click()
        print(f"Selected state: {state}")

        # ... Rest of your scraping logic follows ...

        # For brevity, the remainder of your code for interacting with the page and scraping data remains unchanged.
        # ...
        
    except Exception as e:
        print("An error occurred:", e)
        driver.save_screenshot("error.png")
        raise
    finally:
        driver.quit()

if __name__ == "__main__":
    state = "Delhi"
    city = "Delhi"
    station = "R K Puram"
    start_date = datetime(2025, 1, 16, 14, 0)
    end_date = datetime(2025, 1, 16, 15, 0)

    headers, data = scrape_features_with_selenium(state, city, station, start_date, end_date)
    print("Headers:", headers)
    print("Data Rows:")
    for row in data:
        print(row)
