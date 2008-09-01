/*
   Lexer
*/
header
{
    import os, sys
}

options
{
    language="Python";
}

class TriLexer extends Lexer;

options
{
   k = 2;
   charVocabulary='\u0000'..'\u007F';
}

tokens
{
   STRUCT         =  "struct";
   INT            =  "int";
   BOOL           =  "bool";
   FUN            =  "fun";
   VOID           =  "void";
   PRINT          =  "print";
   ENDL           =  "endl";
   READ           =  "read";
   IF             =  "if";
   ELSE           =  "else";
   WHILE          =  "while";
   DELETE         =  "delete";
   RETURN         =  "return";
   TRUE           =  "true";
   FALSE          =  "false";
   NEW            =  "new";
   NULL           =  "null";
}

LBRACE   :  "{"   ;
RBRACE   :  "}"   ;
SEMI     :  ";"   ;
COMMA    :  ","   ;
LPAREN   :  "("   ;
RPAREN   :  ")"   ;
ASSIGN   :  "="   ;
DOT      :  "."   ;
AND      :  "&&"  ;
OR       :  "||"  ;
EQ       :  "=="  ;
LT       :  "<"   ;
GT       :  ">"   ;
NE       :  "!="  ;
LE       :  "<="  ;
GE       :  ">="  ;
PLUS     :  "+"   ;
MINUS    :  "-"   ;
TIMES    :  "*"   ;
DIVIDE   :  "/"   ;
NOT      :  "!"   ;

ID options {testLiterals=true;}
         :  ('a'..'z' | 'A'..'Z')('a'..'z' | 'A'..'Z' | '0'..'9')* ;

INTEGER      :  '0' | ('1'..'9') ('0'..'9')* ;

WS       :  (  ' '
            |  '\t'
            |  '\f'
               // handle newlines
            |  (  options {generateAmbigWarnings=false;}
               :  "\r\n"   # Evil DOS
               |  '\r'     # Macintosh
               |  '\n'     # Unix (the right way)
               )
               { newline(); }
            )+
            { $setType(Token.SKIP); }
         ;

COMMENT  :  "#"(~'\n')* '\n'
            { newline(); $setType(Token.SKIP); }
         ;

/*
   Parser
*/
class TriParser extends Parser;

options
{
   buildAST=true;
   defaultErrorHandler=false;
}

tokens
{
   PROGRAM;
   TYPES;
   TYPE;
   DECLS;
   FUNCS;
   DECL;
   DECLLIST;
   PARAMS;
   RETTYPE;
   BLOCK;
   STMTS;
   INVOKE;
   ARGS;
   NEG;
}

