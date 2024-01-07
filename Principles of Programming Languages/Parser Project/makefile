CC=g++ -c
FLAGS= -Wall -g
Assignment1: inputbuf.cc inputbuf.h lexer.cc lexer.h parser.cc parser.h parser.o inputbuf.o
	$(CC)  inputbuf.cc parser.cc lexer.cc
	g++ -o a.out parser.o inputbuf.o lexer.o
clean:
	rm *.o
	rm Assignment1.out
