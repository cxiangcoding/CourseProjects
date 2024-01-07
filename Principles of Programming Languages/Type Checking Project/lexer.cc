/*
 * Copyright (C) Rida Bazzi, 2016
 * Do not share this file with anyone
 */
#include <iostream>
#include <istream>
#include <vector>
#include <string>
#include <cctype>
#include <stdlib.h>
#include <string.h>
#include <algorithm>

#include "lexer.h"
#include "inputbuf.h"

using namespace std;

string reserved[] = { 
    "END_OF_FILE", 
    "INT", 
    "REAL", 
    "BOOL", 
    "TR", 
    "FA", 
    "IF", 
    "WHILE", 
    "SWITCH", 
    "CASE", 
    "PUBLIC", 
    "PRIVATE", 
    "NUM", 
    "REALNUM", 
    "NOT", 
    "PLUS", 
    "MINUS", 
    "MULT", 
    "DIV", 
    "GTEQ", 
    "GREATER", 
    "LTEQ", 
    "NOTEQUAL", 
    "LESS", 
    "LPAREN", 
    "RPAREN", 
    "EQUAL", 
    "COLON", 
    "COMMA", 
    "SEMICOLON", 
    "LBRACE", 
    "RBRACE", 
    "ID", 
    "ERROR"
};

#define KEYWORDS_COUNT 11
string keyword[] = { "int", "real", "bool", "true", "false", "if", "while", "switch", "case", "public", "private" };

LexicalAnalyzer lexer;
Token token, token1;
int enumType;
int enumCount = 4;
int parse_body(void);


struct sTableEntry
{
    string name;
    int lineNo;
    int type;
    bool printed;
    sTableEntry(string name, int lineNo, int type, int printed) : name(name),lineNo(lineNo),type(type), printed(printed) {};
};

struct sTable
{
    sTableEntry* item;
    sTable *prev;
    sTable *next;
    sTable(sTableEntry *item, sTable *prev, sTable *next) : item(item), prev(prev), next(next) {};
};

sTable* symbolTable;
char* lResolve;
char* rResolve;
int line = 0;

void addList(std::string name, int line, int type)
{
    if (symbolTable == NULL)
    {
        sTableEntry* newItem = new sTableEntry(name,token.line_no,type,false);
        sTable* newEntry = new sTable(newItem, nullptr, nullptr);
        symbolTable = newEntry;

    }
    else
    {
        sTable* temp = symbolTable;
        while(temp->next != NULL)
        {
            temp = temp->next;
        }
        sTableEntry* newItem = new sTableEntry(name,token.line_no,type,false);
        sTable* newEntry = new sTable(newItem, temp, nullptr);
        temp->next = newEntry;
    }
}

int Search_List(std::string name)
{
    sTable* temp = symbolTable;
    bool found = false;
    if (symbolTable == NULL)
    {
        //cout<<"duplicate check"<<endl;
        addList(name, token.line_no, enumCount);
        enumCount++;
        return (4);
    }
    else
    {
        while(temp)
        {
            if ( temp->item->name == name )
            {
                return temp->item->type;
            }
            temp = temp->next;
        }
        addList(name,token.line_no,enumCount);
        enumCount++;
        return enumCount-1;
    }
}


void Token::Print()
{
    cout << "{" << this->lexeme << " , "
        << reserved[(int) this->token_type] << " , "
        << this->line_no << "}\n";
}

LexicalAnalyzer::LexicalAnalyzer()
{
    this->line_no = 1;
    tmp.lexeme = "";
    tmp.line_no = 1;
    line = 1;
    tmp.token_type = ERROR;
}

bool LexicalAnalyzer::SkipSpace()
{
    char c;
    bool space_encountered = false;

    input.GetChar(c);
    line_no += (c == '\n');
    line = line_no;

    while (!input.EndOfInput() && isspace(c))
    {
        space_encountered = true;
        input.GetChar(c);
        line_no += (c == '\n');
        line = line_no;
    }

    if (!input.EndOfInput())
    {
        input.UngetChar(c);
    }
    return space_encountered;
}

