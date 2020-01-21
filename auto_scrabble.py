from _thread import start_new_thread
from copy import copy
from math import ceil
from PIL import Image, ImageOps
import pyautogui as screen
screen.FAILSAFE = False
from time import sleep

def refocus():
	screen.click(0, 0)
	x = int(screen.size()[0] / 2)
	y = int(screen.size()[1] / 2)
	screen.moveTo(x, y)

# Read in letters and mouse input
def input_semimanual_letters():
	letter_data = []
	print("\nType letter and press [Enter] while hovering over it,")
	print("Or immediately press [Enter] to continue")
	
	while 1:
		new_letter = {}
		new_letter["letter"] = str(input(" - Letter: "))
		if "" is new_letter["letter"]:
			print("\nFinished recording data. Solving...")
			break
		coordinates = screen.position()
		new_letter["x"] = coordinates[0]
		new_letter["y"] = coordinates[1]
		letter_data.append(new_letter)

	return letter_data

# Read in button coordinates for future use
def input_semimanual_next_level():
	print("\nPress [Enter] while hovering over button")
	input("  ")
	coordinates = screen.position()
	next_level_data["x"] = coordinates[0]
	next_level_data["y"] = coordinates[1]

def auto_letter(letter, invert):
	if invert:
		letter_image = Image.open('images/' + letter + '.png')
	else:
		letter_image = Image.open('images/' + letter + '_i.png')
	letter_boxes = list(screen.locateAllOnScreen(letter_image, confidence=0.92, grayscale=True, region=(845, 670, 1065, 880)))
	for letter_box in letter_boxes:
		new_letter = {}
		new_letter["letter"] = letter
		new_letter["x"] = letter_box[0] + int(letter_box[2] / 2)
		new_letter["y"] = letter_box[1] + int(letter_box[3] / 2)

		l = new_letter
		valid = True
		for d in letter_data:
			if d["letter"] == l["letter"] and abs(d["x"] - l["x"]) < 5 and abs(d["y"] - l["y"]) < 5:
				valid = False
				break
		if valid:
			letter_data.append(new_letter)
	
	done_threads.append(1)

def auto_letters():
	alphabet = 'abcdefghijklmnopqrstuvwxyz'
	global letter_data, done_threads
	letter_data = []
	done_threads = []

	for letter in alphabet:
		start_new_thread(auto_letter, (letter, False))
		start_new_thread(auto_letter, (letter, True))
	while len(done_threads) < len(alphabet) * 2:
		pass

	return letter_data

def auto_next_box(box_data):
	boxes = list(screen.locateAllOnScreen('images/' + box_data[0] + '.png', confidence=0.8, grayscale=True, region=box_data[1]))
	try:
		level_boxes += boxes
	except:
		level_boxes = boxes

		for level_box in level_boxes:
			x = level_box[0] + int(level_box[2] / 2)
			y = level_box[1] + int(level_box[3] / 2)
			screen.click(x, y)
	
	done_threads.append(1)

def auto_next_level():
	global level_boxes, done_threads
	level_boxes = []
	done_threads = []
	boxes = [('level1', (880, 695, 1030, 730)), ('level2', (880, 505, 1035, 545)), ('collect', (880, 695, 1030, 730)), ('close', (1050, 320, 1085, 355))]

	for box in boxes:
		start_new_thread(auto_next_box, (box,))
	while len(done_threads) < len(boxes):
		pass

# For each of <= 5000 words, check if word fits with rules
def scrabble_search(i_start):
	for i in range(i_start, i_start + 5000):
		if i > len(dictionary) - 1:
			break
		word = dictionary[i]
		valid = True
		for char in word:
			if word.count(char) > charset.count(char) or len(word) <= 2 or "'" in char:
				valid = False
				break
		if valid:
			valid_words.append(word)

	done_threads.append(1)

# Manages reading through dictionary
def scrabble():
	global valid_words, done_threads, dictionary
	valid_words, done_threads = [], []

	with open("./dictionary_full.txt") as f_dictionary:
		dictionary = f_dictionary.read().split("\n")

	num_words = len(dictionary)
	max_range = ceil(num_words / 5000)
	for i in range(0, max_range):
		start_new_thread(scrabble_search, (i * 5000,))
	while len(done_threads) < max_range:
		pass

	valid_words.sort(key = lambda item: (len(item), item))
	try:
		valid_words.remove("")
	except:
		pass

	return valid_words

# Drags mouse over letters to make words!
def solve_level(letter_data):
	global charset
	charset = ""
	for letter in letter_data:
		charset += letter["letter"]
	if charset: print('  Charset: ' + ''.join(sorted(charset)))
	valid_words = scrabble()

	for word in valid_words:
		word_coordinates = []
		letter_data_tmp = copy(letter_data)
		for i, letter in enumerate(word):
			letter_datum = list(filter(lambda data: (data["letter"] == letter), letter_data_tmp))[0]
			x, y = letter_datum["x"], letter_datum["y"]
			letter_data_tmp.remove(letter_datum)

			if i == 0:
				screen.moveTo(x, y)
				screen.mouseDown()
			elif i == len(word) - 1:
				screen.moveTo(x, y)
				screen.mouseUp()
			else:
				screen.moveTo(x, y)

# Moves past a menu screen
def next_level():
	x, y = next_level_data["x"], next_level_data["y"]
	screen.click(x, y)

# Organizes all the functions
def main():
	global next_level_data
	next_level_data = {}

	print("--- Autosolve Wordscapes ---")
	print("Type [a] for auto or [m] for manual mode")
	choice = str(input("  Mode: "))

	if choice is "m":
		while choice is not "":
			print("\nType [s] to solve or [n] for next level,")
			print("Or immediately press [Enter] to exit")
			choice = str(input("  Choice: "))
			if choice is "s":
				solve_level(input_semimanual_letters())
			elif choice is "n":
				if not next_level_data:
					input_semimanual_next_level()
				next_level()
			refocus()
		print("\nExiting...")

	elif choice is "a":
		try:
			auto_next_level()
			while True:
				refocus()
				sleep(1 / 2)
				solve_level(auto_letters())
				refocus()
				auto_next_level()
		except KeyboardInterrupt:
			print("\nExiting...")

main()