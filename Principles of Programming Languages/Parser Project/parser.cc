#include <iostream>
#include <istream>
#include <vector>
#include <string>
#include <cctype>
#include "stdlib.h"
#include "inputbuf.h"
#include "parser.h"
#include "lexer.h"

using namespace std;


SymbolTable::SymbolTable()
{
    current = new scopeTable;
    pointer = current;
}

void SymbolTable::addScope(string scope)
{
    pointer = current;
    scopeTable* n = new scopeTable();
    n->scope = scope;
    n->previous = pointer;
    pointer = n;
    current = pointer;
}

void SymbolTable::exitScope()
{
    pointer = current = current->previous;
}

void SymbolTable::addVariable(string var, AccessSpecifier access)
{
    pointer = current;
    symbolEntry n = symbolEntry();
    n.variable = var;
    n.access = access;
    pointer->symbols.push_back(n);
}

symbolEntry SymbolTable::searchVariable(string var)
{
    pointer = current;
    symbolEntry n = symbolEntry();
    while (pointer != NULL) {
        for (auto it = pointer->symbols.begin(); it != pointer->symbols.end(); ++it)
        {
            if (it->variable == var) {
                n.variable = it->variable;
                n.access = it->access;
                n.scope = pointer->scope;
                if (it->access == PRIVATE_ACCESS) {
                    if (pointer->scope == current->scope) {
                        return n;
                    }
                }
                else {
                    return n;
                }
            }
        }
        pointer = pointer->previous;
    }
    n.variable = var;
    n.scope = "?";
    return n;
}

void SymbolTable::addAssignment(string lhs, string rhs) 
{
    assignments.push_back(std::make_pair(searchVariable(lhs),searchVariable(rhs)));
}

void Parser::printresolvednaming()
{
    for (auto it = table.assignments.begin(); it != table.assignments.end(); ++it) {
        cout << it->first.scope << ((it->first.scope != "::") ?
        "." : "") << it->first.variable << " = " << it->second.scope << ((it->second.scope != "::") ? 
        "." : "") << it->second.variable << endl;
    }
}

void Parser::parse_global_var()
{
    token = lexer.GetToken();
    if (token.token_type == ID) {
        lexer.UngetToken(token);
        parse_var_list(GLOBAL_ACCESS);
    }  else {
        syntax_error();
    }
    token = lexer.GetToken();
    if (token.token_type != SEMICOLON) {
        syntax_error();
    }
}

void Parser::parse_private_vars()
{
    token = lexer.GetToken();
    if (token.token_type == PRIVATE) {
        token = lexer.GetToken();
        if (token.token_type == COLON) {
            token = lexer.GetToken();
            if (token.token_type == ID) {
                lexer.UngetToken(token);
                parse_var_list(PRIVATE_ACCESS);
            } else {
                syntax_error();
            }
        } else {
            syntax_error();
        }
    } else {
        lexer.UngetToken(token);
        return;
    }
    token = lexer.GetToken();
    if (token.token_type != SEMICOLON) {
        syntax_error();
    }
}

void Parser::parse_var_list(AccessSpecifier access)
{
    token = lexer.GetToken();
    if (token.token_type == ID) {
        table.addVariable(token.lexeme, access);
        token = lexer.GetToken();
        if (token.token_type == COMMA) {
            parse_var_list(access);
        } else if (token.token_type == SEMICOLON) {
            lexer.UngetToken(token);
        }
    } else {
        syntax_error();
    }
}

void Parser::parse_scope()
{
    token = lexer.GetToken();
    if (token.token_type == ID) {
        table.addScope(token.lexeme);
        token = lexer.GetToken();
        if (token.token_type == LBRACE) {
            parse_public_var();
            parse_private_vars();
            token = lexer.GetToken();
            if (token.token_type != RBRACE) {
                lexer.UngetToken(token);
                parse_stmtList();
                token = lexer.GetToken();
                if (token.token_type == RBRACE) {
                    table.exitScope();
                } else {
                    syntax_error();
                }
            } else {
                syntax_error();
            }
        } else {
            syntax_error();
        }
    } else {
        syntax_error();
    }
}

void Parser::parse_public_var()
{
    token = lexer.GetToken();
    if (token.token_type == PUBLIC) {
        token = lexer.GetToken();
        if (token.token_type == COLON) {
            token = lexer.GetToken();
            if (token.token_type == ID) {
                lexer.UngetToken(token);
                parse_var_list(PUBLIC_ACCESS);
            }
            else {
                syntax_error();
            }
        } else {
            syntax_error();
        }
    } else {
        lexer.UngetToken(token);
        return;
    }
    token = lexer.GetToken();
    if (token.token_type != SEMICOLON) {
        syntax_error();
    }
}

void Parser::parse_program()
{
    bool scopeParsed = false;
    table.addScope("::");
    token = lexer.GetToken();
    if (token.token_type == ID) {
        Token token2 = lexer.GetToken();
        if (token2.token_type == COMMA || token2.token_type == SEMICOLON) {
            lexer.UngetToken(token2);
            lexer.UngetToken(token);
            parse_global_var();
            parse_scope();
            scopeParsed = true;
        } else if (token2.token_type == LBRACE) {
            lexer.UngetToken(token2);
            lexer.UngetToken(token);
            parse_scope();
            scopeParsed = true;
        } else {
            syntax_error();
        }
    }
    token = lexer.GetToken();
    if (token.token_type == LBRACE || scopeParsed) {
         table.exitScope();
    } else {
        syntax_error();
    }
}

void Parser::parse_stmt()
{
    token = lexer.GetToken();
    if (token.token_type == ID) {
        Token token2 = lexer.GetToken();
        if (token2.token_type == EQUAL) {
            Token token3 = lexer.GetToken();
            Token token4 = lexer.GetToken();
            if (token3.token_type == ID && token4.token_type == SEMICOLON)
            {
                table.addAssignment(token.lexeme, token3.lexeme);
            }
            else {
                syntax_error();
            }
        }
        else if (token2.token_type == LBRACE) {
            lexer.UngetToken(token2);
            lexer.UngetToken(token);
            parse_scope();
        } else {
            syntax_error();
        }
    } else {
        lexer.UngetToken(token);
    }
}

void Parser::parse_stmtList()
{
    token = lexer.GetToken();
    if (token.token_type == ID) {
        Token token2 = lexer.GetToken();
        if (token2.token_type == EQUAL || token2.token_type == LBRACE) {
            lexer.UngetToken(token2);
            lexer.UngetToken(token);
            parse_stmt();
        } else {
            lexer.UngetToken(token2);
            lexer.UngetToken(token);
            return;
        }
        token = lexer.GetToken();
        if (token.token_type == ID) {
            lexer.UngetToken(token);
            parse_stmtList();
        } else {
            lexer.UngetToken(token);
        }
    }
}

void Parser::syntax_error()
{
    cout << "Syntax Error\n";
    exit(EXIT_FAILURE);
}
int main()
{
    Parser parser;
    parser.parse_program();
    parser.printresolvednaming();
    return 0;
}