bool LexicalAnalyzer::SkipComments()
{
    bool comments = false;
    char c;
    if(input.EndOfInput() )
    {
        input.UngetChar(c);
        return comments;
    }

    input.GetChar(c);

    if(c == '/')
    {
        input.GetChar(c);
        if(c == '/')
        {
            comments = true;
            while(c != '\n')
            {
                comments = true;
                input.GetChar(c);
            }
            line_no++;
            line = line_no;
            SkipComments();
        }
        else
        {
            comments = false;
            cout << "Syntax Error\n";
            exit(0);
        }
    }
    else
    {
        input.UngetChar(c);
    }
    return comments;
}

bool LexicalAnalyzer::IsKeyword(string s)
{
    for (int i = 0; i < KEYWORDS_COUNT; i++)
    {
        if (s == keyword[i])
        {
            return true;
        }
    }
    return false;
}

TokenType LexicalAnalyzer::FindKeywordIndex(string s)
{
    for (int i = 0; i < KEYWORDS_COUNT; i++)
    {
        if (s == keyword[i])
        {
            return (TokenType) (i + 1);
        }
    }
    return ERROR;
}

Token LexicalAnalyzer::ScanNumber()
{
    char c;
    bool realNUM = false;
    input.GetChar(c);
    if (isdigit(c))
    {
        if (c == '0')
        {
            tmp.lexeme = "0";
            input.GetChar(c);
            if(c == '.')
            {            
                input.GetChar(c);

                if(!isdigit(c))
                {
                    input.UngetChar(c);
                }
                else
                {
                    while (!input.EndOfInput() && isdigit(c))
                    {
                        tmp.lexeme += c;
                        input.GetChar(c);
                        realNUM = true;
                    }
                    input.UngetChar(c);
                }
            }
            else
            {
                input.UngetChar(c);
            }
        }
        else
        {
            tmp.lexeme = "";
            while (!input.EndOfInput() && isdigit(c))
            {
                tmp.lexeme += c;
                input.GetChar(c);
            }
            if(c == '.')
            {               
                input.GetChar(c);

                if(!isdigit(c))
                {
                    input.UngetChar(c);
                }
                else
                {
                    while (!input.EndOfInput() && isdigit(c))
                    {
                        tmp.lexeme += c;
                        input.GetChar(c);
                        realNUM = true;
                    }
                }
            }
            if (!input.EndOfInput())
            {
                input.UngetChar(c);
            }
        }
        // TODO: You can check for REALNUM, BASE08NUM and BASE16NUM here!
        if(realNUM)
        {
            tmp.token_type = REALNUM;
        }
        else
        {
            tmp.token_type = NUM;
        }
        tmp.line_no = line_no;
        return tmp;
    }
    else
    {
        if (!input.EndOfInput())
        {
            input.UngetChar(c);
        }
        tmp.lexeme = "";
        tmp.token_type = ERROR;
        tmp.line_no = line_no;
        return tmp;
    }
}

Token LexicalAnalyzer::ScanIdOrKeyword()
{
    char c;
    input.GetChar(c);

    if (isalpha(c))
    {
        tmp.lexeme = "";
        while (!input.EndOfInput() && isalnum(c))
        {
            tmp.lexeme += c;
            input.GetChar(c);
        }
        if (!input.EndOfInput())
        {
            input.UngetChar(c);
        }
        tmp.line_no = line_no;

        if (IsKeyword(tmp.lexeme))
        {
             tmp.token_type = FindKeywordIndex(tmp.lexeme);
        }
        else
        {
            tmp.token_type = ID;
        }
    }
    else
    {
        if (!input.EndOfInput())
        {
            input.UngetChar(c);
        }
        tmp.lexeme = "";
        tmp.token_type = ERROR;
    }
    return tmp;
}

TokenType LexicalAnalyzer::UngetToken(Token tok)
{
    tokens.push_back(tok);;
    return tok.token_type;
}

