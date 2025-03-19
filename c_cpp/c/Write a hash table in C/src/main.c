#include <stdio.h>
#include "hash_table.h"
#include <time.h>
char *rand_word(int min_len, int max_len)
{
    int i, length;
    char c;

    // seed random
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    /* using nano-seconds instead of seconds */
    srand((time_t)ts.tv_nsec);

    length = rand() % (max_len - min_len + 1) + min_len;
    char *word = calloc((size_t)(length + 1), sizeof(char));

    for (i = 0; i < length; i++)
    {
        c = 'a' + rand() % 26;
        word[i] = c;
    }
    word[i] = 0;

    return word;
}

void test2(ht_hash_table *table)
{
#define N 30
    for (size_t i = 0; i < N; i++)
    {
        char *key = rand_word(10, 15);
        ht_insert(table, key, key);
    }
    // ht_dump(table);
    for (size_t i = 0; i < N; i++)
    {
        char *key = rand_word(10, 15);
        char *v = ht_get(table, key);
        // printf("%s       :        %s\n", key, v);
    }
    // ht_dump(table);
    for (size_t i = 0; i < N; i++)
    {
        char *key = rand_word(10, 15);
        bool removed = ht_remove(table, key);
        // printf("key '%s' removed : %d\n", key, removed);
    }
    // ht_dump(table);
    puts("Done");
    ht_print_info(table);
}
void test1(ht_hash_table *table)
{
    ht_insert(table, "Hello", "World");
    ht_dump(table);
    ht_insert(table, "Hello", "No value");
    ht_dump(table);
    char *res1 = ht_get(table, "Hello");
    printf("res1: %s\n", res1);
    ht_remove(table, "Hello");
    ht_dump(table);
    char *res2 = ht_get(table, "Hello");
    printf("res2: %s\n", res2);
    ht_dump(table);
}
int main()
{
    ht_hash_table *table = ht_new_hash_table();
    test2(table);
    ht_delete_hash_table(table);
}