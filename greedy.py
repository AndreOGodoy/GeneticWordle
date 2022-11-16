from util import *

# Greedy GLP-based heuristic
def solve_wordle_greedy(words, secret):
    guesses = 0
    past_guesses = []

    while True:
        # Choose word
        gld = green_letter_distribution(words)
        words_by_glp = sort_by_green_letter_probability(words, gld)
        guess = ''
        for i in range(len(words_by_glp)):
            if words_by_glp[i] not in past_guesses:
                guess = words_by_glp[i]
                break

        print(f'[GREEDY] Guessing: {guess}...')
        guesses += 1

        # Evaluate guess
        guess_result, is_correct = evaluate_guess(guess, secret)
        if is_correct:
            return guesses
        else:
            # Update word list for next iteration
            letters_to_remove = get_letters_to_remove(guess, guess_result)
            words = remove_letters_from_word_list(words, letters_to_remove)
            past_guesses += [guess]
            # print(f'    Wrong guess! Word list now has {len(words)} words.')
