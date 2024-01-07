#ifndef __LEXER__H__
#define __LEXER__H__

#include <string>
#include <vector>
#include "inputbuf.h"

typedef enum {
	END_OF_FILE = 0,
	PUBLIC,
	PRIVATE,
	EQUAL,
	COLON, 
	COMMA, 
	SEMICOLON,
	LBRACE, 
	RBRACE, 
	ID, 
	ERROR
} TokenType;

class Token {
public:
	void Print();
	std::string lexeme;
	TokenType token_type;
	int line_no;
};

class LexicalAnalyzer {
public:
	Token GetToken();
	TokenType UngetToken(Token);
	LexicalAnalyzer();
private:
	std::vector<Token> tokens;
	int line_no;
	Token tmp;
	InputBuffer input;
	void SkipSpace();
	bool IsAccessSpecifier(std::string);
	TokenType FindAccessSpecifierIdx(std::string);
	Token ScanIdOrAccessSpecifier();
};
#endif