program
   :!  t:types d:declarations f:functions EOF!
      { #program = #([PROGRAM,"PROGRAM"],
                     #([TYPES,"TYPES"], #t),
                     #([DECLS,"DECLS"], #d),
                     #([FUNCS,"FUNCS"], #f)); }
   ;
types
   :  (STRUCT ID LBRACE) => type_declaration types
   |
   ;
type_declaration
   :  STRUCT^ ID LBRACE! nested_decl RBRACE! SEMI!
   ;
nested_decl
   :  (decl SEMI!)+
   ;
decl
   :! t:type i:ID { #decl = #([DECL,"DECL"], #([TYPE,"TYPE"],#t), #i); }
   ;
type
   :  INT
   |  BOOL
   |  STRUCT^ ID
   ;
declarations
   :  (declaration)*
   ;
declaration
   :!  t:type ilist:id_list SEMI!
      { #declaration = #([DECLLIST,"DECLLIST"], #([TYPE,"TYPE"], #t), #ilist); }
   ;
id_list
   :  ID (COMMA! ID)*
   ;
functions
   :  (function)*
   ;
function
   :!  FUN<AST=AnnotatedFunctionAST> id:ID p:parameters r:return_type LBRACE d:declarations s:statement_list RBRACE
      { #function = #(FUN,
                        #id,
                        #([PARAMS,"PARAMS"], #p),
                        #([RETTYPE, "RETTYPE"], #r),
                        #([DECLS,"DECLS"], #d),
                        #([STMTS,"STMTS"], #s)
                     );
      }
   ;
parameters
   :  LPAREN! (decl (COMMA! decl)*)? RPAREN!
   ;
return_type
   :  type
   |  VOID
   ;
statement
   :  block
   |  (lvalue ASSIGN) => assignment
   |  print
   |  read
   |  conditional
   |  loop
   |  delete
   |  ret
   |  (ID LPAREN) => invocation
   ;
block
   :!  LBRACE! s:statement_list RBRACE!
         {
            #block = #([BLOCK, "BLOCK"],
                                    #([STMTS,"STMTS"], #s)
                                   );
         }
   ;
statement_list
   :  (statement)*
   ;
assignment
   :  lvalue ASSIGN^ expression SEMI!
   ;
print
   :  PRINT^ expression (ENDL)? SEMI!
   ;
read
   :  READ^ lvalue SEMI!
   ;
conditional
   :  IF^ LPAREN! expression RPAREN! block (ELSE! block)?
   ;
loop
   :  WHILE^ LPAREN! expression RPAREN! block
   ;
delete
   :  DELETE^ expression SEMI!
   ;
ret
   :  RETURN^ (expression)? SEMI!
   ;
invocation
   :! id:ID a:arguments SEMI
      {
         #invocation = #([INVOKE,"INVOKE","AnnotatedExpressionAST"], #id, #a);
      }
   ;
lvalue
   :  ID (DOT^<AST=DottedAST> ID)*
   ;
expression
   :  boolterm ((AND^<AST=AnnotatedExpressionAST> | OR^<AST=AnnotatedExpressionAST>) boolterm)*
   ;
boolterm
   :  simple ((EQ^<AST=AnnotatedExpressionAST> | LT^<AST=AnnotatedExpressionAST> | GT^<AST=AnnotatedExpressionAST> | NE^<AST=AnnotatedExpressionAST> | LE^<AST=AnnotatedExpressionAST> | GE^<AST=AnnotatedExpressionAST>) simple)?
   ;
simple
   :  term ((PLUS^<AST=AnnotatedExpressionAST> | MINUS^<AST=AnnotatedExpressionAST>) term)*
   ;
term
   :  unary ((TIMES^<AST=AnnotatedExpressionAST> | DIVIDE^<AST=AnnotatedExpressionAST>) unary)*
   ;
unary
   :  NOT! odd_not
   |  MINUS! odd_neg
   |  selector
   ;
odd_not
   :  NOT! even_not
   |!  s:selector { #odd_not = #([NOT,"!","AnnotatedExpressionAST"], #s); }
   ;
even_not
   :  NOT! odd_not
   |  selector
   ;
odd_neg
   :  MINUS! even_neg
   |!  s:selector { #odd_neg = #([NEG,"NEG","AnnotatedExpressionAST"], #s); }
   ;
even_neg
   :  MINUS! odd_neg
   |  selector
   ;
selector
   :  factor (DOT^<AST=DottedAST> ID)*
   ;
factor
   :  LPAREN! expression RPAREN!
   |!  id:ID<AST=AnnotatedExpressionAST> (a:arguments)?
      {
         if (#a != null)
         {
            #factor = #([INVOKE,"INVOKE","AnnotatedExpressionAST"], #id, #a);
         }
         else
         {
            #factor = #id;
         }
      }
   |  INTEGER<AST=AnnotatedExpressionAST>
   |  TRUE<AST=AnnotatedExpressionAST>
   |  FALSE<AST=AnnotatedExpressionAST>
   |  NEW^<AST=AnnotatedExpressionAST> ID<AST=AnnotatedExpressionAST>
   |  NULL<AST=AnnotatedExpressionAST>
   ;
arguments
   :  LPAREN! arg_list RPAREN!
   ;
arg_list
   : expression (COMMA! expression)*
      { #arg_list = #([ARGS,"ARGS"], #arg_list); }
   |! { #arg_list = #([ARGS,"ARGS"]); }
   ;

/*
   EvilTreeParser
 */
class TriTreeParser extends TreeParser;

options
{
   importVocab=TriLexer;
}

program [records]
    :  #(PROGRAM types[records] declarations[records] functions[records])
    ;

types [records]
    :  #(TYPES (type_declarations[records])*)
    ;

type_declarations [records]
    :  #(STRUCT val:ID
    {
        key = val.getText()
        structure = Entry(key)
        records.add_to_global(key, structure)
        records.reset_counter()
    }
    (decl[records, structure])+
    )
    ;


decl [records, local]
{
    value = False
}
    :  #(DECL value=type[records] var:ID)
    {
        key = var.getText()

        local.add_to_members(key, value)
        # used only for function parameters
        local.add_to_params(value)

        records.increment_counter()
    }
    ;


type [records]
returns [result = False]
   :  #(TYPE result=datatypes[records])
   ;


datatypes [records]
returns [result = False]
    :  INT
    {
        result = Entry(0)
    }
    |  BOOL
    {
        result = Entry(True)
    }
    |  #(STRUCT var:ID)
    {
        key = var.getText()
        result = records.get_value(key)
    }
    ;

declarations [records, local_decls=False]
    :  #(DECLS (declarations_inter[records, local_decls])*)
    ;

declarations_inter [records, local_decls]
    :  #(DECLLIST declaration[records, local_decls])
    ;

declaration [records, local_decls]
{
    entry = False
}
    :  entry=type[records] id_list[records, local_decls, entry]
    ;

id_list [records, local_decls, entry]
    :  (val:ID
    {
        key = val.getText()
        if local_decls:
            records.add_to_local(key, entry)
        else:
            records.add_to_globals(key, entry)
    }
    )+
    ;

functions [records]
{
    tmp = False
    main = False
}
   :  #(FUNCS (tmp=function[records]
    {
        if tmp == True:
            main = True
    }
    )*)
    {
        if not main:
            print "main function not found"
            raise SystemExit
    }
    ;

function [records]
returns [rtnMain = False]
{
    rtn_type = False
    rtn = False
    param = False
}
    :  #(FUN var:ID
    {
        key = var.getText()
        function_entry = Entry(value, Entry(0))
        records.add_to_global(value, fn)
        records.set_local(function_entry)
    }
    param=parameters[records, function_entry] rtn_type=return_type[records]
    {
        records.set_func_ret(rtn_type)
        function_entry.set_return_type(rtn_type)

        if key == "main" and not param and rtn_type.get_type() == rtn_type.INT_TYPE:
            rtnMain = True
    }
    declarations[table, True] rtn=statements[records]
    {
        if rtn == False and rtn_type.get_type() != rtn_type.NULL_TYPE:
            print function_entry + " doesn't return through all paths ",
            print "or there is extra code after the last return statement"
            raise SystemExit
        elif rtn != False and rtn_type.get_type() == rtn_type.NULL_TYPE:
            print function_entry + " doesn't return a value"
            raise SystemExit
    }
    )
    ;

parameters [records, function_entry]
returns [has_params = False]
    :  #(PARAMS (params_decl[records, function_entry]
    {
        has_params = True
    }
    )?)
    ;

