import gen_instance
from genetic import solve_wordle_genetic
from greedy import solve_wordle_greedy
from random_solver import solve_wordle_random

# def print_glp(word, gld):
#     glp = green_letter_probability(word, gld)
#     print(f'The green letter probability for {word} is {glp}.')


# def print_obtained_info(info: WordleInfo):
#     print(f'Current green results: {info.green_result}')
#     print(f'Current yellow letters: {info.yellow_letters}')
#     print(f'Current gray letters: {info.gray_letters}')

# def print_guess_score(guess, info: WordleInfo):
#     print(f'[{guess}] Expected green correctness: {get_expected_green_correctness(guess, info)}')
#     print(f'[{guess}] Expected yellow correctness: {get_expected_yellow_correctness(guess, info)}')
#     print(f'[{guess}] Expected gray correctness: {get_expected_gray_correctness(guess, info)}')


if __name__ == '__main__':
    word_list, secret = gen_instance.generate_from_wordle_list()

    greedy_result = solve_wordle_greedy(word_list, secret)
    print(f'Greedy solved in {greedy_result} guesses.')
    genetic_result = solve_wordle_genetic(word_list, secret)
    print(f'Genetic solved in {genetic_result} guesses.')