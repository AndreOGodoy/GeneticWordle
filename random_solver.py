from util import *
import random

# Random heuristic
def solve_wordle_random(words, secret):
    guesses = 0
    
    while True:
        guess = random.choice(words)
        # print(f'[RANDOM] Guessing: {guess}...')
        guesses += 1

        # Evaluate guess
        guess_result, is_correct = evaluate_guess(guess, secret)
        if is_correct:
            return guesses
        else:
            # Update word list
            letters_to_remove = get_letters_to_remove(guess, guess_result)
            words = remove_letters_from_word_list(words, letters_to_remove)
            # print(f'    Wrong guess! Word list now has {len(words)} words.')
