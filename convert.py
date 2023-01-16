WORDS = []

with open("words_alpha.txt", "r") as f:
    for line in f.readlines():
        word = line.strip()
        if len(word) == 5:
            WORDS.append(word)
