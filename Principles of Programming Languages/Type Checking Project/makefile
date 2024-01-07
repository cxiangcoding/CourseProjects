CC=g++ -c
FLAGS= -Wall -g
Project3: inputbuf.cc inputbuf.h lexer.cc lexer.h inputbuf.o lexer.o
	$(CC) lexer.cc inputbuf.cc -g 
	g++ -o a.out  lexer.o inputbuf.o
clean:
	rm *.o
	rm a.out
