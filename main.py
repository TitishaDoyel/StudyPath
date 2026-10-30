
import csv
import os

FILE_NAME = "progress.csv"


def record_learning():
    print("\n===== RECORD NEW LEARNING =====")

    name = input("Enter your name: ")
    topic = input("Enter the topic you studied: ")

    try:
        score = int(input("Enter your quiz score: "))
        total = int(input("Enter the total marks: "))
    except ValueError:
        print("Please enter numbers only.")
        return

    if total <= 0 or score < 0 or score > total:
        print("Invalid score or total marks.")
        return

    percentage = (score / total) * 100

    if percentage < 50:
        suggestion = "Revise and practise again."
    elif percentage < 80:
        suggestion = "Practise a few more questions."
    else:
        suggestion = "Great progress! Try the next topic."

    file_exists = os.path.exists(FILE_NAME)

    with open(FILE_NAME, "a", newline="") as file:
        writer = csv.writer(file)

        if not file_exists or os.path.getsize(FILE_NAME) == 0:
            writer.writerow([
                "Name", "Topic", "Score",
                "Total", "Percentage", "Suggestion"
            ])

        writer.writerow([
            name, topic, score,
            total, percentage, suggestion
        ])

    print("\nYour percentage:", percentage, "%")
    print("Suggestion:", suggestion)
    print("Your progress has been saved!")


def view_history():
    print("\n===== LEARNING HISTORY =====")

    if not os.path.exists(FILE_NAME):
        print("No learning records found.")
        return

    with open(FILE_NAME, "r", newline="") as file:
        records = list(csv.DictReader(file))

    if not records:
        print("No learning records found.")
        return

    for number, record in enumerate(records, start=1):
        print("\nRecord", number)
        print("Student:", record["Name"])
        print("Topic:", record["Topic"])
        print("Score:", record["Score"], "/", record["Total"])
        print("Percentage:", record["Percentage"], "%")
        print("Suggestion:", record["Suggestion"])


def view_dashboard():
    print("\n===== PROGRESS DASHBOARD =====")

    if not os.path.exists(FILE_NAME):
        print("No learning records found.")
        return

    with open(FILE_NAME, "r", newline="") as file:
        records = list(csv.DictReader(file))

    if not records:
        print("No learning records found.")
        return

    percentages = [float(record["Percentage"]) for record in records]

    average = sum(percentages) / len(percentages)
    best = max(percentages)
    lowest = min(percentages)

    print("Total records:", len(records))
    print("Average percentage:", round(average, 2), "%")
    print("Best quiz result:", best, "%")
    print("Lowest quiz result:", lowest, "%")

    if average < 50:
        print("Overall suggestion: Revise your topics regularly.")
    elif average < 80:
        print("Overall suggestion: Keep practising to improve.")
    else:
        print("Overall suggestion: Great work! Keep learning.")


def topic_analysis():
    print("\n===== TOPIC-WISE PROGRESS =====")

    if not os.path.exists(FILE_NAME):
        print("No learning records found.")
        return

    with open(FILE_NAME, "r", newline="") as file:
        records = list(csv.DictReader(file))

    if not records:
        print("No learning records found.")
        return

    topic_scores = {}

    for record in records:
        topic = record["Topic"].strip().lower()
        percentage = float(record["Percentage"])

        if topic not in topic_scores:
            topic_scores[topic] = []

        topic_scores[topic].append(percentage)

    for topic, scores in topic_scores.items():
        average = sum(scores) / len(scores)

        print("\nTopic:", topic.title())
        print("Attempts:", len(scores))
        print("Average score:", round(average, 2), "%")

        if average < 50:
            print("Advice: Revise the basics.")
        elif average < 80:
            print("Advice: Practise more questions.")
        else:
            print("Advice: Try more advanced questions.")

def recommend_study():
    print("\n===== SMART STUDY RECOMMENDATIONS =====")

    if not os.path.exists(FILE_NAME):
        print("No learning records found.")
        return

    with open(FILE_NAME, "r", newline="") as file:
        records = list(csv.DictReader(file))

    if not records:
        print("No learning records found.")
        return

    topic_scores = {}

    for record in records:
        topic = record["Topic"].strip().lower()
        percentage = float(record["Percentage"])

        if topic not in topic_scores:
            topic_scores[topic] = []

        topic_scores[topic].append(percentage)

    averages = {}

    for topic, scores in topic_scores.items():
        averages[topic] = sum(scores) / len(scores)

    weakest_topic = min(averages, key=averages.get)
    weakest_score = averages[weakest_topic]

    print("Topic to practise first:", weakest_topic.title())
    print("Average score:", round(weakest_score, 2), "%")

    if weakest_score < 50:
        print("Advice: Revise the basics of this topic.")
    elif weakest_score < 80:
        print("Advice: Practise more questions on this topic.")
    else:
        print("Great work! Try more advanced questions.")


while True:
    print("\n===== STUDYPATH =====")
    print("1. Record new learning")
    print("2. View learning history")
    print("3. View progress dashboard")
    print("4. View topic-wise progress")
    print("5. Smart study recommendations")
    print("6. Exit")

    choice = input("Choose an option: ")

    if choice == "1":
        record_learning()
    elif choice == "2":
        view_history()
    elif choice == "3":
        view_dashboard()
    elif choice == "4":
        topic_analysis()
    elif choice == "5":
         recommend_study()
    elif choice == "6":
        print("Thank you for using StudyPath!")
        break
    else:
        print("Invalid choice. Enter 1, 2, 3, or 4.")
