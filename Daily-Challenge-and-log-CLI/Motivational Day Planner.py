import random
import datetime

def main():
    today = datetime.date.today()
    today_str = today.strftime("%Y-%m-%d")
    yesterday = today - datetime.timedelta(days=1)
    yesterday_str = yesterday.strftime("%Y-%m-%d")
    log = Progress(yesterday_str)
    fetchQuote()
    chal = challengeGenerator()
    progressquestion(log, chal, today_str)

def fetchQuote():
    with open("quotes.txt", "r", encoding="utf-8") as file:
        quote = random.choice(file.readlines()).strip()
        print("\n🌟 Quote of the Day:\n" + quote + "\n")

def challengeGenerator():
    with open("challenge.txt", "r", encoding="utf-8") as file:
        challenge = random.choice(file.readlines()).strip()
        print("💪 Today's Challenge:\n" + challenge + "\n")
    return challenge

def Progress(yesterday_str, filename="logs.txt"):
    collected_lines = []
    found_yesterday = False

    with open(filename, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if line == f"[{yesterday_str}]":
                found_yesterday = True
                continue
            elif found_yesterday and line.startswith("[") and line.endswith("]"):
                break
            if found_yesterday:
                collected_lines.append(line)

    return "\n".join(collected_lines)

def progressquestion(log, chal, today_str):
    print("📘 Yesterday's Log:")
    print(log if log else "No record found for yesterday.")
    try:
        progress = input("📝 How did your challenge go?\n")
    except (KeyboardInterrupt, EOFError):
        print("\n⚠️ Input cancelled by user.")
        progress = "No input provided."
    except Exception as e:
        print(f"⚠️ Unexpected input error: {e}")
        progress = "Input error."

    try:
        with open("logs.txt", "a", encoding="utf-8") as file:
            file.write(f"\n[{today_str}]\n")
            file.write(f"Challenge: {chal}\n")
            file.write(f"Reflection: {progress}\n")
    except Exception as e:
        print(f"⚠️ Failed to write to log file: {e}")


main()
