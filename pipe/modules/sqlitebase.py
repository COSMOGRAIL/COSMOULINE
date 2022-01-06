# -*- coding: utf-8 -*-

"""
MAIN IDEA OF THIS: BE BACKWARDS COMPATIBLE WITH KIRBYBASE

So I'll try to translate everything so that the database
commands throughout the pipeline need not be changed.


all functions in kirbybase:
['db.insertBatch',
 'db.close',
 'db.delete',
 'db.dropFields',
 'db.getFieldNames',
 'db.select',
 'db.drop',
 'db.addFields',
 'db.create',
 'db.append',
 'db.update',
 'db.len',
 'db.validate',
 'db.insert',
 'db.pack',
 'db.getFieldTypes']


only those used in the pipe:

['db.insertBatch',
 'db.dropFields',
 'db.getFieldNames',
 'db.select',
 'db.create',
 'db.addFields',
 'db.append',
 'db.validate',
 'db.update',
 'db.insert',
 'db.pack',
 'db.getFieldTypes']


@author: frederic dux
"""

import sqlite3 as sq

import re

def regexp(expr, item):
    if not item:
        item = ""
    reg = re.compile(expr)
    return reg.search(item) is not None

typeToSQLiteType = {"str":"text",
                    "float":"real",
                    "int":"integer",
                    "bool":"bool"}
SQLiteTypeTotype = {v:k for k,v in typeToSQLiteType.items()}
DEBUG = True

