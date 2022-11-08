import random
import gen_instance

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

if __name__ == '__main__':
    word_list, secret = gen_instance.generate_from_wordle_list()
    result = solve_wordle(word_list, secret)
    print(result)