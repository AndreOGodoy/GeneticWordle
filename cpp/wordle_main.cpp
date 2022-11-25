#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <vector>
#include <string>
#include <fstream>
#include <sstream>
#include <inttypes.h>
#include <algorithm>
#include <unordered_map>

using namespace std;

// RANDOM

uint64_t random_u64()
{
    static uint64_t seed = time(NULL); 
    seed ^= seed >> 12;
    seed ^= seed << 25;
    seed ^= seed >> 27;
    seed = seed * 0x2545F4914F6CDD1DULL;
    return seed;
}

float dist_uniform(float start = 0.f, float end = 1.f)
{
    return start + ((float)random_u64() / (float)(0xFFFFFFFFFFFFFFFF)) * (end - start);
}

// WORDLE
vector<string> wordle_words;

vector<string> read_word_list_file(const char* file_path)
{
    vector<string> result;

    ifstream infile(file_path);
    string line;
    while(getline(infile, line))
    {
        result.push_back(line);
    }
    
    return result;
}

struct WordleInstance
{
    vector<string>* word_list = nullptr;
    int secret = -1;

    string get_word(int index) const
    {
        return (*word_list)[index];
    }
};

WordleInstance generate_wordle_instance(vector<string>* word_list)
{
    WordleInstance result;
    result.word_list = word_list;
    result.secret = (int)dist_uniform(0, (float)word_list->size());
    return result;
}

vector<WordleInstance> generate_training_set(vector<string>* word_list, int count)
{
    vector<WordleInstance> result;
    for(int i = 0; i < count; i++)
    {
        result.push_back(generate_wordle_instance(word_list));
    }
    return result;
}

string evaluate_guess(const string& guess, const string& secret)
{
    string result = "-----";
    for(int i = 0; i < guess.size(); i++)
    {
        if(guess[i] == secret[i])
        {
            result[i] = 'G';
        }
        else
        {
            for(int j = 0; j < guess.size(); j++)
            {
                if(secret[j] == guess[i])
                {
                    result[i] = 'Y';
                    break;
                }
            }
        }
    }
    return result;
}

// GREEDY

vector<unordered_map<char, float>> green_letter_distribution(const vector<string>& word_list)
{
    vector<unordered_map<char, float>> result = vector<unordered_map<char, float>>(5);
    for(int i = 0; i < word_list.size(); i++)
    {
        string word = word_list[i];
        for(int j = 0; j < word.size(); j++)
        {
            char key = word[j];
            result[j][key] += 1.f;
        }
    }

    for(int i = 0; i < 5; i++)
    {
        for(auto& it: result[i])
        {
            it.second /= word_list.size();
        }
    }
    return result;
}

float green_letter_prob(const string& word, vector<unordered_map<char, float>>& gld)
{
    float result = 0;
    for(int i = 0; i < word.size(); i++)
    {
        result += gld[i][word[i]];
    }
    return result;
}

int get_best_glp(const vector<string>& word_list, const vector<string>& past_guesses)
{
    int result = 0;
    float best_glp = 0.f;
    auto gld = green_letter_distribution(word_list);
    for(int i = 0; i < word_list.size(); i++)
    {
        float glp = green_letter_prob(word_list[i], gld);
        if(result == 0 || glp > best_glp)
        {
            bool found = false;
            for(int j = 0; j < past_guesses.size(); j++)
            {
                if(past_guesses[j] == word_list[i])
                {
                    found = true;
                    break;
                }
            }
            if(!found)
            {
                result = i;
                best_glp = glp;
            }
        }
    }
    return result;
}

vector<char> letters_to_remove(const string& guess, const string& eval)
{
    vector<char> result;
    for(int i = 0; i < guess.size(); i++)
    {
        if(eval[i] == '-')
        {
            bool found = false;
            for(int j = 0; j < result.size(); j++)
            {
                if(result[j] == guess[i])
                {
                    found = true;
                    break;
                }
            }
            if(!found) result.push_back(guess[i]);
        }
    }
    return result;
}

void remove_letters_from_word_list(vector<string>& word_list, const vector<char>& unwanted)
{
    for(int i = word_list.size() - 1; i >= 0; i--)
    {
        string word = word_list[i];
        bool remove_word = false;
        for(int j = 0; j < word.size(); j++)
        {
            char c = word[j];
            for(int k = 0; k < unwanted.size(); k++)
            {
                if(unwanted[k] == c)
                {
                    remove_word = true;
                    break;
                }
            }
            if(remove_word) break;
        }
        if(remove_word)
        {
            word_list.erase(word_list.begin() + i);
        }
    }
}

int solve_wordle_greedy(const WordleInstance& instance)
{
    int result = 0;
    vector<string> past_guesses;
    vector<string> word_list = *instance.word_list;
    while(true)
    {
        int guess = get_best_glp(word_list, past_guesses);
        past_guesses.push_back(word_list[guess]);
        string guess_word = word_list[guess];
        // printf("[GREEDY] Guessing word %s...\n", guess_word.c_str());

        result++;

        string eval = evaluate_guess(guess_word, instance.get_word(instance.secret));
        if(eval == string("GGGGG")) return result;

        auto unwanted = letters_to_remove(guess_word, eval);
        remove_letters_from_word_list(word_list, unwanted);
    }
    
    return result;
}

