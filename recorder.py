import pathlib
import threading

import requests
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import os
import subprocess
import time


class ImageCaptureError(Exception):
    pass


def run_shell_script(folder_path):
    script_path = 'make_push_video.sh'
    subprocess.call(['bash', script_path, folder_path])


def record_video(url):
    src_value = ''
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
    driver.get(url)
    src_values = []
    index = 0
    folder_index = 0

    if not os.path.exists('downloaded_images'):
        os.makedirs('downloaded_images')
        print(os.path)

    # Create six folders for storing images
    for i in range(1, 7):
        folder_name = f'folder_{i}'
        folder_path = pathlib.Path('downloaded_images', folder_name)
        os.makedirs(folder_path, exist_ok=True)

    # Initialize variables
    current_folder_index = 1
    start_time = time.time()

    # Define the time intervals for changing folders
    folder_change_interval_minutes = 10
    hourly_reset_interval = 60 * 60  # One hour in seconds

    try:
        img_element = driver.find_element(By.XPATH, '//body//div/img[@class="camera"]')
        src_value = img_element.get_attribute('src')
        src_values.append(src_value)

        while True:
            img_element = driver.find_element(By.XPATH, '//body//div/img[@class="camera"]')
            src_value = img_element.get_attribute('src')

            # Send a GET request to download the image
            response = requests.get(src_value)

            # Check if the request was successful (status code 200)
            if response.status_code == 200:
                index += 1

                # Get the current folder based on the current time
                elapsed_time = time.time() - start_time
                if elapsed_time >= folder_change_interval_minutes * 60:
                    # Create a thread to run the shell script
                    script_thread = threading.Thread(target=run_shell_script,
                                                     args=(f'downloaded_images/folder_{current_folder_index}',))

                    # Start the thread
                    script_thread.start()

                    current_folder_index = (current_folder_index % 6) + 1
                    start_time = time.time()
                    index = 0

                # Define the filename and folder for the downloaded image
                folder_name = f'downloaded_images/folder_{current_folder_index}'
                filename = os.path.join(folder_name, f'image_{index + 1}.jpg')

                # Save the image to the specified filename
                with open(filename, 'wb') as file:
                    file.write(response.content)

                print(f"Downloaded {filename}")
            else:
                print(f"Failed to download {src_value}. Status code: {response.status_code}")

    except Exception as e:
        print(f"Error downloading {src_value}: {str(e)}")
        raise ImageCaptureError(str(e))
    except KeyboardInterrupt:
        driver.quit()
        pass

    # input_pattern = 'path_to_frame_images/image_%d.jpg'
    # output_video = 'output_video.mp4'
    #
    # ffmpeg_command = [
    #     'ffmpeg',
    #     '-framerate', '30',
    #     '-i', input_pattern,
    #     '-c:v', 'libx264',
    #     '-pix_fmt', 'yuv420p',
    #     output_video
    # ]
    #
    # subprocess.run(ffmpeg_command)


def main():
    retry_interval_seconds = 10
    while True:
        try:
            record_video("https://dazzling-smoke-63934.pktriot.net/picture/4/frame")
        except ImageCaptureError as e:
            print(f"Error: {e}")
            if os.path.exists('downloaded_images'):
                all_items = os.listdir('downloaded_images')
                # Filter the items to select only folders (directories)
                folder_names = [item for item in all_items if os.path.isdir(os.path.join('downloaded_images', item))]

                for folder_name in folder_names:
                    all_files = os.listdir(f'downloaded_images/{folder_name}')
                    jpg_files = [file for file in all_files if file.lower().endswith('.jpg')]
                    if len(jpg_files) > 0:
                        # Create a thread to run the shell script
                        script_thread = threading.Thread(target=run_shell_script,
                                                         args=(f'downloaded_images/{folder_name}',))
                        script_thread.start()

            time.sleep(retry_interval_seconds)


if __name__ == "__main__":
    main()
