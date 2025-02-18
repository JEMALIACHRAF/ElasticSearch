import sys

current_city = None
temp_sum = 0
count = 0

for line in sys.stdin:
    city, temp = line.strip().split("\t")
    temp = float(temp)

    if current_city == city:
        temp_sum += temp
        count += 1
    else:
        if current_city:
            print(f"{current_city}\t{temp_sum/count:.2f}")
        current_city = city
        temp_sum = temp
        count = 1

# Print last city
if current_city:
    print(f"{current_city}\t{temp_sum/count:.2f}")
