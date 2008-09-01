/*
   TriCFG
 */

{
   # import files
}

class TriCFG extends TreeParser;

options
{
   importVocab=TriLexer;
   language="Python";
}

program [cfg_group]
    :  #(PROGRAM types[cfg_group] declarations[cfg_group, Iloc_cnst.GLOBAL]
    functions[cfg_group])
    ;

types [cfg_group]
    :  #(TYPES (type_declarations[cfg_group])*)
    ;

type_declarations [cfg_group]
    :  #(STRUCT id5:ID
    {
        var_name = id5.getText();
    }
      (decl[cfg_group, Iloc_cnst.STRUCT_MEMBER])+)
    ;


decl [cfg_group, decl_type]
{
    data_type = False
}
    :  #(DECL data_type=type id:ID)
    {
        val_name = id.getText()

         # add arguments to table
        if decl_type == Iloc_cnst.ARGUMENT:
            reg = Register(cfg_group.get_counter(), data_type)
            reg.set_mem_set(Iloc_cnst.LOCAL)
            cfg_group.add_to_local(val_name, reg)
            cfg_group.increment_counter()

            inst = Inst_Node("loadinargument", reg)
            inst.set_val_name(val_name)
            cfg_group.get_crnt_node().add_iloc_inst(inst)

        # declarations inside of a struct
        if decl_type == Iloc_cnst.STRUCT_MEMBER:
            NOT_SUPP = 0

    }
    ;

type
returns [data_type = False]
   :  #(TYPE data_type=datatypes)
   ;

datatypes
returns [data_type = False]
    :  INT
    |  BOOL
    |  #(STRUCT id6:ID)
    {
        val_name = id6.getText()
        data_type = Entry(val_name)
    }
    ;

declarations [cfg_group, decl_type]
    :  #(DECLS (declarations_inter[cfg_group])*)
    ;

declarations_inter [cfg_group, decl_type]
    :  #(DECLLIST declaration[cfg_group])
    ;

declaration [cfg_group, decl_type]
{
    data_type = False
}
    :  data_type=type id_list[cfg_group, data_type, decl_type]
    ;

id_list [cfg_group, data_type, decl_type]
    :  (id:ID
    {
        var_name = id.getText()

        # add locals
        if decl_type == Iloc_cnst.LOCAL:
            reg = Register(cfg_group.get_counter(), data_type)
            reg.set_mem_loc(Iloc_cnst.LOCAL)
            cfg_group.add_local(var_name, reg)
            cfg_group.increment_counter()

        # add globals
        if decl_type == Iloc_cnst.GLOBAL:
            NOT_SUPP = 0
    }
    )+
    ;

functions [cfg_group]
    :  #(FUNCS
    (
    {
        # LABEL & CREATE:
        new_node = Node()

        # ENTRY LIST:
        new_node.add_entry_node(cfg_group.get_start_node())

        # EXIT LIST:
        cfg_group.get_start_node().add_exit_node(new_node)

        # new virtual register counter
        cfg_group.reset_counter()
        cfg_group.set_crnt_node(new_node)
    }
    function[cfg_group]
    {
        # ENTRY LIST:
        cfg_group.get_end_node().add_entry_node(cfg_group.get_crnt_node())

        # EXIT LIST:
        rtn_node.add_exit_node(cfg_group.get_end_node())
    }
    )*)
    ;

function [cfg_group]
{
    data_type = False
}
    :  #(FUN value:ID parameters[cfg_group] data_type=return_type
    {
        num_args = cfg_group.get_counter()
    }
    declarations[cfg_group, Iloc_cnst.LOCAL]
    {
        val = value.getText()
        cfg_group.get_crnt_node().add_label(val)
        cfg_group.get_crnt_node().set_num_args(num_args)
        cfg_group.get_crnt_node().set_num_locals(cfg_group.get_counter())

        # function return type
        cfg_group.set_func_ret(data_type)
    }
    statements[cfg_group]
    {
        inst = new Inst_Node("ret")
        cfg_group.get_crnt_node().add_iloc_inst(inst)
    }
    )
    ;

parameters [cfg_group]
    :  #(PARAMS (params_decl[cfg_group])?)
    ;

params_decl [cfg_group]
    :  (decl[cfg_group, Iloc_cnst.ARGUMENT])+
    ;

return_type
returns [ data_type = False ]
    :  #(RETTYPE data_type=ret_type)
    ;

ret_type
returns [ data_type = False ]
    :  data_type=datatypes
    |  VOID
    ;

statements [cfg_group]
    :  #(STMTS (statement[cfg_group])*)
    ;

statement [cfg_group]
    :  block[cfg_group]
    |  assignment[cfg_group]
    |  print[cfg_group]
    |  read[cfg_group]
    |  conditional[cfg_group]
    |  loop[cfg_group]
    |  delete[cfg_group]
    |  ret[cfg_group]
    |  invocation[cfg_group]
    ;

