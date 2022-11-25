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

    async def execute_training(self, training_instances: int, pop_size: int, elite_count: int,
                               iterations: int, cross_prob: float, mut_prob: float, clear_folder = False):

        command = ['./bin/wordle', 'train', str(training_instances), str(pop_size), str(elite_count), str(iterations), str(cross_prob), str(mut_prob)]

        param_folder = 'train_out/' + f'{training_instances}_{pop_size}_{elite_count}_{iterations}_{cross_prob}_{mut_prob}'
        if clear_folder:
            self.clear_folder(param_folder)

        async def training(dict_path: str):
            command_with_dict = command + [dict_path]
            result = await asyncio.create_subprocess_shell(' '.join(command_with_dict), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = await result.communicate()
            stdout = stdout.decode()
            best_individual = stdout[stdout.index('RESULT'):].replace('\n', '')

            dict_folder = int(''.join(filter(str.isdigit, dict_path)))
            print(f'{best_individual} > {param_folder}/{dict_folder}')
            os.makedirs(f'{param_folder}/{dict_folder}', exist_ok=True)
            with open(f'{param_folder}/{dict_folder}/best.txt', 'a') as file:
                file.write(best_individual + '\n')

        tasks = []
        for dictionary in os.listdir(self.dicts_path):
            tasks.append(training(f'{self.dicts_path}/{dictionary}'))

        await asyncio.gather(*tasks)

    def get_training_stats(self):
        mut_prob_fit = {}
        cross_prob_fit = {}
        pop_size_fit = {}
        iterations_fit = {}
        training_set_fit = {}
        dict_size_fit = {}

        for training_result in os.listdir('./train_out/'):
            params = training_result.split('_')

            num_instances = params[0]
            pop_size = params[1]
            elite_count = params[2]
            iterations = params[3]
            cross_prob = params[4]
            mut_prob = params[5]

            for dict_size in os.listdir(f'./train_out/{training_result}'):
                with open(f'./train_out/{training_result}/{dict_size}/best.txt') as file:
                    content = file.readlines()
                    best_fitness = 99999999.0

                    for result in content:
                        fitness = float(result[result.index(':')+1 : result.index('\n')])
                        if fitness < best_fitness:
                            best_fitness = fitness

                    mut_prob_fit[mut_prob] = best_fitness
                    cross_prob_fit[cross_prob] = best_fitness
                    pop_size_fit[pop_size] = best_fitness
                    iterations_fit[iterations] = best_fitness
                    training_set_fit[num_instances] = best_fitness
                    dict_size_fit[dict_size] = best_fitness

        best = lambda x: min(x, key=x.get)
        with open('./resultado_treino.txt', 'w+') as file:
            file.write(f'Melhor valor mutação: {best(mut_prob_fit)} -> Fitness: {mut_prob_fit[best(mut_prob_fit)]}\n')
            file.write(f'Melhor valor crossover: {best(cross_prob_fit)} -> Fitness: {cross_prob_fit[best(cross_prob_fit)]}\n')
            file.write(f'Melhor valor pop_size: {best(pop_size_fit)} -> Fitness: {pop_size_fit[best(pop_size_fit)]}\n')
            file.write(f'Melhor valor iterações: {best(iterations_fit)} -> Fitness: {iterations_fit[best(iterations_fit)]}\n')
            file.write(f'Melhor valor training_set: {best(training_set_fit)} -> Fitness: {training_set_fit[best(training_set_fit)]}\n')
            file.write(f'Melhor valor dict_size: {best(dict_size_fit)} -> Fitness: {dict_size_fit[best(dict_size_fit)]}\n')

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
    import time

    # Wordle word list size is ~2.3k
    tester = Tester(sizes=[200, 500, 1000, 2000], cpp_source_path='./cpp/wordle_main.cpp')
    tester.get_training_stats()
    return

    tester.populate_test_folder('./test_dicts')

    async_queue = []
    for mut_prob in [0.2, 0.3, 0.4, 0.5]:
        for pop_size in [50, 100, 150, 200, 300]:
            for iterations in [50, 70, 100, 200]:
                for cross_prob in [0.6, 0.8, 0.9]:
                    for training_set in [1, 3, 5]:
                        async_queue.append(tester.execute_training(training_set, pop_size, 1, iterations, cross_prob, mut_prob, clear_folder=False))
                        if len(async_queue) == 20:
                            await asyncio.gather(*async_queue)
                        else:
                            continue
                        async_queue.clear()


if __name__ == '__main__':
    asyncio.run(main())
    #wordle_perform_tests(1000)

