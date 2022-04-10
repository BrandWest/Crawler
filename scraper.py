#WebScraper with Selenium

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException


import pickle
import time, os, sys, getopt, csv, re
import pandas as pd


def download(url, directory, driver):
	actions = ActionChains(driver)

	stack = []
	files_readable = []
	driver.get(url)
	time.sleep(10)
	url = url + 'post/USLfL9XIAOk9xnX562344fec4aac8'
	time.sleep(10)

	driver.get(url)
	with open (directory + "fileStructure.csv", "w") as file:
		writer = csv.writer(file)
		while(True):
			element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME,"file-listing__item")))
			# time.sleep(5)
			# print(element)
			# # print(driver)
			# print(element.text)
			file = driver.find_element(By.CLASS_NAME, "file-listing__item").text.split('\n')
			files_readable.append(file[0]) #Root
			stack.append(driver.find_element(By.CLASS_NAME, "file-listing__item")) #Root
			writer.writerow([str(file[0])])
			actions.move_to_element(element).double_click().perform()
			print("download loop")
			driver, cookies, writer, stack, files_readable = getFileStructure(element, driver, writer, stack, files_readable)
			exit(1)
def getFileStructure(element, driver, writer, stack, files_readable):
	actions = ActionChains(driver)
	#get cookies
	pickle.dump(driver.get_cookies(), open("cookies.pkl","wb"))

	time.sleep(2)
	try:
		#wait for populate
		element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "file-listing__item")))
	finally:
		#get all folders/files
		elements = driver.find_elements(By.CLASS_NAME,"file-listing__item")
		#apply each file to stack
		for i in elements:
			# print("element:", i.text)
			file = i.text.split('\n')
			files_readable.append(file[0])
			stack.append(i)
			writer.writerow([str(file[0])])

		# print('-------------------------------------------')
		# print("The Stack: ", stack, files_readable)
		print('-------------------------------------------')
		print("The readable: ", files_readable)
		print('-------------------------------------------')
		cookies = pickle.load(open("cookies.pkl", "rb"))
		# print(cookies)
		for cookie in cookies:
			driver.add_cookie(cookie)
		
	#check to see if paging is required
	try:
		# driver.find_element(By.CLASS_NAME,"file-listing__pagination")
		# element = driver.find_element(By.CLASS_NAME,"on-end")
		element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "on-end")))
		# print(element.text)
		print("Try to click on-end")
		if element.text == "disabled":
			print("Disabled", element.text)
			for first_out in files_readable[::-1]:
				first_out_element = stack.pop()
				if re.search(r'\.*', first_out):
					value = files_readable.pop()
					writer.writerow([str(value)])
				else:
					#Go into the folder.
					# element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "file-listing__item")))
					actions.move_to_element(first_out_element).click().perform()
					getFileList(element, driver, writer, stack, files_readable)

			for i in elements[::-1]:
				# print("element i: ", i)
				actions.move_to_element(element).double_click().perform()
				driver, cookies, writer, stack, files_readable = getFileList(element, driver, cookies, writer, stack, files_readable)

				stack.pop()
		else:
			print("enabled click", element.text)
			actions.move_to_element(element).click().perform()
	except TimeoutException as e:
		element = -1
		print("TimeoutException",element.text)
	except WebDriverException:
		element = -1
		print("No futher pages",element.text)
	finally:
		if len(stack) == 0:
			return driver, cookies, writer, stack, files_readable
		else:
			getFileStructure(element, driver, writer, stack, files_readable)

