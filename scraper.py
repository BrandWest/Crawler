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
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException

import pickle
import time, os, sys, getopt, csv, re
import pandas as pd


def download(url, directory, driver):
	actions = ActionChains(driver)

	stack = []
	directory_path = []
	driver.get(url)
	time.sleep(10)
	url = url + 'post/USLfL9XIAOk9xnX562344fec4aac8'
	# time.sleep(10)

	driver.get(url)
	with open (directory + "fileStructure.csv", "w") as file:
		writer = csv.writer(file)
		element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME,"file-listing__item")))
		file = driver.find_element(By.CLASS_NAME, "file-listing__item").text.split('\n')
		directory_path.append(file[0]) #Root
		stack.append(driver.find_element(By.CLASS_NAME, "file-listing__item")) #Root
		writer.writerow([str(file[0])])
		actions.move_to_element(element).double_click().perform()
		while(True):
			print("while loop")
			ignored_exceptions=(NoSuchElementException,StaleElementReferenceException,)
			element = WebDriverWait(driver, 10,ignored_exceptions=ignored_exceptions).until(EC.presence_of_element_located((By.CLASS_NAME,"file-listing__item")))
			driver, writer, stack, directory_path = getFileStructure(element, driver, writer, stack, directory_path)
			
			# your_element = WebDriverWait(your_driver, some_timeout,ignored_exceptions=ignored_exceptions).until(expected_conditions.presence_of_element_located((By.ID, my_element_id)))


def getFileListing(elements, driver, writer, stack, directory_path):
	elements = driver.find_elements(By.CLASS_NAME,"file-listing__item")
	for i in elements:
		directory_path.append(i.get_attribute('data-dir'))
		stack.append(i)
		writer.writerow(str([i.get_attribute('data-dir')]))

	return stack, directory_path

#Check if its a folder, or not.
def folder_nav(stack, directory_path, driver):
	actions = ActionChains(driver)

	for element in stack[::-1]:
		print("folder nav", element.text)
		first_in = stack.pop()
		cookies = get_cookies(driver)

		actions.move_to_element(first_in).double_click().perform()

		return driver

	if 'folder' in on_end.get_attribute('outerHTML'):
		final_page = 'folder'
	else:
		final_page = 'no_folder'

	return final_page, back_one_page

def get_cookies(driver):
	pickle.dump(driver.get_cookies(), open("cookies.pkl","wb"))
	cookies = pickle.load(open("cookies.pkl", "rb"))
	
	#iterate the cookies
	for cookie in cookies:
		driver.add_cookie(cookie)

	return driver

def check_paging(driver):
	#check to see if paging is required
	forward = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME,"on-end")))
	pagination = driver.find_element(By.CLASS_NAME, 'file-listing__pagination')
	on_end = pagination.find_element(By.CLASS_NAME, "on-end")
	back = pagination.find_element(By.CLASS_NAME, "back-one-page")

	# <button class="on-start disabled"></button>
	
	if 'disabled' in on_end.get_attribute('outerHTML'):
		final_page = 'disabled'
	else:
		final_page = 'active'

	if 'disabled' in back.get_attribute('outerHTML'):
		back_one_page = 'disabled'
	else:
		back_one_page = 'active'

	return final_page, back_one_page

