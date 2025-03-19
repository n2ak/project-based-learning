IDIR=src
CC=gcc
CFLAGS=-I$(IDIR)

ODIR=build
# LDIR =../lib

LIBS=-lm

_DEPS = hash_table.h
_OBJ = main.o hash_table.o 

DEPS = $(patsubst %,$(IDIR)/%,$(_DEPS))
OBJ = $(patsubst %,$(ODIR)/%,$(_OBJ))

# @ to supress make from printing the command
$(ODIR)/%.o: $(IDIR)/%.c $(DEPS)
	@$(CC) -c -o $@ $< $(CFLAGS)

main: $(OBJ)
	@$(CC) -o $@ $^ $(CFLAGS) $(LIBS)
	mv main $(ODIR)/main

.PHONY: clean

clean:
	@rm -f $(ODIR)/*.o $(ODIR)/main