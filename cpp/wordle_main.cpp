#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <vector>
#include <string>
#include <fstream>
#include <sstream>
#include <inttypes.h>

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
        for(int j = 0; j < info.gray_letters.size(); j++)
        {
            if(word[i] == info.gray_letters[j])
            {
                result += 1.f;
                break;
            }
        }
    }
    return result / (float)word.size();
}

float score_word(const string& word, const string& secret, const WordleCurrentInfo& info, const float& w_green, const float& w_yellow, const float& w_gray)
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
        float score = score_word(word, instance.get_word(instance.secret), info, w_green, w_yellow, w_gray);
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

void update_wordle_info(const WordleInstance& instance, const int& guess, WordleCurrentInfo* out_info)
{
    // Updating past guesses
    out_info->past_guesses.push_back(guess);

    string secret_word = instance.get_word(instance.secret);
    string guess_word = instance.get_word(guess);
    string eval = evaluate_guess(guess_word, secret_word);
    // Updating discovered result
    {
        for(int i = 0; i < eval.size(); i++)
        {
            if(eval[i] == 'G') out_info->current_result[i] = guess_word[i];
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
}

// GENETIC

struct Individual
{
    float w[3];
};

Individual new_random_individual()
{
    Individual guy;
    guy.w[0] = dist_uniform(0.f, 1.f);
    guy.w[1] = dist_uniform(0.f, 1.f - guy.w[0]);
    guy.w[2] = 1.f - guy.w[0] - guy.w[1];
    return guy;
}

int solve_wordle(const WordleInstance& instance, const Individual& guy)
{
    int result = 0;
    WordleCurrentInfo info;
    while(true)
    {
        result++;
        int next_guess = select_next_guess(instance, info, guy.w[0], guy.w[1], guy.w[2]);
        string eval = evaluate_guess(instance.get_word(next_guess), instance.get_word(instance.secret));
        if(eval == string("GGGGG")) return result;

        update_wordle_info(instance, next_guess, &info);
    }
    return result;
}

float train(const vector<WordleInstance>& training_instances, const Individual& guy)
{
    float result = 0.f;
    for(int i = 0; i < training_instances.size(); i++)
    {
        const WordleInstance& instance = training_instances[i];
        result += solve_wordle(instance, guy);
    }
    return result / (float)training_instances.size();
}

int main(int argc, char** argv)
{
    wordle_words = read_word_list_file("../wordle_words.txt");

    auto training_set = generate_training_set(&wordle_words, 100);

    Individual guy = new_random_individual();
    printf("Individual green %.4f, yellow %.4f, gray %.4f\n", guy.w[0], guy.w[1], guy.w[2]);

    float guy_result = train(training_set, guy);
    printf("Individual finished training, average result: %.4f\n", guy_result);

    return 0;
}