def getFileStructure(element, driver, writer, stack, directory_path):
	actions = ActionChains(driver)
	print("get File structure")
	#get cookies
	driver = get_cookies(driver)

	time.sleep(2)
	# driver.navigate().refresh()
	#wait for populate
	element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "file-listing__item")))
	
	#get all folders/files
	elements = driver.find_elements(By.CLASS_NAME,"file-listing__item")
	forward_pages, backward_pages = check_paging(driver)
	stack_printing(stack, directory_path)



	if forward_pages == 'active':
		print("click required")
		forward_flag = 1
		
		#go to end of pages
		time.sleep(2)
		actions.move_to_element(driver.find_element(By.CLASS_NAME, 'on-end')).click().perform()
		# element = driver.find_element(By.CLASS_NAME, 'on-end')
		# print(element.text)
		time.sleep(2)
		# element.click().perform()
		driver.find_elements(By.CLASS_NAME, "file-listing__item")
		time.sleep(2)
		stack, directory_path = getFileListing(elements, driver, writer, stack, directory_path)
		stack_printing(stack, directory_path)
		forward_pages, backward_pages = check_paging(driver)

		# stack, directory_path = getFileListing(element, driver, writer, stack, directory_path)
		# folder_nav(stack, directory_path, driver)


		while backward_pages == 'active':
			print("back one page")
			print("going into folder") 
			driver = folder_nav(stack, directory_path, driver)
			time.sleep(5)
			# backward = driver.find_element(By.CLASS_NAME, 'back-one-page')
			ignored_exceptions=(NoSuchElementException,StaleElementReferenceException,)
			backward = WebDriverWait(driver, 10, ignored_exceptions=ignored_exceptions).until(EC.presence_of_element_located((By.CLASS_NAME,"back-one-page")))

			if backward_pages == 'active' and forward_flag == 1:
				stack, directory_path = getFileListing(element, driver, writer, stack, directory_path)


				print("backward click")
				backward = WebDriverWait(driver, 10, ignored_exceptions=ignored_exceptions).until(EC.presence_of_element_located((By.CLASS_NAME,"back-one-page")))
				backward = driver.find_element(By.CLASS_NAME, 'back-one-page')
				# print("backward, pass: ", backward.get_attribute('back-one-page'))
				actions.move_to_element(backward).click().perform()
				stack, directory_path = getFileListing(element, driver, writer, stack, directory_path)

			else:
				print("No backward click, return.")
				back_one_dir = WebDriverWait(driver,10).until(EC.presence_of_element_located(By.CLASS_NAME,'file__back active'))
				back_one_dir = driver.find_element(By.CLASS_NAME,'file__back')
				actions.move_to_element(back_one_dir).click()
				getFileStructure(element, driver, writer, stack, directory_path)
			
			forward_pages, backward_pages = check_paging(driver)



			#Check the stack, see if the item is there. If there, and back-on-page is disabled. Click return
			#Get all file listings, go through each.
				# Root -> Y -> User1 -> Folder1 -> item


	elif forward_pages == 'disabled':
		print("NO click required")
		stack, directory_path = getFileListing(elements, driver, writer, stack, directory_path)
	

		for first_out in directory_path[::-1]:
			first_out_element = stack.pop()
			print("First Out:", first_out)
			print("First Out Element:",first_out_element)
			#If it is a file, write the value and pop

			

			# Here do the folder vs the regex
			element = first_out_element.get_attribute("outerHTML")
			if 'file__name--folder' not in element:
				print("NOT a folder")
				directory_path_value = directory_path.pop()
				# writer.writerow([str(directory_path_value)])
			else:
				print("a folder")
				actions.move_to_element(first_out_element).double_click().perform()
	
				#if not a file, Go into the folder.
				# element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "file-listing__item")))
				getFileStructure(element, driver, writer, stack, directory_path)

		'''




		'''				
		# driver, writer, stack, directory_path = getFileList(element, driver, writer, stack, directory_path)

		# for i in elements[::-1]:
		# 	# print("element i: ", i)
		# 	actions.move_to_element(element).double_click().perform()
		# 	getFileStructure(element, driver, writer, stack, directory_path)
		# 	# driver, writer, stack, directory_path = getFileList(element, driver, writer, stack, directory_path)

		# 	stack.pop()
			# actions.move_to_element(element).click().perform()

	# except TimeoutException as e:
	# 	element = -1
	# 	print("TimeoutException",element.text)
	# except WebDriverException:
	# 	element = -1
	# 	print("No futher pages",element.text)
	# finally:
	if len(stack) == 0:
		print("return")
		return driver, writer, stack, directory_path
	else:
		print("Finally, recurse")

		# getFileStructure(element, driver, writer, stack, directory_path)
		return driver, writer, stack, directory_path


def check_stack(stack, directory_path):
	return stack[-1]

def stack_printing(stack, directory_path):
	print('-------------------------------------------')
	# print("The Stack: ", stack)
	print('-------------------------------------------')
	print("The readable: ", directory_path)
	print('-------------------------------------------')

def getFileList(element, driver, writer, stack, directory_path):
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
		return driver, writer, stack, directory_path
	
	if element == -1: #No next page
		elements = driver.find_elements(By.CLASS_NAME, "file-listing__name")
		for first_out in directory_path[::-1]:
			first_out_element = stack.pop()
			if re.search(r'\.*', first_out):
				value = directory_path.pop()
				writer.writerow([str(value)])
			else:
				#Go into the folder.
				# element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "file-listing__item")))
				actions.move_to_element(first_out_element).click().perform()
				getFileStructure(element, driver, writer, stack, directory_path)

		for i in elements[::-1]:
			print(i)
			actions.move_to_element(element).double_click().perform()
			driver, writer, stack, directory_path = getFileList(element, driver, writer, stack, directory_path)

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
			return driver, writer, stack, directory_path





















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
	# 					getFileStructure(element, driver, writer)
	# 					stack.pop()
	# 				else:
	# 					writer.writerow(ele[0])
	# 	return driver, writer, stack, directory_path

	# elif element != -1:
	# 	driver.find_element(By.CLASS_NAME,"on-end")
	# 	actions.move_to_element(element).click().perform()

	# 	# driver.click()
	# 	current = driver.find_element(By.CLASS_NAME, "current")
	# 	print(current.text)
	# 	for i in current.text:
	# 		if str(i[0]) != "0":
	# 			getFileList(element, driver, writer, stack, directory_path)
	# 		else:
	# 			driver.find_element(By.CLASS_NAME,"file__back").click()
	# 	getFileList(element, driver, writer, stack, directory_path)


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