Token LexicalAnalyzer::GetToken()
{
    char c;
    if (!tokens.empty())
    {
        tmp = tokens.back();
        tokens.pop_back();
        return tmp;
    }

    SkipSpace();
    SkipComments();
    SkipSpace();
    tmp.lexeme = "";
    tmp.line_no = line_no;
    input.GetChar(c);
    switch (c)
    {
        case '!':
            tmp.token_type = NOT;
            return tmp;
        case '+':
            tmp.token_type = PLUS;
            return tmp;
        case '-':
            tmp.token_type = MINUS;
            return tmp;
        case '*':
            tmp.token_type = MULT;
            return tmp;
        case '/':
            tmp.token_type = DIV;
            return tmp;
        case '>':
            input.GetChar(c);
            if(c == '=')
            {
                tmp.token_type = GTEQ;
            }
            else
            {
                input.UngetChar(c);
                tmp.token_type = GREATER;
            }
            return tmp;
        case '<':
            input.GetChar(c);
            if(c == '=')
            {
                tmp.token_type = LTEQ;
            }
            else if (c == '>')
            {
                tmp.token_type = NOTEQUAL;
            }
            else
            {
                input.UngetChar(c);
                tmp.token_type = LESS;
            }
            return tmp;
        case '(':
            //cout << "\n I am here" << c << " \n";
            tmp.token_type = LPAREN;
            return tmp;
        case ')':
            tmp.token_type = RPAREN;
            return tmp;
        case '=':
            tmp.token_type = EQUAL;
            return tmp;
        case ':':
            tmp.token_type = COLON;
            return tmp;
        case ',':
            tmp.token_type = COMMA;
            return tmp;
        case ';':
            tmp.token_type = SEMICOLON;
            return tmp;
        case '{':
            tmp.token_type = LBRACE;
            return tmp;
        case '}':
            tmp.token_type = RBRACE;
            return tmp;
        default:
            if (isdigit(c))
            {
                input.UngetChar(c);
                return ScanNumber();
            }
            else if (isalpha(c))
            {
                input.UngetChar(c);
                //cout << "\n ID scan " << c << " \n";
                return ScanIdOrKeyword();
            }
            else if (input.EndOfInput())
            {
                tmp.token_type = END_OF_FILE;
            }
            else
            {
                tmp.token_type = ERROR;
            }
            return tmp;
    }
}

void  parse_varlist(void)
{
    token = lexer.GetToken();
    addList(token.lexeme, token.line_no, 0);
    if (token.token_type == ID)
    {
        token = lexer.GetToken();
        if(token.token_type == COMMA)
        {
            parse_varlist();
        }
        else if(token.token_type == COLON)
        {
            lexer.UngetToken(token);
        }
        else
        {
            cout << "\n Syntax Error \n";
        }
    }
    else
    {
        cout << "\n Syntax Error \n";
    }
}

// return 1 if it's valid unary operator 
int parse_unaryOperator(void)
{
    token = lexer.GetToken();
    if (token.token_type == NOT) {
        return(1);
    } else {
        cout << "\n Syntax Error\n";
        return(0);
    }
}

TokenType parse_binaryOperator(void)
{
    token = lexer.GetToken();
    return token.token_type;
}

int parse_primary(void)
{
    token = lexer.GetToken();
    if ( token.token_type == ID ) {
        return(Search_List(token.lexeme));
        //cout << "\n Rule parsed: primary -> ID\n";
    } else if ( token.token_type == NUM ) {
        return 1;
    } else if ( token.token_type == REALNUM) {
        return 2;
    } else if ( token.token_type == TR ) {
        return 3;
    } else if ( token.token_type == FA ) {
        return 3;
    } else {
        cout << "\n Syntax Error \n";
        return(0);
    }
}


bool isEpr(TokenType op){
    return  (op >= PLUS && op <= LESS) || (op == EQUAL);
}

bool isExpress(int op){
    return !(op >= PLUS && op <= LESS) && (op != EQUAL); 
}

