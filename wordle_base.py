import random
import gen_instance

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

def green_letter_probability(word, gld):
    result = 0

    for i in range(len(word)):
        result += gld[word[i]][i]

    return result

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

def solve_wordle(words, secret, max_guesses = 50):
    guesses = 0
    
    while guesses < max_guesses:
        # Choose word
        # TODO: Implement choice heuristics, currently choosing at random
        guess = random.choice(words)
        print(f'Guessing: {guess}...')
        guesses += 1

        # Evaluate guess
        guess_result, is_correct = evaluate_guess(guess, secret)
        if is_correct:
            return guesses
        else:
            # Update word list
            letters_to_remove = get_letters_to_remove(guess, guess_result)
            words = remove_letters_from_word_list(words, letters_to_remove)
            print(f'    Wrong guess! Word list now has {len(words)} words.')

    # Oops, exceeded number of max guesses (this shouldn't happen with heuristics, I think)
    return False

def print_glp(word, gld):
    glp = green_letter_probability(word, gld)
    print(f'The green letter probability for {word} is {glp}.')


if __name__ == '__main__':
    word_list, secret = gen_instance.generate_from_wordle_list()
    # result = solve_wordle(word_list, secret)
    # print(result)
    gld = green_letter_distribution(word_list)
    
    print_glp('ANDRE', gld)
    print_glp('JULIA', gld)