block [cfg_group]
    :  #(BLOCK statements[cfg_group])
    ;

assignment [cfg_group]
{
    r1 = False
    r2 = False
}
    :  #(ASSIGN r1=lvalue[cfg_group] r2=expression[cfg_group])
    {

        # store into a global
        if r1.get_mem_loc() == Iloc_cnst.GLOBAL:
            inst = Inst_Node("storeai", r2)
            inst.set_val_name(r1.get_val_name())

        # store into memory
        if r1.get_mem_loc() == Iloc_cnst.MEMORY:
            inst = Inst_Node("storeai", r2, r1)

        # store into a register
        else:
            inst = Inst_Node("mov", r2, r1)

        cfg_group.get_crnt_node().add_iloc_inst(inst)
    }
    ;


print [cfg_group]
{
    r1 = False
    end = False
}
    :  #(PRINT r1=expression[cfg_group] (ENDL
    {
        end = True
    }
    )?)
    {
        if end:
            inst = Inst_Node("println", r1)
        else
            inst = Inst_Node("print", r1)

        cfg_group.get_crnt_node().add_iloc_inst(inst)
    }
    ;


read [cfg_group]
{
    r1 = False
}
    :  #(READ r1=lvalue[cfg_group])
    {
        inst = Inst_Node("read", r1)
        cfg_group.get_crnt_node().add_iloc_inst(inst)
    }
    ;

conditional [cfg_group]
{
    r1 = False
    else_ndx = False
    then_ndx = False
    end_ndx = False
}
    :  #(IF r1=expression[cfg_group]
    {
        start_node = cfg_group.get_crnt_node()

        # FOR THEN BLOCK
        # SET LABEL & CREATE:
        then_node = Node(cfg_group.get_label_counter())
        then_ndx = cfg_group.get_label_counter()
        cfg_group.increment_label_counter()

        # ENTRY LIST:
        then_node.add_entry_node(start_node)

        # EXIT LIST:
        start_node.add_exit_node(then_node)

        cfg_group.set_crnt_node(then_node)
    }
    block[cfg_group]
    {
        then_node = cfg_group.get_crnt_node()
    }
    (
    {
        # FOR ELSE BLOCK
        # SET LABEL & CREATE:
        else_node = Node(cfg_group.get_label_counter())
        else_ndx = cfg_group.get_label_counter()
        cfg_group.increment_label_counter()

        # ENTRY LIST:
        else_node.add_entry_node(start_node)

        # EXIT LIST:
        start_node.add_exit_node(else_node)

        cfg_group.set_crnt_node(else_node)
    }
    block[cfg_group]
    {
        else_node = cfg_group.get_crnt_node()
    }
    )?
    {
        # EXIT NODE
        # SET LABEL & CREATE
        end_node = Node(cfg_group.get_label_counter())
        end_ndx = cfg_group.get_label_counter()
        cfg_group.increment_label_counter()

        # ENTRY_LIST
        end_node.add_entry_node(then_node)

        # EXIT_LIST
        then_node.add_exit_node(end_node)

        inst = Inst_Node("cbr", r1)
        inst.add_label(then_ndx)

        if else_ndx == False:
            inst.add_label(end_ndx)
            end_node.add_entry_node(start_node)
            start_node.add_exit_node(end_node)
        else:
            inst.add_label(else_ndx)
            end_node.add_entry_node(else_node)
            else_node.add_exit_node(end_node)

        start_node.add_iloc_inst(inst)

        cfg_group.set_crnt_node(end_node)
    }
    )
    ;

loop [cfg_group]
{
    r1 = False
}
    :  #(WHILE r1=guard:expression[cfg_group]
    {
        start_node = cfg_group.get_crnt_node()
        while_ndx = cfg_group.get_label_counter()

        # SET LABEL & CREATE:
        while_node = new node(cfg_group.get_label_counter())
        cfg_group.increment_label_counter()

        # ENTRY_LIST:
        while_node.add_entry_node(cfg_group.get_crnt_node())

        # EXIT_LIST:
        cfg_group.get_crnt_node().add_exit_node(while_node)

        cfg_group.set_crnt_node(while_node)
    }
    block[cfg_group])
    {
        # update node reference
        rtn_node = cfg_group.get_crnt_node()

        # end node, label & create
        end_node = Node(cfg_group.get_label_counter())
        end_ndx = cfg_group.get_label_counter()
        cfg_group.increment_label_counter()

        inst = Inst_Node("cbr", r1)
        inst.add_label(while_ndx)
        inst.add_label(end_ndx)
        start_node.add_iloc_inst(inst)

        # Repeat guard expression for repeated guard evaluation
        r2 = expression(guard, cfg_group)
        inst = Inst_Node("cbr", r2)
        inst.add_label(while_ndx)
        inst.add_label(end_ndx)
        rtn_node.add_iloc_inst(inst)

        # ENTRY LIST:
        while_node.add_entry_node(start_node)
        end_node.add_entry_node(rtn_node)

        # EXIT LIST
        start_node.add_exit_node(while_node)
        rtn_node_add_exit_node(end_node)

        cfg_group.set_crnt_node(end_node)
    }
    ;