int parse_expression(void)
{
    //check for C2 error here
    int ret;
    token = lexer.GetToken();
    if(token.token_type == ID || token.token_type == NUM || token.token_type == REALNUM || token.token_type == TR || token.token_type == FA )
    {
        //cout << "\n Rule parsed: expression -> primary \n";
        lexer.UngetToken(token);
        ret = parse_primary();
    } else if (isEpr(token.token_type))
    {
        //cout << "\n Rule parsed: expression -> binary_operator expression expression \n";
        int leftExp, rightExp;
        lexer.UngetToken(token);
        ret = parse_binaryOperator(); 
        leftExp = parse_expression();
        rightExp = parse_expression();     
        if((leftExp != rightExp) || isExpress(ret))
        {
            if ( ret >= PLUS && ret <= DIV )
            {
                if (leftExp <= REAL && rightExp > BOO) {
                    update_Types(rightExp, leftExp);
                    rightExp = leftExp;
                } else if (leftExp > BOO && rightExp <= REAL ) {
                    update_Types(rightExp, leftExp);
                    leftExp = rightExp;
                } else if (leftExp > BOO && rightExp > BOO) {
                    update_Types(rightExp, leftExp);
                    rightExp = leftExp;
                } else {
                    cout << "TYPE MISMATCH " << token.line_no << " C2"<<endl;
                    exit(1);
                }
            } else if ( (ret >= GTEQ && ret <= LESS) || ret == EQUAL ) {
                if (rightExp > BOO && leftExp > BOO ) {
                    update_Types(rightExp, leftExp);
                    rightExp = leftExp;
                    return BOO;
                } else {
                    cout << "TYPE MISMATCH " << token.line_no << " C2"<<endl;
                    exit(1);
                }
            } else {
                cout << "TYPE MISMATCH " << token.line_no << " C2"<<endl;
                exit(1);
            }
        }
        if ((ret >= GTEQ && ret <= LESS) || ret == EQUAL  ) {
            ret = BOO;
        } else  {
            ret = rightExp;
        }
    }
    else if (token.token_type == NOT)
    {
        lexer.UngetToken(token);
        ret = parse_unaryOperator(); // return 0 for error and return 1 for NOT
        ret = parse_expression();
        if(ret != BOO)
        {
            cout << "TYPE MISMATCH " << token.line_no << " C3"<<endl;
            exit(1);
        }
    }
    else
    {
        cout << "\n Syntax Error \n";
        return(0);
    }
    return ret;
}

void update_line_tokentype(int line_No, int token_Type)
{
    sTable *temp = symbolTable;
    while(temp) {
        if ( temp->item->lineNo == line_No )
            temp->item->type = token_Type;
        temp = temp->next;
    }
}

void update_Types(int currentType, int newType)
{
    sTable* temp = symbolTable;
    while( temp )
    {
        if ( temp->item->type == currentType )
            temp->item->type = newType;
        temp = temp->next;
    }
}

bool isExp(TokenType type){
    return type == ID || type == NUM || type == REALNUM || type == TR || type == FA || (type >= NOT && type <= 23) || type == EQUAL;
}

int parse_assstmt(void)
{
    string name;
    int LHS, RHS;
    token = lexer.GetToken();
    if (token.token_type == ID)
    {
        LHS = Search_List(token.lexeme);
        token = lexer.GetToken();
        if(token.token_type == EQUAL)
        {
            token = lexer.GetToken();
            if(isExp(token.token_type))
            {
                lexer.UngetToken(token);
                RHS = parse_expression();
                if(LHS == INT || LHS == REAL || LHS == BOO)
                {
                    if(LHS != RHS)
                    {
                        if (LHS < 3) {
                            cout << "TYPE MISMATCH " << token.line_no << " C1" << endl;
                            exit(1);
                        } else {
                            update_Types(RHS,LHS);
                            RHS = LHS;
                        }
                    }
                } else {
                    update_Types(LHS,RHS);
                    LHS = RHS;
                }
                token = lexer.GetToken();
                if(token.token_type != SEMICOLON)
                {
                    cout << "\n HI Syntax Error " << token.token_type << " \n";
                }
            } else {
                cout << "\n Syntax Error \n";
            }
        } else {
            cout << "\n Syntax Error \n";
        }
    } else {
        cout << "\n Syntax Error \n";
    }
    return(0);
}

void parse_case(void)
{
    token = lexer.GetToken();
    if (token.token_type == CASE )
    {
        token = lexer.GetToken();
        if (token.token_type == NUM)
        {
            token = lexer.GetToken();
            if (token.token_type == COLON)
            {
                //cout << "\n Rule parsed: case -> CASE NUM COLON body";
                parse_body();
            } else {
                cout << "\n Syntax Error \n";
            }
        } else {
            cout << "\n Syntax Error \n";
        }
    } else {
        cout << "\n Syntax Error \n";
    }
}

void parse_caselist(void)
{
    token = lexer.GetToken();
    if (token.token_type == CASE) {
        lexer.UngetToken(token);
        parse_case();
        token = lexer.GetToken();
        if (token.token_type == CASE) {
            lexer.UngetToken(token);
            //cout << "\n Rule parsed: case_list -> case case_list \n";
            parse_caselist();
        } else if(token.token_type == RBRACE) {
            lexer.UngetToken(token);
            //cout << "\n Rule parsed: case_list -> case  \n";
        }
    }
}

