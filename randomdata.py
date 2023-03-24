import csv
import random
from itertools import permutations

# List of household work categories
categories = [
    "cleaning",
    "cooking",
    "gardening",
    "childcare",
    "petcare",
    "eldercare",
    "shopping",
    "homeorganize",
    "handyman",
    "tutoring",
]

# Generate 10000 random data samples
data = []
for i in range(10000):
    # Generate unique customer and worker IDs
    customer_id = f"{i}"
    worker_id = f"{i}"
    while worker_id == customer_id:
        worker_id = f"{random.randint(0, 9999)}"
    # Randomly assign the worker's skills
    worker_skills = random.sample(categories, k=random.randint(1, len(categories)))
    # Generate a random rating between 1 and 5
    rating = random.randint(1, 5)
    # Create a dictionary to hold the data for this sample
    row = {"customer_id": customer_id, "worker_id": worker_id, "rating": rating}
    # Set a flag for each category indicating whether the worker has that skill or not
    for category in categories:
        row[category] = int(category in worker_skills)
    # Add the data sample to the list
    data.append(row)

# Add 50 tasks completed by one customer and one worker
for i in range(50):
    customer_id = "10000"
    worker_id = "20000"
    # Generate a random list of skills for the worker
    worker_skills = random.sample(categories, k=random.randint(1, len(categories)))
    # Generate a random rating between 1 and 5
    rating = random.randint(1, 5)
    # Create a dictionary to hold the data for this sample
    row = {"customer_id": customer_id, "worker_id": worker_id, "rating": rating}
    # Set a flag for each category indicating whether the worker has that skill or not
    for category in categories:
        row[category] = int(category in worker_skills)
    # Add the data sample to the list
    data.append(row)

# Add 50 tasks completed by another worker
for i in range(50):
    customer_id = "20000"
    worker_id = "10000"
    # Generate a random list of skills for the worker
    worker_skills = random.sample(categories, k=random.randint(1, len(categories)))
    # Generate a random rating between 1 and 5
    rating = random.randint(1, 5)
    # Create a dictionary to hold the data for this sample
    row = {"customer_id": customer_id, "worker_id": worker_id, "rating": rating}
    # Set a flag for each category indicating whether the worker has that skill or not
    for category in categories:
        row[category] = int(category in worker_skills)
    # Add the data sample to the list
    data.append(row)

# Write the data to a CSV file
with open("household_data.csv", "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["customer_id", "worker_id", *categories, "rating"])
    for row in data:
        writer.writerow(
            [
                row["customer_id"],
                row["worker_id"],
                *[row[category] for category in categories],
                row["rating"],
            ]
        )