def getFileList(element, driver, cookies, writer, stack, files_readable):
	print('-------------------------------------------')
	print("Get File List")
	actions = ActionChains(driver)

	try:
		# driver.find_element(By.CLASS_NAME,"file-listing__pagination")
		# element = driver.find_element(By.CLASS_NAME,"on-end")
		print("")
		element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "back-one-page")))
		actions.move_to_element(element).click().perform()
	except TimeoutException as e:
		element = -1
		print("TimeoutException: ",element.text)
	except WebDriverException:
		element = -1
		print("No Clicks: ",element)
		return driver, cookies, writer, stack, files_readable
	
	if element == -1: #No next page
		elements = driver.find_elements(By.CLASS_NAME, "file-listing__name")
		for first_out in files_readable[::-1]:
			first_out_element = stack.pop()
			if re.search(r'\.*', first_out):
				value = files_readable.pop()
				writer.writerow([str(value)])
			else:
				#Go into the folder.
				# element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "file-listing__item")))
				actions.move_to_element(first_out_element).click().perform()
				getFileStructure(element, driver, writer, stack, files_readable)

		for i in elements[::-1]:
			print(i)
			actions.move_to_element(element).double_click().perform()
			driver, cookies, writer, stack, files_readable = getFileList(element, driver, cookies, writer, stack, files_readable)

			stack.pop()
	else:
		try:
			actions.move_to_element(element).click().perform()
		except TimeoutException as e:
			element = -1
			print("TimeoutException",element.text)
		except WebDriverException:
			element = -1
			print("No futher pages",element.text)
		finally:
			return driver, cookies, writer, stack, files_readable





















	# 	for e in elements:
	# 		ele = e.text.split("\n")
	# 		if "." in e: #This is a file
	# 			print(ele)
	# 			writer.writerow(ele[0])
	# 		else: #This is a folder
	# 			stack.append(ele)
	# 			for last_in in stack:	
	# 				if last_in == ele:
	# 					writer.writerow(ele[0], "Checked")
	# 					print("ele[0]: ", ele[0])
	# 					actions.move_to_element(ele).double_click().perform #Click into the folder
	# 					getFileStructure(element, driver, cookies, writer)
	# 					stack.pop()
	# 				else:
	# 					writer.writerow(ele[0])
	# 	return driver, cookies, writer, stack, files_readable

	# elif element != -1:
	# 	driver.find_element(By.CLASS_NAME,"on-end")
	# 	actions.move_to_element(element).click().perform()

	# 	# driver.click()
	# 	current = driver.find_element(By.CLASS_NAME, "current")
	# 	print(current.text)
	# 	for i in current.text:
	# 		if str(i[0]) != "0":
	# 			getFileList(element, driver, cookies, writer, stack, files_readable)
	# 		else:
	# 			driver.find_element(By.CLASS_NAME,"file__back").click()
	# 	getFileList(element, driver, cookies, writer, stack, files_readable)


	# if :
	# 	print("CAPTCHA")
	# for item in driver.find_elements(By.CLASS_NAME, value="file-listing__item"):
	# items = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME,"phone-no ")))
	# for item in items:
	# 	print(item)
	# 	if item.find_element(By.CLASS_NAME, value="file__name--folder"):
	# 		print("item:",item.text)
	# 		cookies = pickle.load(open("cookies.pkl", "rb"))
	# 		print(cookies)
	# 		for cookie in cookies:
	# 			driver.add_cookie(cookie)
	# 		actions.double_click(item).perform()
	# 	else:
	# 		print("item:",item.text)
	# 		cookies = pickle.load(open("cookies.pkl", "rb"))
	# 		print(cookies)
	# 		for cookie in cookies:
	# 			driver.add_cookie(cookie)
	# 		actions.mote_to_element(item).double_click().perform()
			
	# 		print("Get files here")
	# if value.find(".") == -1:
	# 	folders.append(value)
	# 	print("Folders",folders)
		

		'''
			Next steps:
				1. traverse + paging
				2. write filename into a file
				3. add in the downloads (clicking)

			Search for sudo code for recuresively traversing a tree.

			Download files first, move into folder after


			Get files function
			get folders function --> Call folder function with new folder.
		'''

			# Loop through the file-listing__item
			# Loop through and check for any child under and double clikc if its a folder.
			# Go through the folders recursively
			# Check if the file exists within the os.
			# I can click on file-listing__name file__name--xls 
			# Paging can be an issue.
				#Accout for the number of pages
			# search for tree for the recursive traversing + paging + selenium code
			# create a stack to traverse === Some kind of data structure
			# Emulate the cookie --> 
			# Collect all files --> everythung I'm seeing
				# Run get requests.
				# Collect all file names, folders, etc....
				# Make sure the session ID is spoofed with session IDs.
				# Get cookies
				# https://lockbitaptc2iq4atewz2ise62q63wfktyrl4qtwuk5qax262kgtzjqd.onion.ly/ajax/listing-post?file-download=true&folder-id=1238&data-dir=GENAZSSP01%2FG%2FArchive%2F012.xls
	# else:
	# 	filename = driver.find_elements_by_class_name('file-listing__item ')
	# 	files.append(filename)
	# 	driver.find_element_by_name('post-download-btn').click()
	# 	driver.implicitly_wait(10)

	# 	clickable_element = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//div[@class='post-downlod-btn']")))





def driver_creation(url, directory):
	prefs = {
		"download.default_directory" : directory,
		"download.prompt_for_download": False,
		"download.directory_upgrade": True,
		"safebrowsing_for_trusted_sources_enabled": False,
		"safebrowsing.enabled": False
	}

	chrome_options = ChromeOptions()
	chrome_options.add_argument("--incognito")
	chrome_options.add_experimental_option("prefs", prefs)
	service = ChromeService(executable_path=ChromeDriverManager().install())
	
	driver = webdriver.Chrome(service=service, options=chrome_options)
	download(url, directory, driver)

def main(argv):
	path = ''
	url = ''

	try:
		opts, args = getopt.getopt(argv,"u:d:p:t", ["url","destination","proxy","test"])

	except getopt.GetoptError:
		print('py combinator.py -p <path to source folder> -d <destination folder location> -e <type of file .csv, .xlsx>')
		sys.exit(2)

	for opt, arg in opts:
		if opt in('-h', '--help'):
			print('py combinator.py -p <path to source folder> -d <destination folder location> -e <type of file .csv, .xlsx>')
			sys.exit()
		elif opt in ("-u", "--url"):
			url = arg
		elif opt in ('-d', '--destination'):
			destination = arg
		elif opt in ('-p', '--proxy'):
			proxy = arg
		elif opt in ("-t", "--test"):
			print(url, destination)

			prefs = {
				"download.default_directory" : destination,
				"download.prompt_for_download": False,
				"download.directory_upgrade": True,
				"safebrowsing_for_trusted_sources_enabled": False,
				"safebrowsing.enabled": False
			}

			chrome_options = ChromeOptions()
			chrome_options.add_experimental_option("prefs", prefs)
			service = ChromeService(executable_path=ChromeDriverManager().install())
			
			driver = webdriver.Chrome(service=service, options=chrome_options)
			driver.get(url)


			exit(1)
	driver_creation(url, destination)

if __name__ == '__main__':
	main(sys.argv[1:])