int parse_switchstmt(void)
{
    int ret;
    token = lexer.GetToken();
    if (token.token_type == SWITCH) {
        token = lexer.GetToken();
        if (token.token_type == LPAREN) {
            ret = parse_expression();
            if (ret <= BOO && ret != INT) {
                cout<< "TYPE MISMATCH " << token.line_no << " C5"<<endl;
                exit(1);
            }
            token = lexer.GetToken();
            if (token.token_type == RPAREN) {
                token = lexer.GetToken();
                if (token.token_type == LBRACE)
                {
                    parse_caselist();
                    token = lexer.GetToken();
                    if(token.token_type != RBRACE) {
                        cout << "\n Syntax Error \n";
                    }
                } else {
                    cout << "\n Syntax Error \n";
                }
            } else {
                cout << "\n Syntax Error \n";
            }
        } else {
            cout << "\n Syntax Error \n";
        }
    } else {
        cout << "\n Syntax Error \n";
    }
    return(0);
}

int parse_whilestmt(void)
{
    int ret;
    token = lexer.GetToken();
    if (token.token_type == WHILE)
    {
        token = lexer.GetToken();
        if (token.token_type == LPAREN)
        {
            ret = parse_expression();
            if (ret != BOO) {
                cout<< "TYPE MISMATCH " << token.line_no << " C4" << endl;
                exit(1);
            }
            token = lexer.GetToken();
            if (token.token_type == RPAREN) {
                //cout << "\n Rule parsed: whilestmt -> WHILE LPAREN expression RPAREN body \n";
                ret = parse_body();
            } else {
                cout << "\n Syntax Error \n";
            }
        } else {
            cout << "\n Syntax Error \n";
        }
    } else {
        cout << "\n Syntax Error \n";
    }
    return(0);
}

int parse_ifstmt(void)
{
    int ret;
    token = lexer.GetToken();
    if (token.token_type == IF)
    {
        token = lexer.GetToken();
        if (token.token_type == LPAREN) {
            ret = parse_expression();
            if (ret != BOO)
            {
                cout<< "TYPE MISMATCH " << token.line_no << " C4" << endl;
                exit(1);
            }
            token = lexer.GetToken();
            if (token.token_type == RPAREN)
            {
                //cout << "\n Rule parsed: ifstmt -> IF LPAREN expression RPAREN body \n";
                ret = parse_body();
            } else {
                cout << "\n Syntax Error \n";
            }
        }
        else
        {
            cout << "\n Syntax Error \n";
        }
    } else {
        cout << "\n Syntax Error \n";
    }
    return(0);
}

int parse_stmt(void)
{
    int ret;
    token = lexer.GetToken();
    if (token.token_type == ID)
    {
        lexer.UngetToken(token);
        //cout << "\n Rule parsed: stmt -> assignment_stmt \n";
        ret = parse_assstmt();
    } else if(token.token_type == IF) {
        lexer.UngetToken(token);
        //cout << "\n Rule parsed: stmt -> if_stmt";
        ret = parse_ifstmt();
    } else if(token.token_type == WHILE) {
        lexer.UngetToken(token);
        //cout << "\n Rule parsed: stmt -> while_stmt";
        ret = parse_whilestmt();
    } else if(token.token_type == SWITCH) {
        lexer.UngetToken(token);
        //cout << "\n Rule parsed: stmt -> switch_stmt";
        ret = parse_switchstmt();
    } else {
        cout << "\n Syntax Error \n";
    }
    return(0);
}

int parse_stmtlist(void)
{
    token = lexer.GetToken();
    if (token.token_type == ID || token.token_type == IF || token.token_type == WHILE || token.token_type == SWITCH)
    {
        lexer.UngetToken(token);
        parse_stmt();
        token = lexer.GetToken();
        if (token.token_type == ID || token.token_type == IF || token.token_type == WHILE || token.token_type == SWITCH)
        {
            lexer.UngetToken(token);
            //cout << "\n Rule Parsed: stmt_list -> stmt stmt_list \n";
            parse_stmtlist();

        } else if (token.token_type == RBRACE) {
            lexer.UngetToken(token);           
            //cout << "\n Rule parsed: stmt_list -> stmt \n";
        }
    } else {
        cout << "\n Syntax Error \n";
    }
    return(0);
}

