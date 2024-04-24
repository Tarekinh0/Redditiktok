
import shutil, errno, os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager




def generate_main_images(title, nb_of_chunks):
    paths = []
    copy_dir('ressources/', 'temp/ressources/')
    for i in range(nb_of_chunks):
        modify_html(title, i+1, nb_of_chunks)
        path = take_screenshot(i+1, nb_of_chunks)
        paths.append(path)

    return paths




def modify_html(title, i, nb_of_chunks):
    file_path = "temp/ressources/reddit.html"

    with open(file_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'lxml')

    # Find the h3 element with id 'modifyTitle'
    title_tag = soup.find('h3', id='modifyTitle')

    # Check if the element was found and modify its content
    if title_tag:
        title_tag.string = title + f"\nPartie {i} sur {nb_of_chunks}"
    else:
        print("Element not found")

    # Write the modified HTML back to the same file
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(str(soup))


def take_screenshot(i, nb_of_chunks):
    img_path = f"temp/part{i}-{nb_of_chunks}.png"
    html_path = "temp/ressources/reddit.html"
    absolute_prefix_html_file = 'file:///' + os.path.abspath(html_path).replace('\\', '/')  # Ensure correct path separator

    # Setup Firefox options
    firefox_options = Options()
    firefox_options.add_argument("--headless")  # Enable headless mode for Firefox

    # Set up Firefox driver
    firefox_service = Service(GeckoDriverManager().install())
    driver = webdriver.Firefox(service=firefox_service, options=firefox_options)

    # Load HTML file
    driver.get(absolute_prefix_html_file)

    # Find the element by ID
    main_element = driver.find_element("id", "main")

    driver.execute_script("""
    arguments[0].style.backgroundColor = 'transparent';  // Change 'transparent' to any color you prefer
    """, main_element)


    # Take screenshot of the specific element
    main_element.screenshot(img_path)

    # Clean up: close the browser window
    driver.quit()

    return img_path


def copy_dir(src, dst):
    try:
        shutil.copytree(src, dst, dirs_exist_ok=True)
    except OSError as exc: # python >2.5
        if exc.errno in (errno.ENOTDIR, errno.EINVAL):
            shutil.copy(src, dst)
        else: raise


# generate_main_images("My(25F) stepbro(21M) is a dick but I love him so so much !", 2)