# Accumulated information to be updated along the solving process
class WordleInfo:
    def __init__(self):
        self.green_result = ['-', '-', '-', '-', '-']
        self.yellow_letters = []
        self.gray_letters = []

def update_obtained_info(guess, guess_result, info: WordleInfo):
    for i in range(len(info.green_result)):
        if guess_result[i] == 'G' and info.green_result[i] == '-': info.green_result[i] = guess[i]
        
        if (guess_result[i] == 'Y' or guess_result[i] == 'G'):
            if guess[i] not in info.yellow_letters: info.yellow_letters += [guess[i]]
        else:
            if guess[i] not in info.gray_letters: info.gray_letters += [guess[i]]

    return info
    
# Green letter distribution:
# Dictionary of the probability for each letter of the word list in each possible position
def green_letter_distribution(word_list, word_len = 5):
    dist_probability = {}
    word_count = len(word_list) 
    for i in range(word_count):
        word = word_list[i]
        for j in range(len(word)):
            if word[j] in dist_probability:
                dist_probability[word[j]][j] += 1
            else:
                dist_probability[word[j]] = [0 for x in range(word_len)]
    
    for letter in dist_probability:
        for i in range(len(dist_probability[letter])):
            dist_probability[letter][i] /= word_count

    return dist_probability

# Green letter probability ([0, 1]):
# How probable a word is to have green letters in each position based on green letter distribution
def green_letter_probability(word, gld):
    result = 0

    for i in range(len(word)):
        result += gld[word[i]][i]

    return result / len(word)

def sort_by_green_letter_probability(word_list, gld):
    return sorted(word_list, key=lambda word: green_letter_probability(word, gld), reverse=True)

# Expected green correctness ([0, 1]):
# How much do we expect the word to have green letters based on the accumulated information
def get_expected_green_correctness(word, info: WordleInfo):
    result = 0
    for i in range(len(word)):
        if word[i] == info.green_result[i]: result += 1
    return result / len(word)

# Expected yellow correctness ([0, 1]):
# How much do we expect the word to have green or yellow letters based on the accumulated information
def get_expected_yellow_correctness(word, info: WordleInfo):
    result = 0
    for i in range(len(word)):
        if word[i] in info.yellow_letters: result += 1
    return result / len(word)

# Expected gray correctness ([0, 1]):
# How much do we expect the word to not have gray letters based on the accumulated information
def get_expected_gray_correctness(word, info: WordleInfo):
    result = 0
    for i in range(len(word)):
        if word[i] not in info.gray_letters: result += 1
    return result / len(word)

def evaluate_guess(guess, secret):
    result = []
    for i in range(len(guess)):
        if guess[i] == secret[i]: result += ['G']
        elif guess[i] in secret: result  += ['Y']
        else: result += ['-']
    return result, result == ['G','G','G','G','G']

def get_letters_to_remove(guess, guess_result):
    result = []
    for i in range(len(guess_result)):
        if guess_result[i] == '-':
            result += [guess[i]]
    return result

def remove_letters_from_word_list(words, letters_to_remove):
    result = []
    for i in range(len(words)):
        word = words[i]
        remove = False
        for j in range(len(word)):
            if word[j] in letters_to_remove: remove = True
        
        if not remove: result += [word] 
    return result
