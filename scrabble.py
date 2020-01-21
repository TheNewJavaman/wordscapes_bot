#!/usr/bin/env python3
from _thread import start_new_thread
from sys import argv
from urllib import request
import re

try:
	letters = argv[1]
except:
	print("No charset specified")
	exit()
try:
	if argv[2]:
		format = True
except:
	format = False
valid_words = []
done_list = []
with open("dictionary.txt") as f:
	dictionary = f.read().split("\n")

def search_thread(start):
	for i in range(start, start + 10000):
		if i > len(dictionary) - 1:
			break
		word = dictionary[i]
		valid = True
		for char in word:
			if word.count(char) > letters.count(char) or len(word) <= 2 or "'" in word:
				valid = False
				break
		if valid:
			valid_words.append(word)
	done_list.append(int(i / 10000))
	done_list.sort()

for i in range(0, 11):
	start_new_thread(search_thread, (i * 10000,))
while len(done_list) < 11:
	pass

valid_words.sort(key=lambda item: (len(item), item))
valid_words.remove("")

if format:
	for i, word in enumerate(valid_words):
		formatted_i = str(i + 1) + ". "
		while len(str(len(valid_words))) > len(formatted_i) - 2:
			formatted_i = " " + formatted_i
		formatted_word = word + ": "
		while len(valid_words[len(valid_words) - 1]) > len(formatted_word) - 2:
			formatted_word += " "
		webpage = request.urlopen("http://www.dictionary.com/browse/" + word).read()
		shit_biscuit = word[0].upper() + word[1:] + " definition"
		regex = re.search(shit_biscuit + "(.*?)\.", str(webpage))
		try:
			formatted_meaning = regex.group(0).replace("See more.", "").replace(shit_biscuit + ", ", "")
			formatted_meaning = formatted_meaning[0:len(formatted_meaning) - 1]
			print(formatted_i + formatted_word + formatted_meaning)
		except:
			print(formatted_i + formatted_word.replace(":", " "))
else:
	for word in valid_words:
		print(word)
