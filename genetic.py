from typing import List
from dataclasses import dataclass, field
from util import *
from random import random, randint
import heapq

def generate_random_gene():
    return [random(), random(), random()]

# Maybe inside Population?
MUT_PROB = 0.5 
CROSS_PROB = 0.5

POP_SIZE = 1000
ELITISM = 10 # Quantos passarão diretamente para a próxima geração

@dataclass
class Individual:
    fitness: float
    gene: List[float] = field(default_factory=generate_random_gene)
    
    def green_weigth(self):
        return self.gene[0]

    def yellow_weigth(self):
        return self.gene[1]

    def gray_weigth(self):
        return self.gene[2]

    def mutate(self) -> 'Individual':
        new_gene = self.gene.copy()
        mutation_point = randint(0, len(self.gene)-1)

        new_gene[mutation_point] = random()
        return Individual(gene=new_gene)

    def crossover(self, other: 'Individual') -> 'Individual':
        new_gene = [0] * len(self.gene)
        
        for gene_pos in range(len(self.gene)):
            new_gene[gene_pos] = self.gene[gene_pos] if random() < 0.5 else other.gene[gene_pos]

        new_individual = Individual(gene=new_gene)
        if random() < MUT_PROB:
            new_individual = self.mutate(new_individual)

        return new_individual

    def self_reproduce(self) -> 'Individual':
        new_individual = Individual(gene=self.gene.copy())

        if random() < MUT_PROB:
            new_individual = self.mutate(new_individual)
        
        return new_individual

class Population:
    size: int
    individuals: List[Individual]

    def __init__(self, size: int):
        for _ in range(size):
            individual = Individual()
            self.individuals.push(Individual())
        
    def _update_fitness(self, ind: Individual, word, problem_info):
        ind.fitness = genetic_word_score(word, problem_info, ind.green_weigth(), ind.yellow_weigth(), ind.gray_weigth())
        return ind

    def advance(self, word, problem_info):
        fit_func = lambda ind: self._update_fitness(ind, word, problem_info)
        self.individuals = list(map(fit_func, self.individuals))

        best_n = heapq.nlargest(ELITISM, self.individuals)
        self.best = best_n[0]

        new_individuals = best_n.copy()

        while len(new_individuals) < POP_SIZE:
            a = self.individuals[randint(0, len(self.individuals)-1)]
            if CROSS_PROB:
                b = None 
                while b is None or b == a: 
                    b = self.individuals[randint(0, len(self.individuals)-1)]

                new_ind = a.crossover(b)
                new_individuals.append(new_ind)
            else:
                new_ind = a.self_reproduce()
                new_individuals.append(new_ind)
            
        assert len(new_individuals) == POP_SIZE

        self.individuals = new_individuals

    def get_best(self):
        if not self.best:
            return # Or raise error?

        return self.best

# Genetic algorithm heuristic and related functions
def genetic_word_score(word, problem_info, w_egreen_correctness = 1, w_eyellow_correctness = 1, w_egray_correctness = 1):
    egreen = get_expected_green_correctness(word, problem_info)
    eyellow = get_expected_yellow_correctness(word, problem_info)
    egray = get_expected_gray_correctness(word, problem_info)
    return egreen * w_egreen_correctness + eyellow * w_eyellow_correctness + egray * w_egray_correctness

def genetic_select_next_guess(word_list, problem_info, past_guesses, w_egreen_correctness = 1, w_eyellow_correctness = 1, w_egray_correctness = 1):
    words_by_score = sorted(word_list, key=lambda word: genetic_word_score(word, problem_info), reverse=True)
    for i in range(len(words_by_score)):
            if words_by_score[i] not in past_guesses:
                return words_by_score[i]
    return ''   # Shouldn't happen

def solve_wordle_genetic(words, secret):
    guesses = 0
    past_guesses = []
    info = WordleInfo()

    while True:
        # Choose word
        # TODO: Currently only performs a greedy seach on expected score metrics. Genetic part still unimplemented.
        guess = genetic_select_next_guess(words, info, past_guesses, 1, 1, 1)
        print(f'[GENETIC] Guessing: {guess}...')
        guesses += 1

        # Evaluate guess
        guess_result, is_correct = evaluate_guess(guess, secret)
        if is_correct:
            return guesses
        else:
            # Update problem info for next iteration
            past_guesses += [guess]
            info = update_obtained_info(guess, guess_result, info)