params_decl [records, function_entry]
    :
    {
        records.reset_counter()
    }
    (decl[records, function_entry])+
    {
        records.set_num_params(records.get_counter())
    }
    ;

return_type [records]
returns [rtn_val = False]
    :  #(RETTYPE rtn_val=ret_type[records])
    ;

ret_type [records]
returns [rtn_val = False]
    :  rtn_val=datatypes[records]
    |  VOID
    {
        rtn_val = new Entry()
    }
    ;

statements [records]
returns [rtn = False]
    :  #(STMTS (rtn=statement[records])*)
    ;

statement [records]
returns [rtn = False]
{
    tmp = False
}
    :  rtn=block[records]
    |  assignment[records]
    |  print[records]
    |  read[records]
    |  rtn=conditional[records]
    |  rtn=loop[records]
    |  delete[records]
    |  rtn=ret[records]
    |  tmp=invocation[records]
    ;

block [records]
returns [rtn = False]
    :  #(BLOCK rtn=statements[records])
    ;

assignment [records]
{
    exp = False
    id = False
}
    :  #(ASSIGN id=lvalue[records] exp=expression[records])
    {
        id.compare_types(e, "=")
    }
    ;

print [records]
{
    exp = False
}
    :  #(PRINT exp=expression[records] (ENDL)?)
    {
        if exp.get_type() != exp.INT_TYPE:
            print "found '" + exp + "', can only print integers"
            raise SystemExit
    }
    ;

