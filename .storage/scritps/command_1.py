import sys, json

data = json.loads(sys.argv[1])

town = data.get('town', 'Tczew')
number = data.get('number', 1)

print(f"weather in {town} is {number} degrees")