int parse_body(void)
{
    token = lexer.GetToken();
    if (token.token_type == LBRACE)
    {
        //cout << "\n Rule Parsed: scope -> ID LBRACE public_vars private_vars stmt_list RBRACE \n";
        parse_stmtlist();
        token = lexer.GetToken();
        if (token.token_type != RBRACE)
        {
            cout << "\n Syntax Error\n ";
            return(0);
        }
        return 0;
    } else if (token.token_type == END_OF_FILE) {
        lexer.UngetToken(token);
        return(0);
    } else {
        cout << "\n Syntax Error \n ";
        return(0);
    }
}

int parse_typename(void)
{
    token = lexer.GetToken();
    if (token.token_type == INT || token.token_type == REAL || token.token_type == BOO) {
        update_line_tokentype(token.line_no, token.token_type);
    } else {
        cout << "\n Syntax Error in parse_typename \n";
    }
    return(0);
}

int parse_vardecl(void)
{
    token = lexer.GetToken();
    if (token.token_type == ID)
    {
        lexer.UngetToken(token);
        parse_varlist();
        token = lexer.GetToken();
        if (token.token_type == COLON)
        {
            parse_typename();
            token = lexer.GetToken();
            if (token.token_type != SEMICOLON)
            {
                cout << "\n Syntax Error \n";
            }
        } else {
            cout << "\n Syntax Error \n";
        }
    } else {
        cout << "\n Syntax Error \n";
    }    
    return(0);
}

int parse_vardecllist(void)
{
    token = lexer.GetToken();
    while (token.token_type == ID)
    {
        lexer.UngetToken(token);
        parse_vardecl();
        token = lexer.GetToken();   
    }
    lexer.UngetToken(token);
    return(0);
}

int parse_globalVars(void)
{
    token = lexer.GetToken();
    if (token.token_type == ID) {
        lexer.UngetToken(token);
        //cout << "\n Rule parsed: globalVars -> var_decl_list \n";
        parse_vardecllist();
    } else {
        cout << "Syntax Error";
    }
    return(0);
}

void parse_program(void)
{
    token = lexer.GetToken();
    while (token.token_type != END_OF_FILE)
    {
        if (token.token_type == ID) {
            lexer.UngetToken(token);
            parse_globalVars();
            parse_body();
        } else if(token.token_type == LBRACE) {
            lexer.UngetToken(token);
            //cout << "\n Rule parsed: global_vars -> epsilon \n";
            parse_body();
        } else if(token.token_type == END_OF_FILE) {
        } else {
            cout << "\n Syntax Error\n";
            exit(1);
        }
        token = lexer.GetToken();
    }
}

string output = "";
void printList(void)
{
    sTable* temp = symbolTable;
    int temp1;

    while (temp->next != NULL)
    {
       if (temp->item->type > 3 && !temp->item->printed) {          
            temp1 = temp->item->type;
            output += temp->item->name;
            temp->item->printed = 1;
            while (temp->next != NULL) {
                temp = temp->next;
                if (temp->item->type == temp1)
                {
                    output += ", " + temp->item->name;
                    temp->item->printed = 1;
                }
            }
            output += ": ? #";
            cout << output <<endl;
            temp->item->printed = 1;
            output = "";
            temp = symbolTable;
        } else if (temp->item->type < 4 && !temp->item->printed ) {
            string type = keyword[(temp->item->type)-1 ];
            temp1 = temp->item->type;
            output = temp->item->name + ": " + type + " #";
            cout << output <<endl;
            output = "";
            temp->item->printed = 1;           

            while(temp->next != NULL  && temp->next->item->type == temp1)
            {
                temp = temp->next;
                string type = keyword[(temp->item->type)-1];
                output = temp->item->name + ": " + type + " #";
                cout << output <<endl;
                temp->item->printed = 1;
                output = "";
            }
        } else {
            temp = temp->next;
        }
    }
    if (temp->item->type <= 3 && temp->item->printed == 0)
    {        
        string type = keyword[(temp->item->type)-1];
        output += temp->item->name + ": " + type + " #";
        cout << output <<endl;
        output = "";
    } else if (temp->item->type > 3 && temp->item->printed == 0)
    {
        output += temp->item->name + ":" + " ? " + "#";
        cout << output <<endl;
        output = "";
    }
}

int main()
{
    parse_program();
    printList();  
}
