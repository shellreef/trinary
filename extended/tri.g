/*
   Lexer
*/
header
{
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
               :  "\r\n"   // Evil DOS
               |  '\r'     // Macintosh
               |  '\n'     // Unix (the right way)
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

program [record]
    :  #(PROGRAM types[record] declarations[record] functions[record])
    ;

types [record]
    :  #(TYPES (type_declarations[record])*)
    ;

type_declarations [record]
    :  #(STRUCT val:ID
{
    key = val.getText()
    structure = Entry(key)
    record.add_to_global(key, structure)
    record.reset_counter()
}
    (decl[record, entry])+
{
    # table.put(key, entry);
}
    )
    ;

decl [records, Records local, Counter i] { returned = null; }
    :  #(DECL returned=type[table, local] var:ID)
      {
         String id = var.getText();
         local.put(id, t);
         local.put("" + (i.count), t);
         i.count++;
      }
   ;

type [records, Records local] returns [Entry t = null]
   :  #(TYPE t=datatypes[table, local])
   ;

datatypes [records, Records local] returns [type = False]
   :  INT
      {
         t = new Entry(0);
      }
   |  BOOL
      {
         t = new Entry(true);
      }
   |  #(STRUCT v:ID)
      {
         String value = v.getText();
         t = (Entry)table.ReturnValue(value, local);
      }
   ;

declarations [Records table, Records local]
   :  #(DECLS (declarations_inter[table, local])*)
   ;

declarations_inter [Records table, Records local]
   :  #(DECLLIST declaration[table, local])
   ;

declaration [Records table, Records local] { Entry tp = null; }
   :  tp=type[table, local] id_list[table, local, tp]
   ;

id_list [Records table, Records local, Entry tp]
   :  (val0:ID
         {
            String id = val0.getText();
            if (local == null) {
               table.put(id, tp);
            }
            else {
               local.put(id, tp);
            }
         }
      )+
   ;

functions [Records table] {boolean tmp, main = false;}
   :  #(FUNCS (tmp=function[table]
         {  if (tmp == true) { main = true; } }
       )*)
         {  if (!main) {
               (new Entry()).printError("'fun main() int {}' not found"); } }
   ;

function [Records table] returns [boolean rtnMain = false]
   { Entry fn, returnType = null, retn; String value; boolean param = false;}
   :  #(FUN var2:ID
      {
         value = var2.getText();
         fn = new Entry(value, new Entry(0));
         table.put(value, fn);
      }
   param=parameters[table, fn.table, fn] returnType=return_type[table, fn.table]
      {
         fn.table.put(fn.table.RTN, returnType);

         if (!returnType.isNull) {
            fn.return_variable = returnType;
            fn.hasReturnType = true;
         }
         else {
            fn.hasReturnType = false;
         }

         if (value.equals("main") && !param && returnType.isInt) {
            rtnMain = true;
         }
      }
   declarations[table, fn.table] retn=statements[table, fn.table]
   {
      if (retn == null && (fn.hasReturnType) && !(fn.return_variable.isNull)) {
         fn.printError(fn.stringname + " doesn't return through all paths " +
                       "or there is extra code after the last return statement");
      }
      else if (retn != null && !(fn.hasReturnType)) {
         fn.printError(fn.stringname + " doesn't return a value");
      }
   }
   )
   ;

parameters [Records table, Records local, Entry f_entry]
   returns [boolean rtn = false;]
   :  #(PARAMS (params_decl[table, local]
      {
         rtn = true;
         f_entry.hasParams = true;
      }
      )?)
   ;

params_decl [Records table, Records local] { Counter i = new Counter(0); }
   :  (decl[table, local, i])+
   ;

return_type [Records table, Records local] returns [Entry t = null]
   :  #(RETTYPE t=ret_type[table, local])
   ;

ret_type [Records table, Records local] returns [Entry t = null]
   :  t=datatypes[table, local]
   |  VOID
      {
         t = new Entry();
      }
   ;

statements [Records table, Records local] returns [Entry rtn = null]
   :  #(STMTS (rtn=statement[table, local])*)
   ;

statement [Records table, Records local] returns [Entry rtn = null]
   { Entry tmp = null;}
   :  rtn=block[table, local]
   |  assignment[table, local]
   |  print[table, local]
   |  read[table, local]
   |  rtn=conditional[table, local]
   |  rtn=loop[table, local]
   |  delete[table, local]
   |  rtn=ret[table, local]
   |  tmp=invocation[table, local]
   ;

