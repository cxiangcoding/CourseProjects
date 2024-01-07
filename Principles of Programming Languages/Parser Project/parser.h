#ifndef __PARSER__H__
#define __PARSER__H__

#include "lexer.h"
typedef enum {
	GLOBAL_ACCESS,
	PUBLIC_ACCESS,
	PRIVATE_ACCESS
} AccessSpecifier;

struct symbolEntry {
	std::string variable;
	std::string scope;
	AccessSpecifier access;
};

struct scopeTable {
	std::string scope;
	scopeTable* previous;
	std::vector<symbolEntry> symbols;
	scopeTable()
	{
		previous = NULL;
	}
};

class SymbolTable
{
public:
	std::vector<std::pair<symbolEntry, symbolEntry> > assignments;
	SymbolTable();
	void addScope(std::string);
	void exitScope();
	void addVariable(std::string, AccessSpecifier);
	symbolEntry searchVariable(std::string);
	void addAssignment(std::string, std::string);
private:
	scopeTable* current;
	scopeTable* pointer;
};

class Parser
{
public:
	void parse_program();
	void printresolvednaming();

private:
	void parse_global_var();
	void parse_var_list(AccessSpecifier);
	void parse_scope();
	void parse_public_var();
	void parse_private_vars();
	void parse_stmtList();
	void parse_stmt();
	void syntax_error();
	Token token;
	LexicalAnalyzer lexer;
	SymbolTable table;
};

#endif