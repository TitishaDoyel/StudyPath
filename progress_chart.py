
import csv
import os
import matplotlib.pyplot as plt

FILE_NAME = "progress.csv"
print("CSV location:", os.path.abspath(FILE_NAME))
print("CSV file exists:", os.path.exists(FILE_NAME))
print("Matplotlib version:", plt.matplotlib.__version__)

if not os.path.exists(FILE_NAME):
    print("No learning records found.")
else:
    topic_scores = {}

    with open(FILE_NAME, "r", newline="") as file:
        records = csv.DictReader(file)

        for record in records:
            print("Record found:", record)
            topic = record["Topic"].strip().title()
            percentage = float(record["Percentage"])

            if topic not in topic_scores:
                topic_scores[topic] = []

            topic_scores[topic].append(percentage)

    if not topic_scores:
        print("No learning records found.")
    else:
        topics = list(topic_scores.keys())
        averages = [
            sum(scores) / len(scores)
            for scores in topic_scores.values()
        ]

        plt.bar(topics, averages)
        plt.title("StudyPath - Topic-wise Progress")
        plt.xlabel("Topics")
        plt.ylabel("Average Score (%)")
        plt.ylim(0, 100)
        plt.tight_layout()
        
        plt.savefig("study_progress.png")
        print("Chart saved as study_progress.png")
        plt.show(block=True)