// GENETIC

struct WordleCurrentInfo
{
    string current_result = "-----";
    vector<char> yellow_letters;
    vector<char> gray_letters;
    vector<int> past_guesses;
};

float expected_green(const string& word, const WordleCurrentInfo& info)
{
    float result = 0.f;
    for(int i = 0; i < word.size(); i++)
    {
        if(word[i] == info.current_result[i]) result += 1.f;
    }
    return result / (float)word.size();
}

float expected_yellow(const string& word, const WordleCurrentInfo& info)
{
    float result = 0.f;
    for(int i = 0; i < word.size(); i++)
    {
        for(int j = 0; j < info.yellow_letters.size(); j++)
        {
            if(word[i] == info.yellow_letters[j])
            {
                result += 1.f;
                break;
            }
        }
    }
    return result / (float)word.size();
}

float expected_gray(const string& word, const WordleCurrentInfo& info)
{
    float result = 0.f;
    for(int i = 0; i < word.size(); i++)
    {
        bool found = false;
        for(int j = 0; j < info.gray_letters.size(); j++)
        {
            if(word[i] == info.gray_letters[j])
            {
                found = true;
                break;
            }
        }
        if(!found) result += 1.f;
    }
    return result / (float)word.size();
}

float score_word(const string& word, const WordleCurrentInfo& info, const float& w_green, const float& w_yellow, const float& w_gray)
{
    float egreen = expected_green(word, info);
    float eyellow = expected_yellow(word, info);
    float egray = expected_gray(word, info);
    return w_green * egreen + w_yellow * eyellow + w_gray * egray;
}

int select_next_guess(const WordleInstance& instance, const WordleCurrentInfo& info, const float& w_green, const float& w_yellow, const float& w_gray)
{
    int guess_index = 0;
    float best_score = -1.f;
    for(int i = 0; i < instance.word_list->size(); i++)
    {
        string word = instance.get_word(i);
        float score = score_word(word, info, w_green, w_yellow, w_gray);
        if(score > best_score)
        {
            bool found = false;
            for(int j = 0; j < info.past_guesses.size(); j++)
            {
                if(i == info.past_guesses[j])
                {
                    found = true;
                    break;
                }
            }
            if(!found)
            {
                guess_index = i;
                best_score = score;
            }
        }
    }
    return guess_index;
}

bool update_wordle_info(const WordleInstance& instance, const int& guess, WordleCurrentInfo* out_info)
{
    // Updating past guesses
    out_info->past_guesses.push_back(guess);

    string secret_word = instance.get_word(instance.secret);
    string guess_word = instance.get_word(guess);
    string eval = evaluate_guess(guess_word, secret_word);
    bool result = true;
    // Updating discovered result
    {
        for(int i = 0; i < eval.size(); i++)
        {
            if(eval[i] == 'G') out_info->current_result[i] = guess_word[i];
            else result = false;
        }
    }

    // Updating found letters
    {
        for(int i = 0; i < guess_word.size(); i++)
        {
            if(eval[i] == 'Y' || eval[i] == 'G')
            {
                bool found_yellow = false;
                for(int j = 0; j < out_info->yellow_letters.size(); j++)
                {
                    if(guess_word[i] == out_info->yellow_letters[j])
                    {
                        found_yellow = true;
                        break;
                    }
                }
                if(!found_yellow) out_info->yellow_letters.push_back(guess_word[i]);
            }
            else
            {
                bool found_gray = false;
                for(int j = 0; j < out_info->gray_letters.size(); j++)
                {
                    if(guess_word[i] == out_info->gray_letters[j])
                    {
                        found_gray = true;
                        break;
                    }
                }
                if(!found_gray) out_info->gray_letters.push_back(guess_word[i]);
            }
        }
    }

    return result;
}

struct Individual
{
    float w[3];
    float fitness = 0.f;
};

bool compare_fitness(const Individual& a, const Individual& b)
{
    return a.fitness < b.fitness;
}

Individual new_random_individual()
{
    Individual guy;
    guy.w[0] = dist_uniform();
    guy.w[1] = dist_uniform();
    guy.w[2] = dist_uniform();
    return guy;
}

Individual crossover(const Individual& parent_1, const Individual& parent_2)
{
    Individual new_guy;
    int genes_from_first = (int)dist_uniform(0, 3);
    for(int i = 0; i < 3; i++)
    {
        if(genes_from_first)
        {
            new_guy.w[i] = parent_1.w[i];
            genes_from_first--;
        }
        else
        {
            new_guy.w[i] = parent_2.w[i];
        }
    }
    return new_guy;
}

Individual mutate(const Individual& parent)
{
    Individual new_guy = parent;
    int mutation_point = (int)dist_uniform(0, 3);
    new_guy.w[mutation_point] = dist_uniform();
    
    return new_guy;
}

