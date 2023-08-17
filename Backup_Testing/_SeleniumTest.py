# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.action_chains import ActionChains
# import time

# # Replace this with the path to your geckodriver executable
# firefox_driver_path = '/home/noaa_gms/Downloads/geckodriver'

# # Set Firefox options with the executable path
# options = webdriver.Firefox
# # options.binary_location = '/usr/bin/firefox'  
# # options.add_argument(firefox_driver_path)

# # Create a new instance of the Firefox browser with the options
# driver = webdriver.Firefox(options=options)
# time.sleep(2)

# try:
#     driver.get("http://192.168.4.1/")
#     driver.set_window_size(1888, 1040)

#     # Click on the first element with class "bx" inside an element with class "navnarrow"
#     driver.find_element(By.CSS_SELECTOR, ".navnarrow .bx:nth-child(1)").click()

#     element = driver.find_element(By.ID, "blackimg")
#     actions = ActionChains(driver)
#     actions.move_to_element(element).perform()

#     element = driver.find_element(By.CSS_SELECTOR, "body")
#     actions = ActionChains(driver)
#     actions.move_to_element(element, 0, 0).perform()

#     # Locate the element with ID "az" and type "23" into it
#     driver.find_element(By.ID, "az").send_keys("23")

#     # Click on the element with ID "btnSetAnt"
#     driver.find_element(By.ID, "btnSetAnt").click()
# except Exception as e:
#     print(f"Error: {e}")
# finally:
#     # Close the browser window
#     driver.quit()


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

# Replace this with the path to your geckodriver executable
firefox_driver_path = '/usr/bin/geckodriver'

# Create the Firefox WebDriver using the executable_path directly
driver = webdriver.Firefox(executable_path=firefox_driver_path)

try:
    driver.get("http://192.168.4.1/")
    driver.set_window_size(1888, 1040)

    # Click on the first element with class "bx" inside an element with class "navnarrow"
    driver.find_element(By.CSS_SELECTOR, ".navnarrow .bx:nth-child(1)").click()

    # Rest of your interactions...

except Exception as e:
    print(f"Error: {e}")
finally:
    # Close the browser window
    driver.quit()


