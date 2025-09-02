from lxml import etree
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import unquote_plus


session = requests.Session()
retry = Retry(connect=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)

url = ""
file_extension = ""
xpath = ""


def decode_url(encoded_url):
    decoded_url = unquote_plus(encoded_url)
    return decoded_url


def download_and_save_with_stream(url:str):
    with session.get(url, stream=True) as response:
        filename = url.split("/")[-1].replace(" ","_").replace("-","_")
        with open(filename, 'wb') as file:
            for chunk in response.iter_content(1000*1024):
                file.write(chunk)

    print(f"Downloaded and saved: {filename}")



def process_download(url:str, xpath_article:str):
    try:
        # url = "http://blog.apify.com/python-lxml-tutorial/"
        # resp = session.get("https://server4.ftpbd.net/FTP-4/English-Foreign-TV-Series/Butterfly-2015/Season-1/")
        # resp = session.get("http://172.16.50.14/DHAKA-FLIX-14/KOREAN%20TV%20%26%20WEB%20Series/Return%20to%20the%20Palace"
        #                    "%20%28The%20Haunted%20Palace%29%20%28TV%20Series%202025%E2%80%93%20%29%20720p/Season%201%20"
        #                    "%28Korean%20Language%29/")
        # xpath_article = "//img[@class='kg-image']/@src"
        # xpath_article = "//a[contains(@href,'jpg')]/@href"
        # xpath_article = "//img[contains(@src,'jpg')]/@src"
        # xpath_article = "//img[contains(@class,'kg-image')]/@src"
        # xpath_article = "//img[contains(@class,'kg-image')]/@src"

        print(f"url: {url}")
        print(f"Xpath: {xpath_article}")

        resp = session.get(url)
        tree = etree.HTML(resp.text)
        elements = []

        for element in tree.xpath(xpath_article):
            # print(f"element: {element}")
            elements.append(f"{element}")

        for link in elements:
            print(f"downloadable link: {link}")


        # details: below code will download files one by one (sequentially)
        # for element in elements:
        #     download_and_save_with_stream(element)

        # details: below code will use multithreading to download files concurrently
        with ThreadPoolExecutor(3) as executor:
            executor.map(download_and_save_with_stream, elements)

    except requests.exceptions.ConnectionError as r:
        r.status_code = "Connection refused"
        print("Connection refused.",r)
    except Exception as e:
        print("Something went wrong.",e)


def initiate_inputs():
    global url , file_extension, xpath
    url = input("Enter the URL: ").strip()
    file_extension = input("Enter the file extension (e.g., mkv, mp4, zip, jpg): ").strip()
    xpath = input("Enter the XPath (optional, press Enter for 'default'): ").strip()
    return url, file_extension, xpath


if __name__ == '__main__':
    url, file_extension, xpath = initiate_inputs()
    if not xpath:
        xpath = f"//a[contains(@href,'{file_extension}')]/@href"
    process_download(url, xpath)