block [Records table, Records local] returns [Entry rtn = null]
   :  #(BLOCK rtn=statements[table, local])
   ;

assignment [Records table, Records local]
   {
      Entry e;
      Entry id;
   }
   :  #(ASSIGN id=lvalue[table, local] e=expression[table, local])
      {
         id.compareTypes(e, "=");
      }
   ;

print [Records table, Records local]
   {
      Entry e;
   }
   :  #(PRINT e=expression[table, local] (ENDL)?)
      {
         if (!e.isInt) {
            e.printError("found '" + e.stringname +
            "', can only print integers");
         }
      }
   ;

read [Records table, Records local]
   {
      Entry id;
   }
   :  #(READ id=lvalue[table, local])
      {
         if (!id.isInt) {
            id.printError("found '" + id.stringname +
            "', can only read to an integer");
         }
      }
   ;

conditional [Records table, Records local] returns [Entry rtn = null]
   {
      Entry e, tmp=null;
   }
   :  #(IF e=expression[table, local]
      {
         if (!e.isBool) {
            e.printError("found '" + e.stringname
            +"', condifional needs a boolean guard");
         }
      }

      rtn=block[table, local] (tmp=block[table, local]
      {
         if (rtn != null) {
            rtn = tmp;
         }
      }
      )?)
   ;

loop [Records table, Records local] returns [Entry rtn = null]
   {
      Entry e;
   }
   :  #(WHILE e=expression[table, local]
      {
         if (!e.isBool) {
            e.printError("found '" + e.stringname
            +"', loop needs a boolean guard");
         }
      }
      rtn=block[table, local])
   ;

delete [Records table, Records local]
   {
      Entry e;
   }
   :  #(DELETE e=expression[table, local])
      {
         if (!e.isStruct) {
            e.printError("cannot free '" + e.stringname + "' b/c it is not a struct");
         }
      }
   ;

ret [Records table, Records local] returns [Entry t = null]
   :  #(RETURN (t=expression[table, local]
         { t.compareTypes( (Entry)local.get(local.RTN) , "return"); }
      )?)
   ;

invocation [Records table, Records local] returns [Entry rtn = null]
   { Entry f_entry = null; }
   : #(INVOKE val:ID
      {
         String s = (String)val.getText();
         f_entry = (Entry)table.ReturnValue(s, local);
         if (!(f_entry.isFunction)) {
            f_entry.printError(" '" + s + "' is not a function. invocation failed");
         }
      }
     arguments[table, local, f_entry])
      {
         String value = val.getText();
         rtn = (table.ReturnValue(value, local)).return_variable;
      }
   ;

lvalue [Records table, Records local] returns [Entry t = null]
   {
      Entry id;
   }
   :  val0:ID
      {
         String value = val0.getText();
         t = table.ReturnValue(value, local);
      }
   |  #(DOT id=lvalue[table, local] val1:ID)
      {
         String value = val1.getText();
         if (!id.isStruct) {
            id.printError("can't apply . to '" + id.stringname + "' (not a struct)");
         }

         t = id.table.ReturnValue(value, null);
      }
   ;

