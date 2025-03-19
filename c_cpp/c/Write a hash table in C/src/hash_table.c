#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <math.h>
#include "hash_table.h"

// static int PRIME_1 = 131;
// static int PRIME_2 = 137;
static int PRIME_1 = 151;
static int PRIME_2 = 163;
static ht_item *ht_new_item(const char *key, const char *value)
{
    ht_item *item = malloc(sizeof(ht_item));

    item->key = strdup(key);
    item->value = strdup(value);
    return item;
}
ht_hash_table *ht_new_hash_table()
{
    ht_hash_table *table = malloc(sizeof(ht_hash_table));
    table->capacity = 53;
    table->size = 0;
    table->items = calloc(table->capacity, sizeof(ht_item *));
    return table;
}
static void ht_delete_item(ht_item *item)
{
    if (item == NULL)
        return;
    free(item->key);
    free(item->value);
    free(item);
}
void ht_delete_hash_table(ht_hash_table *table)
{
    for (size_t i = 0; i < table->capacity; i++)
    {
        ht_item *item = table->items[i];
        ht_delete_item(item);
    }
    free(table);
}
static size_t hash(const char *s, size_t num_buckets, int a)
{
    // a: prime number > 128 (n chars)
    long long h = 0;
    size_t len = strlen(s);
    for (size_t i = 0; i < len; i++)
    {
        h += (long long)pow(a, (len - (i + 1))) * (long long)s[i];
    }
    h = h % num_buckets;
    return (size_t)h;
}
int is_prime(const int x)
{
    if (x < 2)
        return -1;
    if (x < 4)
        return 1;
    if ((x % 2) == 0)
        return 0;
    for (int i = 3; i <= floor(sqrt((double)x)); i += 2)
        if ((x % i) == 0)
            return 0;
    return 1;
}
int next_prime(int x)
{
    while (is_prime(x) != 1)
        x++;
    return x;
}
static size_t ht_get_hash(const char *s, size_t num_buckets, int attempt)
{
    size_t h1 = hash(s, num_buckets, PRIME_1);
    size_t h2 = hash(s, num_buckets, PRIME_2);
    size_t index = h1 + attempt * (h2 + 1);
    index = index % num_buckets;
    // printf("s: '%s' ==> h1: %zu h2: %zu ==> index: %zu\n", s, h1, h2, index);
    return index;
}

void ht_insert(ht_hash_table *table, const char *key, const char *value)
{
    ht_try_resize(table);
    int collisions = 0;
    size_t index = ht_get_hash(key, table->capacity, collisions);
    ht_item *item = table->items[index];
    while (item != NULL)
    {
        if (strcmp(item->key, key) == 0)
        {
            // update
            item->value = strdup(value);
            return;
        }
        index = ht_get_hash(key, table->capacity, ++collisions);
        // keep going untill we find a null (free spot).
        item = table->items[index];
        // if (item != NULL)
        //     printf("key: '%s' ,collisions: %d coll value: '%s' %p\n",
        //            key, collisions, item->value, item);
    }
    table->items[index] = ht_new_item(key, value);
    table->size++;
}
void ht_dump(ht_hash_table *table)
{
    puts("================");
    ht_print_info(table);
    for (size_t i = 0; i < table->capacity; i++)
    {
        ht_item *item = table->items[i];
        // printf("%d\n", (int)i);
        if (item != NULL)
        {
            printf("    at %d => '%s': '%s',\n", (int)i, item->key, item->value);
        }
    }
    puts("================");
}
static int ht_get_item_index(ht_hash_table *table, const char *key)
{
    int collisions = 0;
    size_t index = ht_get_hash(key, table->capacity, collisions);
    ht_item *item = table->items[index];
    while (item != NULL)
    {
        if (strcmp(item->key, key) == 0)
            return (int)index;
        index = ht_get_hash(key, table->capacity, ++collisions);
        item = table->items[index];
    }
    return -1;
}
bool ht_remove(ht_hash_table *table, const char *key)
{
    int index = ht_get_item_index(table, key);
    if (index != -1)
    {
        ht_delete_item(table->items[index]);
        table->items[index] = NULL;
        table->size--;
        return true;
    }
    return false;
}
char *ht_get(ht_hash_table *table, const char *key)
{
    int index = ht_get_item_index(table, key);
    if (index == -1)
        return NULL;
    return table->items[index]->value;
}
void ht_print_info(ht_hash_table *table)
{
    printf("Capacity %d, size: %d, %.3f%%\n",
           (int)table->capacity,
           (int)table->size,
           ((float)table->size / table->capacity) * 100);
}
static void ht_reduce_size(ht_hash_table *table)
{
    // ht_print_info();

    // ht_print_info();
}
#define INC 0.7
static void ht_increase_size(ht_hash_table *table)
{
    ht_print_info(table);
    size_t increase = (size_t)(INC * table->capacity);
    size_t new_capacity = next_prime(table->capacity + increase);
    ht_item **old_list = table->items;
    ht_item **new_list = calloc(new_capacity, sizeof(ht_item *));
    memcpy(new_list, old_list, table->capacity * sizeof(ht_item *));
    free(table->items);
    table->items = new_list;
    table->capacity = new_capacity;
    ht_print_info(table);
}
static void ht_try_resize(ht_hash_table *table)
{
    float perc = ((float)table->size / table->capacity);
    // printf("perc %f\n", perc * 100);
    if (perc < .1)
        // reduce capacity
        ht_reduce_size(table);
    else if (perc > .7)
        // increase capacity
        ht_increase_size(table);
}