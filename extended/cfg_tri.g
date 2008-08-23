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
}

program [cfg_group]
    :  #(PROGRAM types[cfg_group] declarations[cfg_group, ILOC_CONST.GLOBALS]
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
      (decl[cfg_group, ILOC_CONST.STRUCT_MEMBER])+)
    ;


decl [cfg_group, decl_type]
{
    data_type = False
}
    :  #(DECL data_type=type id:ID)
    {
        val_name = id.getText()

         # add arguments to table
        if decl_type == ILOC_CNST.ARGUMENT:

            reg = Register(cfg_group.get_counter(), data_type)
            cfg_group.add_to_local(val_name, reg)

            inst = Inst_Node("loadinargument", reg)
            inst.set_val_name(val_name)

            cfg_group.get_crnt_node().add_iloc_inst(inst)
            cfg_group.increment_counter()

        # declarations inside of a struct
        if decl_type == ILOC_CONST.STRUCT_MEMBER:
            TODO = 0

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
        if decl_type == ILOC_CONST.LOCALS:
            reg = Register(cfg_group.get_counter(), data_type)

            cfg_group.add_local(var_name, reg)
            cfg_group.increment_counter()

        # add globals
        if decl_type == ILOC_CONST.GLOBALS:
            TODO = 0
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
    declarations[cfg_group, ILOC_CONST.LOCALS]
    {
        val = value.getText()
        cfg_group.get_crnt_node().add_label(val)
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

