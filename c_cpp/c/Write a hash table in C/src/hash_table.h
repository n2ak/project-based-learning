// #pragma once
#include <stdbool.h>
#include <stdlib.h>

typedef struct
{
    char *key;
    char *value;
} ht_item;

typedef struct
{
    size_t capacity;
    size_t size;
    ht_item **items;
} ht_hash_table;

ht_hash_table *ht_new_hash_table();
void ht_delete_hash_table(ht_hash_table *table);
void ht_insert(ht_hash_table *, const char *key, const char *value);
bool ht_remove(ht_hash_table *, const char *key);
void ht_print_info(ht_hash_table *table);
static void ht_try_resize(ht_hash_table *table);

char *ht_get(ht_hash_table *, const char *key);
void ht_dump(ht_hash_table *);