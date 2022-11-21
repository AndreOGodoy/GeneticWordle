import wordle_solver
import gen_instance
import random
import numpy as np
# import matplotlib.pyplot as plt
import shutil
import asyncio
from typing import List
import subprocess
import os

class Tester:
    dict_sizes: List[int]

    rng: np.random.Generator

    def __init__(self, sizes: List[int], cpp_source_path: str):
        self.dict_sizes = sizes
        self.rng = np.random.default_rng()

        self.dicts_path: str
        self._compile_program(cpp_source_path)

    def clear_folder(self, path: str):
        shutil.rmtree(path, ignore_errors=True)

    def _compile_program(self, path: str):
        bin_path = './bin'
        os.makedirs(bin_path, exist_ok=True)

        command = ['g++', '-O2', path, '-o', bin_path + '/wordle'] #talvez tenha que mudar pra windows
        subprocess.run(command)

    def populate_test_folder(self, path: str):
        self.dicts_path = path
        os.makedirs(path, exist_ok=True)
        
        dictionary, _ = gen_instance.generate_from_wordle_list()
        for size in self.dict_sizes:
            subdict = self.rng.choice(dictionary, size, replace=False)

            with open(path+f'/dict_{size}.txt', 'w+') as file:
                file.writelines('\n'.join(subdict))

    async def execute_training(self, training_instances: int, pop_size: int, elite_count: int, iterations: int, cross_prob: float, mut_prob: float, clear_folder = False):
        command = ['./bin/wordle', 'train', str(training_instances), str(pop_size), str(elite_count), str(iterations), str(cross_prob), str(mut_prob)]

        param_folder = 'train_out/' + f'{training_instances}_{pop_size}_{elite_count}_{iterations}_{cross_prob}_{mut_prob}'
        if clear_folder:
            self.clear_folder(param_folder)

        async def training(dict_path: str):
            command_with_dict = command + [dict_path]
            result = subprocess.run(command_with_dict, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout = result.stdout.decode()
            best_individual = stdout[stdout.index('RESULT'):].replace('\n', '')
            
            dict_folder = int(''.join(filter(str.isdigit, dict_path)))
            os.makedirs(f'{param_folder}/{dict_folder}', exist_ok=True)
            with open(f'{param_folder}/{dict_folder}/best.txt', 'a') as file:
                file.write(best_individual + '\n')

        tasks = []
        for dictionary in os.listdir(self.dicts_path):
            tasks.append(training(f'{self.dicts_path}/{dictionary}'))

        await asyncio.gather(*tasks)

    # TODO
    async def execute_test(self, path_to_best_individual: str):
        command = ['./bin/wordle', 'test'] #...

        raise NotImplementedError

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

async def main():
    # Wordle word list size is ~2.3k
    tester = Tester(sizes=[200, 500, 1000, 2000], cpp_source_path='./cpp/wordle_main.cpp')
    tester.populate_test_folder('./test_dicts')
    await tester.execute_training(1, 1, 1, 1, 1, 0, clear_folder=True)

if __name__ == '__main__':
    asyncio.run(main())
    #wordle_perform_tests(1000)
