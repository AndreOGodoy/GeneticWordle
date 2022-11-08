import wordle_solver
import gen_instance
import random
import numpy as np
import matplotlib.pyplot as plt

def wordle_perform_tests(test_count):
    # Plot settings
    plt.figure(figsize = (8,6), dpi = 72)

    word_list, _ = gen_instance.generate_from_wordle_list()
    random_results = []
    greedy_results = []
    for i in range(test_count):
        test_secret_word = random.choice(word_list)
        
        random_result = wordle_solver.solve_wordle_random(word_list, test_secret_word)
        random_results += [random_result]
        
        greedy_result = wordle_solver.solve_wordle_greedy(word_list, test_secret_word)
        greedy_results += [greedy_result]

    # Histograms
    plt.hist(greedy_results, bins=np.arange( min(greedy_results) - 0.5 , max(greedy_results) + 1.5 , 1.0), alpha=0.5, color='goldenrod')
    plt.hist(random_results, bins=np.arange( min(random_results) - 0.5 , max(random_results) + 1.5 , 1.0), alpha=0.5, color='cornflowerblue')

    # Averages
    plt.axvline(np.mean(greedy_results), color='goldenrod', linestyle='solid', linewidth=2)
    plt.axvline(np.mean(random_results), color='cornflowerblue', linestyle='solid', linewidth=2)

    plt.savefig(f'./out/test_greedy.png')

if __name__ == '__main__':
    wordle_perform_tests(1000)