delete [cfg_group]
{
    r1 = False
}
    :  #(DELETE r1=expression[cfg_group]
    {
        inst = Inst_Node("del", r1)
        cfg_group.get_crnt_node().add_iloc_inst(inst)
    }
    )
    ;

ret [cfg_group]
{
    r1 = False
}
   :  #(RETURN (r1=expression[cfg_group]
    {
        inst = Inst_Node("storeret", r1)
        cfg_group.get_crnt_node().add_iloc_inst(inst)
    }
    )?
    {
        inst = Inst_Node("ret")
        cfg_group.get_crnt_node().add_iloc_inst(inst)
    }
    )
    ;

invocation [cfg_group]
{
    load_insts = []
}
   : #(INVOKE id:ID arguments[cfg_group, load_insts]
    {
        cfg_group.get_crnt_node().extend_iloc(load_insts)

        inst = Inst_Node("call")
        inst.set_val_name(id.getText())
        cfg_group.get_crnt_node().add_iloc_inst(inst)
    }
    )
    ;

lvalue [cfg_group]
returns [dest_reg = False]
{
    r1 = False
}
    :  id:ID
    {
        var_name = id.getText()
        dest_reg = cfg_group.get_value(var_name)
    }
    |  #(DOT r1=lvalue[cfg_group] id1:ID)
    {
        NOT_SUPP = 0
    }
    ;