class SQLInterface():
    def __init__(self, path):
        self.path = path
        self.defaulttable = "imgdb"
        
    def __str__(self):
        return f"sqlite3 database at {self.path}"
    
    def execute(self, sqlstatement, params=None):
        if DEBUG:
            print(sqlstatement)
        conn = sq.connect(self.path)
        # in case there is reg exprs, must add a function to the connection:
        if 'regexp' in sqlstatement.lower():
            conn.create_function("REGEXP", 2, regexp)
        with conn:
            cur = conn.cursor()
            if params:
                cur.execute(sqlstatement, params)
            else:
                cur.execute(sqlstatement)
            result = cur.fetchall()
        conn.close()
        return result
    
    
    def _formatFields(self, fields):
        """
        takes fields in the KirbyBase format: ["name:type", "name2:type2"...]
        and transforms it to an sql format:
            name sqltype, name2 sqltype, ...

        """
        cmd = ""
        for f in fields:
            name, typ = f.split(':')
            typ = self._typeToSQLiteType(typ)
                
            cmd += f"{name} {typ},"
        return cmd
    
    
    def _typeToSQLiteType(self, typ):
        try:
            typ = typeToSQLiteType[typ]
        except KeyError:
            msg = f"Uknown type encountered while creating db: {typ}"
            raise NotImplementedError(msg)
        return typ


    def _convertInput(self, values):
        """If values is a dictionary or an object, we are going to convert 
        it into a list.  That way, we can use the same validation and 
        updating routines regardless of whether the user passed in a 
        dictionary, an object, or a list.
        """
        # If values is a list, make a copy of it.
        if isinstance(values, list): record = list(values)
        # If values is a dictionary, convert its values into a list
        # corresponding to the table's field names.  If there is not
        # a key in the dictionary corresponding to a field name, place a
        # '' in the list for that field name's value.
        elif isinstance(values, dict):
            record = [values.get(k,'') for k in self.getFieldNames()]        
        # If values is a record object, then do the same thing for it as
        # you would do for a dictionary above.
        else:
            record = [getattr(values,a,'') for a in self.getFieldNames()]
        # Return the new list with all items == None replaced by ''.
        new_rec = []
        for r in record:
            if r == None:
                new_rec.append('')
            else:
                new_rec.append(r)
        return new_rec   


    def getTableNames(self):
        tabs = self.execute("SELECT name FROM sqlite_master WHERE type='table';")
        return [t[0] for t in tabs]
    
    def getColumns(self, tablename=None):
        if not tablename:
            tablename = self.defaulttable
        return self.execute(f"select name,type from pragma_table_info('{tablename}')")
    
    def getFieldNames(self, tablename=None):
        if not tablename:
            tablename = self.defaulttable 
        return [c[0] for c in self.getColumns(tablename)]

    def getFieldTypes(self, tablename=None):
        if not tablename:
            tablename = self.defaulttable 
        return [SQLiteTypeTotype[c[1].lower()] for c in self.getColumns(tablename)]
    
    def getColumnType(self, field, tablename=None):
        if not tablename:
            tablename = self.defaulttable 
        fields = self.getFieldNames(tablename)
        types = self.getFieldTypes(tablename)
        if not field in fields:
            raise AssertionError(f"no such field ({field}) in table {tablename}")
        matchindex = fields.index(field)
        return types[matchindex]

    def create(self, fields, tablename=None, exist_ok=True):
        """
        creates a table in the database.
        In our context, usually we create only one table 
        so this will be called once.

        Parameters
        ----------
        fields : list of strings
            format: ["name:type", "name2:type2", ...]
        tablename : str, name of the created table
             defaults to "imgdb".
        exist_ok : bool
            if true, doesn't mind that the table already exists and simply 
            does nothing.
            if false, will crash if the table exists.

        Returns
        -------
        None.

        """
        if len(fields) == 0:
            raise AssertionError("Can't create a table with 0 column.")
            
        if not tablename:
            tablename = self.defaulttable
            
        if tablename in self.getTableNames():
            if exist_ok:
                return []
            else:
                raise RuntimeError(f"table {tablename} already exists!")
                
        cmd = f"CREATE TABLE {tablename} (recno INTEGER NOT NULL PRIMARY KEY,"
        
        
        cmd += self._formatFields(fields)
        cmd = cmd[:-1] + ")"
        return self.execute(cmd)
    
    def addFields(self, listoffields, tablename=None, exist_ok=True):
        if not tablename:
            tablename = self.defaulttable
            
        if not tablename in self.getTableNames():
            raise RuntimeError(f"table {tablename} does not exists!")
            
        alreadytherecols = self.getColumns(tablename)
        colnames = [c[0] for c in alreadytherecols]
        coltypes = [c[1] for c in alreadytherecols]
        
        for col in listoffields:
            name, typ = col.split(":")
            typ = self._typeToSQLiteType(typ)
            if name in colnames:
                if exist_ok:
                    matchindex = colnames.index(name)
                    oldtyp = coltypes[matchindex]
                    if not oldtyp == typ:
                        raise RuntimeError(f"can't change type of existing column: {col}!")
                    # if column exists, and we fine with that and the type matches:
                    # go to next.
                    continue
                else:
                    raise RuntimeError(f"column {col} already exists!")
            else:
                self.execute(f"alter table {tablename} add {name} {typ}")
                
    def insertBatch(self, listOfDics, tablename=None):
        if not tablename:
            tablename = self.defaulttable
            
        for dic in listOfDics:
            self.insert(dic, tablename=tablename)
        
    def insert(self, dic, tablename=None):
        if not tablename:
            tablename = self.defaulttable
        colnames, colvals = "(", "("
        for name, val in dic.items():
            colnames += f"{name},"
            colvals += f"{val},"
        colnames, colvals = colnames[:-1]+")", colvals[:-1]+")"
        cmd = f"insert into {tablename} {colnames} values {colvals}"
        return self.execute(cmd)


    def select(self, fields, searchData, filter=None, useRegExp=False, 
               sortFields=[], sortDesc=[], returnType="list", tablename=None):
        if not tablename:
            tablename = self.defaulttable
        if not filter:
            filter_str = " * "
        else:
            filter_str = ','.join(filter)
        req = f"select {filter_str} from {tablename} "
        conditions = []
        for searchstr, field in zip(searchData, fields):
            if str(searchstr).strip() == "*":
                #joker, skip this condition.
                continue
            if not str(searchstr).strip()[0] in ["=", "<", ">", "=="]:
                if useRegExp and self.getColumnType(field, tablename) == "str":
                    searchstr = f" REGEXP '{searchstr}'"
                else:
                    if self.getColumnType(field, tablename) == "str":
                        searchstr = f"=='{searchstr}'"
                    else:
                        searchstr = f"=={searchstr}"
            conditions.append( f"{field}{searchstr}")
        conditions = " and ".join(conditions)
        if len(conditions) > 0:
            req += f"where {conditions}"
        result = self.execute(req)
        

        if returnType == "dict":
            if not filter:
                names = self.getFieldNames(tablename=tablename) 
            else:
                names = filter
            
            resultdic = [{name:val for name,val in zip(names, res)} for res in result]
            return resultdic
        elif returnType == "report":
            pass
        
        return result
    
if __name__ == "__main__":
    minimaldbfields = ['imgname:str', 'treatme:bool', 'gogogo:bool', 'whynot:str', 'testlist:bool', 'testcomment:str',
'telescopename:str', 'setname:str', 'rawimg:str',
'scalingfactor:float', 'pixsize:float','date:str','datet:str','jd:str','mjd:float',
'telescopelongitude:str', 'telescopelatitude:str', 'telescopeelevation:float',
'exptime:float','gain:float', 'readnoise:float', 'rotator:float', 'saturlevel:float',
'preredcomment1:str', 'preredcomment2:str', 'preredfloat1:float', 'preredfloat2:float']
    db = SQLInterface("test.db")
    db.create(minimaldbfields)
    db.addFields(["imgname:str"])
    