read [records]
{
    id = False
}
    :  #(READ id=lvalue[records])
    {
        if exp.get_type() != exp.INT_TYPE:
            print "found '" + exp + "', can only read integers"
            raise SystemExit
    }
    ;

conditional [records]
returns [rtn = False]
{
    exp = False
    tmp = False
}
    :  #(IF exp=expression[records]
    {
        if exp.get_type() != exp.BOOL_TYPE:
            print "found '" + exp +"', condifional needs a boolean guard"
            raise SystemExit
    }
    rtn=block[records] (tmp=block[records]
    {
         if rtn != False:
            rtn = tmp
    }
    )?)
    ;

loop [records]
returns [rtn = False]
{
    exp = False
}
    :  #(WHILE exp=expression[records]
    {
        if exp.get_type() != exp.BOOL_TYPE:
            print "found '" + exp +"', condifional needs a boolean guard"
            raise SystemExit
    }
    rtn=block[records])
    ;

delete [records]
{
    exp = False
}
    :  #(DELETE exp=expression[records])
    {
        if exp.get_type() != exp.STRUCT_TYPE:
            print "found '" + exp +"': cannot delete, must be a structure reference"
            raise SystemExit
    }
    ;

ret [records]
returns [exp = False]
    :  #(RETURN (exp=expression[records]
    {
        exp.compareTypes(records.get_func_ret , "return")
    }
    )?)
    ;

invocation [records]
returns [rtn = False]
    : #(INVOKE val:ID
    {
        key = val.getText()
        function_entry = records.get_value(key)
        if function_entry.get_type() != function_type.FUNCTION_TYPE:
            print " '" + key + "' is not a function. invocation failed"
            raise SystemExit
    }
    arguments[records, function_entry])
    {
        rtn = function_entry.get_return_type()
    }
    ;

lvalue [records]
returns [rtn = False]
{
    id = False
}
    :  val0:ID
    {
        key = val0.getText()
        rtn = records.get_value(key0)
    }
    |  #(DOT id=lvalue[records] val1:ID)
    {
        key = val1.getText()
        if id.get_type() != id.get_type.STRUCT_TYPE:
            print "can't apply . to '" + id + "' (not a struct)"
            raise SystemExit

        rtn = id.table.ReturnValue(value, null)
    }
    ;