expression [cfg_group]
returns [dest_reg = False]
{
    r1 = False
    r2 = False
    load_insts = []
}
    :  #(AND r1=expression[cfg_group] r2=expression[cfg_group]
    {
        dest_reg = Register(cfg_group.get_counter())
        cfg_group.increment_counter()

        inst = Inst_Node("and", r1, r2, dest_reg)
        cfg_group.get_crnt_node().add_iloc_inst(inst)
    }
    )
    |  #(OR r1=expression[cfg_group] r2=expression[cfg_group]
    {
        dest_reg = Register(cfg_group.get_counter())
        cfg_group.increment_counter()

        inst = Inst_Node("or", r1, r2, dest_reg)
        cfg_group.get_crnt_node().add_iloc_inst(inst)
    }
    )
    |  #(DIVIDE r1=expression[cfg_group] r2=expression[cfg_group])
    {
        dest_reg = Register(cfg_group.get_counter())
        cfg_group.increment_counter()

        inst = Inst_Node("div", r1, r2, dest_reg)
        cfg_group.get_crnt_node().add_iloc_inst(inst)
    }
    |  #(TIMES r1=expression[cfg_group] r2=expression[cfg_group])
    {
        dest_reg = Register(cfg_group.get_counter())
        cfg_group.increment_counter()

        inst = Inst_Node("mult", r1, r2, dest_reg)
        cfg_group.get_crnt_node().add_iloc_inst(inst)
    }
    |  #(PLUS r1=expression[cfg_group] r2=expression[cfg_group])
    {
        dest_reg = Register(cfg_group.get_counter())
        cfg_group.increment_counter()

        inst = Inst_Node("add", r1, r2, dest_reg)
        cfg_group.get_crnt_node().add_iloc_inst(inst)
    }
    |  #(MINUS r1=expression[cfg_group] r2=expression[cfg_group])
    {
        dest_reg = Register(cfg_group.get_counter())
        cfg_group.increment_counter()

        inst = Inst_Node("sub", r1, r2, dest_reg)
        cfg_group.get_crnt_node().add_iloc_inst(inst)
    }
    |  #(EQ r1=expression[cfg_group] r2=expression[cfg_group])
    {
        dest_reg = Register(cfg_group.get_counter())
        cfg_group.increment_counter()

        inst = Inst_Node("cmpEQ", r1, r2, dest_reg)
        cfg_group.get_crnt_node().add_iloc_inst(inst)
    }
    |  #(LT r1=expression[cfg_group] r2=expression[cfg_group])
    {
        dest_reg = Register(cfg_group.get_counter())
        cfg_group.increment_counter()

        inst = Inst_Node("cmpLT", r1, r2, dest_reg)
        cfg_group.get_crnt_node().add_iloc_inst(inst)
    }
    |  #(GT r1=expression[cfg_group] r2=expression[cfg_group])
    {
        dest_reg = Register(cfg_group.get_counter())
        cfg_group.increment_counter()

        inst = Inst_Node("cmpLE", r2, r1, dest_reg)
        cfg_group.get_crnt_node().add_iloc_inst(inst)
    }
    |  #(NE r1=expression[cfg_group] r2=expression[cfg_group])
    {
        tmp_reg = Register(cfg_group.get_counter())
        cfg_group.increment_counter()

        inst = Inst_Node("cmpEQ", r1, r2, tmp_reg)
        cfg_group.get_crnt_node().add_iloc_inst(inst)

        dest_reg = Register(cfg_group.get_counter())
        cfg_group.increment_counter()

        inst = Inst_Node("xori", r1, dest_reg, False, 1)
        cfg_group.get_crnt_node().add_iloc_inst(inst)
    }
    |  #(LE r1=expression[cfg_group] r2=expression[cfg_group])
    {
        dest_reg = Register(cfg_group.get_counter())
        cfg_group.increment_counter()

        inst = Inst_Node("cmpLE", r1, r2, dest_reg)
        cfg_group.get_crnt_node().add_iloc_inst(inst)
    }
    |  #(GE r1=expression[cfg_group] r2=expression[cfg_group])
    {
        dest_reg = Register(cfg_group.get_counter())
        cfg_group.increment_counter()

        inst = Inst_Node("cmpLT", r2, r1, dest_reg)
        cfg_group.get_crnt_node().add_iloc_inst(inst)
    }
    |  #(NOT r1=expression[cfg_group])
    {
        dest_reg = Register(cfg_group.get_counter())
        cfg_group.increment_counter()

        inst = Inst_Node("xori", r1, dest_reg, False, 1)
        cfg_group.get_crnt_node().add_iloc_inst(inst)
    }
    |  #(NEG r1=expression[cfg_group])
    {
        dest_reg = Register(cfg_group.get_counter())
        cfg_group.increment_counter()

        inst = Inst_Node("multi", r1, dest_reg, False, -1)
        cfg_group.get_crnt_node().add_iloc_inst(inst)
    }
    |  #(NEW id:ID)
    {
        dest_reg = Register(cfg_group.get_counter())
        cfg_group.increment_counter()

        inst = Inst_Node("new")
        inst.set_val_name(id.getText())
        inst.set_imd(4) # size of structure (4 is a placeholder)
        cfg_group.get_crnt_node().add_iloc_inst(inst)
    }
    |  #(INVOKE id3:ID (arguments[cfg_group, load_insts])?
    {
        cfg_group.get_crnt_node().extend_iloc(load_insts)

        dest_reg = Register(cfg_group.get_counter())
        cfg_group.increment_counter()

        inst = Inst_Node("call")
        inst.set_val_name(id3.getText())
        cfg_group.get_crnt_node().add_iloc_inst(inst)
    }
    )
    {
        dest_reg = Register(cfg_group.get_counter(), cfg_group.get_func_ret())
        cfg_group.increment_counter()

        inst = Inst_Node("loadret", dest_reg)
        cfg_group.get_crnt_node().add_iloc_inst(inst)
    }
    |  #(DOT r1=expression[cfg_group] id2:ID)
    {
        NOT_SUPP = 0
    }
    |  id1:ID
    {
        var_name = id.getText()
        dest_reg = cfg_group.get_value(var_name)
    }
    |  i:INTEGER
    {
        dest_reg = Register(cfg_group.get_counter())
        cfg_group.increment_counter()

        inst = Inst_Node("loadi", dest_reg)
        inst.set_imd = int(i.getText())
        cfg_group.get_crnt_node().add_iloc_inst(inst)
    }
    |  TRUE
    {
        dest_reg = Register(cfg_group.get_counter())
        cfg_group.increment_counter()

        inst = Inst_Node("loadi", dest_reg)
        inst.set_imd = 1
        cfg_group.get_crnt_node().add_iloc_inst(inst)

    }
    |  FALSE
    {
        dest_reg = Register(cfg_group.get_counter())
        cfg_group.increment_counter()

        inst = Inst_Node("loadi", dest_reg)
        inst.set_imd = 0
        cfg_group.get_crnt_node().add_iloc_inst(inst)
    }
    |  NULL
    {
        dest_reg = Register(cfg_group.get_counter())
        cfg_group.increment_counter()

        inst = Inst_Node("loadi", dest_reg)
        inst.set_imd = 0
        cfg_group.get_crnt_node().add_iloc_inst(inst)
    }
    ;

arguments [cfg_group, load_insts]
{
    r1 = False
    arg_count = 0
}
    :  #(ARGS ((r1=expression[cfg_group]
    {
        inst = Inst_Node("storeoutargument", r1)
        inst.set_arg_num(arg_count)
        arg_count = arg_count + 1
        load_insts.append(inst)
    }
    )+)?
    )
    ;