expression [Records table, Records local] returns [Entry t = null]
   {Entry lft, rht, f_entry;}
   :  #(AND lft=expression[table, local] rht=expression[table, local])
      {
         if (!lft.isBool) {
            lft.printError("AND requires boolean types");
         }
         lft.compareTypes(rht, "AND");
         t = new Entry(true);
      }
   |  #(OR lft=expression[table, local] rht=expression[table, local])
      {
         if (!lft.isBool) {
            lft.printError("OR requires boolean types");
         }
         lft.compareTypes(rht, "OR");
         t = new Entry(true);
      }
   |  #(DIVIDE lft=expression[table, local] rht=expression[table, local])
      {
         if (!lft.isInt) {
            lft.printError("DIVIDE requires int types");
         }
         lft.compareTypes(rht, "DIVIDE");
         t = new Entry(0);
      }
   |  #(TIMES lft=expression[table, local] rht=expression[table, local])
      {
         if (!lft.isInt) {
            lft.printError("TIMES requires int types");
         }
         lft.compareTypes(rht, "TIMES");
         t = new Entry(0);
      }
   |  #(PLUS lft=expression[table, local] rht=expression[table, local])
      {
         if (!lft.isInt) {
            lft.printError("PLUS requires int types");
         }
         lft.compareTypes(rht, "PLUS");
         t = new Entry(0);
      }
   |  #(MINUS lft=expression[table, local] rht=expression[table, local])
      {
         if (!lft.isInt) {
            lft.printError("MINUS requires int types");
         }
         lft.compareTypes(rht, "MINUS");
         t = new Entry(0);
      }
   |  #(EQ lft=expression[table, local] rht=expression[table, local])
      {
    if (!lft.isInt && !lft.isStruct) {
       lft.printError("EQ requires int or struct types");
    }
         lft.compareTypes(rht, "EQ");
         t = new Entry(true);
      }
   |  #(LT lft=expression[table, local] rht=expression[table, local])
      {
         if (!lft.isInt) {
            lft.printError("LT requires int types");
         }
         lft.compareTypes(rht, "LT");
         t = new Entry(true);
      }
   |  #(GT lft=expression[table, local] rht=expression[table, local])
      {
         if (!lft.isInt) {
            lft.printError("GT requires int types");
         }
         lft.compareTypes(rht, "GT");
         t = new Entry(true);
      }
   |  #(NE lft=expression[table, local] rht=expression[table, local])
      {
         if (!lft.isInt && !lft.isStruct) {
            lft.printError("NE requires int or struct types");
         }
         lft.compareTypes(rht, "NE");
         t = new Entry(true);
      }
   |  #(LE lft=expression[table, local] rht=expression[table, local])
      {
         if (!lft.isInt) {
            lft.printError("LE requires int types");
         }
         lft.compareTypes(rht, "LE");
         t = new Entry(true);
      }
   |  #(GE lft=expression[table, local] rht=expression[table, local])
      {
         if (!lft.isInt) {
            lft.printError("GE requires int types");
         }
         lft.compareTypes(rht, "GE");
         t = new Entry(true);
      }
   |  #(NOT lft=expression[table, local])
      {
         if (lft.isBool) {
            t = new Entry(true);
         }
         else {
            lft.printError("can't apply NOT to '" + lft.stringname + "'");
         }
      }
   |  #(NEG lft=expression[table, local])
      {
         if (lft.isInt) {
            t = new Entry(0);
         }
         else {
            lft.printError("can't apply NEG to '" + lft.stringname + "'");
         }
      }
   |  #(NEW val0:ID)
      {
         String value = val0.getText();
         lft = table.ReturnValue(value, local);

         if (lft.isStruct) {
            t = new Entry(value);
         }
         else {
            lft.printError("can't apply NEW to '" + lft.stringname + "'");
         }
      }
   |  #(INVOKE val4:ID
      {
         String s = (String)val4.getText();
         f_entry = (Entry)table.ReturnValue(s, local);
         if (!(f_entry.isFunction)) {
            f_entry.printError(" '" + s + "' is not a function. invocation failed");
         }

         t = f_entry.return_variable;
      }
      (arguments[table, local, f_entry])?)
   |  #(DOT lft=expression[table, local] val5:ID)
      {
         String value = val5.getText();
         if (!lft.isStruct) {
            lft.printError("can't apply . to '" + lft.stringname + "'(not a struct)");
         }

         t = table.ReturnValue(value, local, lft.table);
      }
   |  val1:ID
      {
         String value = val1.getText();

         t = table.ReturnValue(value, local);
      }
   |  val2:INTEGER
      {
         int value = (int)Integer.parseInt(val2.getText());
         t = new Entry(value);
      }
   |  val3:TRUE
      {
         boolean value = (boolean)Boolean.getBoolean(val3.getText());
         t = new Entry(value);
      }
   |  FALSE
      {
         t = new Entry(false);
      }
   |  NULL
      {
         t = new Entry();
      }
   ;

arguments [Records table, Records local, Entry f_entry]
   {
      Entry e, actual; int count = 0; boolean f_params = false;
   }
   :  #(ARGS ((e=expression[table, local]
         {
         actual = (Entry)table.ReturnValue("" + count, f_entry.table);
         actual.compareTypes(e, "argument");
         count++;
         }
      )+
         {
         if (!(f_entry.hasParams)) {
            f_entry.printError(f_entry.stringname + " doesn't require params");
         }
         f_params = true;
         }
      )?)
         {
         if ((f_entry.hasParams) && !f_params) {
            f_entry.printError(f_entry.stringname + " requires arguments");
         }
         else if (f_params && f_entry.table.containsKey("" + count)) {
            f_entry.printError(f_entry.stringname + " requires more arguments");
         }
         }
   ;