expression [records]
returns [rtn = False]
{
    lft = False
    rht = False
    f_entry = False
}
    :  #(AND lft=expression[records] rht=expression[records])
    {
        lft.expr_compare_types(rht, "AND", lft.BOOL_TYPE)
        rtn = Entry(True)
    }
    |  #(OR lft=expression[records] rht=expression[records])
    {
        lft.expr_compare_types(rht, "OR", lft.BOOL_TYPE)
        rtn = Entry(True)
    }
    |  #(DIVIDE lft=expression[records] rht=expression[records])
    {
        lft.expr_compare_types(rht, "DIVIDE", lft.INT_TYPE)
        rtn = Entry(0)
    }
    |  #(TIMES lft=expression[records] rht=expression[records])
    {
        lft.expr_compare_types(rht, "TIMES", lft.INT_TYPE)
        rtn = Entry(0)
    }
    |  #(PLUS lft=expression[records] rht=expression[records])
    {
        lft.expr_compare_types(rht, "PLUS", lft.INT_TYPE)
        rtn = Entry(0)
    }
    |  #(MINUS lft=expression[records] rht=expression[records])
    {
        lft.expr_compare_types(rht, "MINUS", lft.INT_TYPE)
        rtn = Entry(0)
    }
    |  #(EQ lft=expression[records] rht=expression[records])
    {
        if lft.get_type() != lft.INT_TYPE and lft.get_type() != lft.STRUCT_TYPE:
            print "EQ requires int or struct types"

        lft.compare_types(rht, "EQ")
        rtn = Entry(True)
    }
    |  #(LT lft=expression[records] rht=expression[records])
    {
        lft.expr_compare_types(rht, "LT", lft.INT_TYPE)
        rtn = Entry(True)
    }
    |  #(GT lft=expression[records] rht=expression[records])
    {
        lft.expr_compare_types(rht, "GT", lft.INT_TYPE)
        rtn = Entry(True)
    }
    |  #(NE lft=expression[records] rht=expression[records])
    {
        lft.expr_compare_types(rht, "NE", lft.INT_TYPE)
        rtn = Entry(True)
    }
    |  #(LE lft=expression[records] rht=expression[records])
    {
        lft.expr_compare_types(rht, "LE", lft.INT_TYPE)
        rtn = Entry(True)
    }
    |  #(GE lft=expression[records] rht=expression[records])
    {
        lft.expr_compare_types(rht, "GE", lft.INT_TYPE)
        rtn = Entry(True)
    }
    |  #(NOT lft=expression[records])
    {
        if lft.get_type() != lft.BOOL_TYPE:
            print "can't apply NOT to '" + lft + "'"
            raise SystemExit
        rtn = Entry(True)
    }
    |  #(NEG lft=expression[records])
    {
        if lft.get_type() != lft.INT_TYPE:
            print "can't apply NEG to '" + lft + "'"
            raise SystemExit

        rtn = Entry(0)
    }
    |  #(NEW val0:ID)
    {
        value = val0.getText()
        lft = table.get_value(value)

        if lft.get_type() != lft.STRUCT_TYPE:
            print "can't apply NEW to '" + lft + "'"
            raise SystemExit

        rtn = Entry(value)
    }
    |  #(INVOKE val4:ID
    {
        value = val4.getText()
        function_entry = records.get_value(value, local)
        if function_entry.get_type() != function_entry.FUNCTION_TYPE:
            print " '" + value + "' is not a function. invocation failed"
            raise SystemExit

        rtn = function_entry.get_return_type()
    }
    (arguments[records, f_entry])?)
    |  #(DOT lft=expression[records] val5:ID)
    {
        value = val5.getText()
        if lft.get_type() != lft.STRUCT_TYPE:
            print "can't apply . to '" + lft + "'(not a struct)"
            raise SystemExit

        rtn = records.get_value(value, lft.get_table())
    }
    |  val1:ID
    {
        value = val1.getText()
        rtn = records.get_value(value)
    }
    |  val2:INTEGER
    {
        value = int(val2.getText())
        rtn = Entry(value)
    }
    |  TRUE
    {
        rtn = Entry(True)
    }
    |  FALSE
    {
        rtn = Entry(False)
    }
    |  NULL
    {
        rtn = Entry()
    }
    ;

arguments [records, function_entry]
{
    exp = False
    param_count = 0
    found_params = False
}
    :  #(ARGS ((exp=expression[records]
    {
        exp.compare_types(function_entry.get_param_by_ndx(param_count), "argument match")
        param_count = param_count + 1
    }
    )+
    {
        if function_entry.get_num_params() == 0:
            print function_entry + " doesn't require params"
            raise SystemExit
        found_params = True
    }
    )?)
    {
        if function_entry.get_num_params() != 0 and not found_params
            print function_entry + ": requires arguments"
            raise SystemExit

        elif function_entry.get_num_params() != param_count:
            print function_entry + ": number of arguments missmatch"
            raise SystemExit
    }
    ;
