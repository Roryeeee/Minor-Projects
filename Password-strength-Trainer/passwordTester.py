def main():
    symbols = "!@#$%^&*({'[]})=-\+_<>,|.?/:;"
    password = input("Enter your password to Train: ")
    score = 0


    print("Training your password...")
    score = Round1(password, score)
    score = Round2(password, score)
    score = Round3(password, score)
    score = Round4(password, score, symbols)
    score = Round5(password, score)

    print(f"\nFinal Strength Score: {score}/100")
    if score >= 80:
        print("Rating: Strong")
    elif score >= 50:
        print("Rating: Moderate")
    else:
        print("Rating: Weak")

    



def Round1(password, score):
    print("Round 1....", end=" ")
    count = 0
    for char in password:
        if char.isupper():
            count += 1
          
    if count > 0:
        print("Contains uppercase letters")
        score += 20
    return score

def Round2(password, score):
    print("Round 2....", end=" ")
    count = 0
    for char in password:
        if char.islower():
            count += 1
          
    if count > 0:
        print("Contains lowercase letters")
        score += 20 
    return score

def Round3(password, score):
    print("Round 3....", end=" ")
    count = 0
    for char in password:
        if char.isdigit():
            count += 1
          
    if count > 0:
        print("Contains numbers")
        score += 20 
    return score

def Round4(password, score, symbols):
    print("Round 4....", end=" ")
    count = 0
    for char in password:
        if char in symbols:
            count += 1
          
    if count > 0:
        print("Contains symbols")
        score += 20 
    return score

def Round5(password, score):
    print("Round 5....", end=" ")
    count = 0
    if len(password) >= 8:
        count += 1
          
    if count > 0:
        print("Contains sufficient letters")
        score += 20 
    return score

main()