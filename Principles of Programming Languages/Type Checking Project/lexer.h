/*
 * Copyright (C) Rida Bazzi, 2016
 *
 * Do not share this file with anyone
 */
#ifndef __LEXER__H__
#define __LEXER__H__

#include <vector>
#include <string>

#include "inputbuf.h"

// ------- token types -------------------

typedef enum {
  END_OF_FILE,    // 0
  INT,
  REAL,
  BOO,
  TR,
  FA,           // 5
  IF,
  WHILE,
  SWITCH,
  CASE,
  PUBLIC,       //10
  PRIVATE,
  NUM,
  REALNUM,
  NOT,
  PLUS,         //15
  MINUS,
  MULT,
  DIV,
  GTEQ,
  GREATER,      // 20
  LTEQ,
  NOTEQUAL,
  LESS,
  LPAREN,
  RPAREN,     // 25
  EQUAL, 
  COLON, 
  COMMA, 
  SEMICOLON, 
  LBRACE,     // 30
  RBRACE, 
  ID, 
  ERROR     // 33
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

    bool SkipSpace();
    bool SkipComments();
    bool IsKeyword(std::string);
    TokenType FindKeywordIndex(std::string);
    Token ScanIdOrKeyword();
    Token ScanNumber();
};
void update_Types(int LHS, int RHS);
void addList(std::string n, int lN, int t);
//void printList(void);
int Search_List(std::string n);



#endif  //__LEXER__H__