int solve_wordle_genetic(const WordleInstance& instance, const Individual& guy)
{
    // TODO(caio): Continue here. For some reason, wordle solving is taking waaaay too many tries.
    int result = 0;
    WordleCurrentInfo info;
    while(true)
    {
        result++;
        int next_guess = -1;
        bool already_found = true;
        for(int i = 0; i < info.current_result.size(); i++)
        {
            if(info.current_result[i] == '-')
            {
                already_found = false;
                break;
            }
        }
        if(already_found)
        {
            return result;
        }
        else
        {
            next_guess = select_next_guess(instance, info, guy.w[0], guy.w[1], guy.w[2]);
            if(next_guess == instance.secret)
            {
                return result;
            }
        }

        update_wordle_info(instance, next_guess, &info);
    }
    return result;
}

float train_individual(const vector<WordleInstance>& training_instances, const Individual& guy)
{
    float result = 0.f;
    for(int i = 0; i < training_instances.size(); i++)
    {
        const WordleInstance& instance = training_instances[i];
        result += solve_wordle_genetic(instance, guy);
    }
    return result / (float)training_instances.size();
}

vector<Individual> new_random_population(int count)
{
    vector<Individual> result;
    for(int i = 0; i < count; i++)
    {
        result.push_back(new_random_individual());
    }
    return result;
}

void train_population(vector<Individual>* population, const vector<WordleInstance>& training_instances)
{// Calculate fitness
    for(int i = 0; i < population->size(); i++)
    {
        Individual& guy = (*population)[i];
        guy.fitness = train_individual(training_instances, guy);
    }
}

vector<Individual> get_elite(const vector<Individual>& population, int count)
{
    vector<Individual> result = population;
    sort(result.begin(), result.end(), compare_fitness);
    result.resize(count);
    return result;
}

vector<Individual> advance_population(const vector<Individual>& population, const vector<WordleInstance>& training_instances, const int& elite_count, const float& cross_prob, const float& mut_prob)
{
    // Select elite based on fitness
    vector<Individual> next_population = get_elite(population, elite_count);

    // Repopulate
    while(next_population.size() < population.size())
    {
        // TODO(caio): Maybe we should select these guys with fitness roulette
        int selected_guy = (int)dist_uniform(0, population.size());
        Individual guy = population[selected_guy];

        float sample = dist_uniform();
        if(sample < cross_prob)
        {
            Individual other = population[(int)dist_uniform(0, population.size())];
            guy = crossover(guy, other);
        }
        sample = dist_uniform();
        if(sample < mut_prob)
        {
            guy = mutate(guy);
        }

        next_population.push_back(guy);
    }

    return next_population;
}

int print_population_stats(const vector<Individual>& population, const int& index)
{
    float avg = 0.f;
    float best = 0.f;
    int result = 0;
    for(int i = 0; i < population.size(); i++)
    {
        const Individual& guy = population[i];
        avg += guy.fitness;
        if(i == 0 || guy.fitness < best)
        {
            best = guy.fitness;
            result = i;
        }
    }
    avg /= (float)population.size();
    printf("%d,%.4f,%.4f\n", index, best, avg);

    return result;
}

int main(int argc, char** argv)
{
    wordle_words = read_word_list_file(argv[argc-1]);

    if(strcmp(argv[1], "train") == 0)
    {
        // Perform training routine. Returns best individual found at last population.
        int training_set_count = atoi(argv[2]);
        int pop_size = atoi(argv[3]);
        int elite_count = atoi(argv[4]);
        int iterations = atoi(argv[5]);
        float cross_prob = strtof(argv[6], NULL);
        float mut_prob = strtof(argv[7], NULL);

        auto training_set = generate_training_set(&wordle_words, training_set_count);
        auto population = new_random_population(pop_size);
        int result = -1;
        train_population(&population, training_set);
        result = print_population_stats(population, 0);
        for(int i = 0; i < iterations; i++)
        {
            population = advance_population(population, training_set, elite_count, cross_prob, mut_prob);
            train_population(&population, training_set);
            result = print_population_stats(population, i + 1);
        }

        Individual best_guy = population[result];
        printf("RESULT,%.4f,%.4f,%.4f FITNESS:%.4f\n",best_guy.w[0],best_guy.w[1],best_guy.w[2], best_guy.fitness);
    }
    else if(strcmp(argv[1], "test") == 0)
    {
        // Perform comparison routine. Compares performance of given individual against greedy approach. Returns all results in csv format
        int test_count = atoi(argv[2]);
        float w0 = strtof(argv[3], nullptr);
        float w1 = strtof(argv[4], nullptr);
        float w2 = strtof(argv[5], nullptr);

        Individual guy;
        guy.w[0] = w0; guy.w[1] = w1; guy.w[2] = w2;

        auto test_set = generate_training_set(&wordle_words, test_count);

        for(int i = 0; i < test_count; i++)
        {
           int result_greedy = solve_wordle_greedy(test_set[i]); 
           int result_genetic = solve_wordle_genetic(test_set[i], guy);
           printf("%d,%d,%d\n", i, result_greedy, result_genetic);
        }
    }

    return 0;
}
