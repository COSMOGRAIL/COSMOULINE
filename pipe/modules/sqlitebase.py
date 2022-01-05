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

typeToSQLiteType = {"str":"text",
                    "float":"real",
                    "int":"integer",
                    "bool":"bool"}

class SQLInterface():
    def __init__(self, path):
        self.path = path
        self.defaulttable = "imgdb"
    def __str__(self):
        return f"sqlite3 database at {self.path}"
    
    def execute(self, sqlstatement, params=None):
        conn = sq.connect(self.path)
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
    
    def getTableNames(self):
        tabs = self.execute("SELECT name FROM sqlite_master WHERE type='table';")
        return [t[0] for t in tabs]
    
    def getColumns(self, table=None):
        if not table:
            table = self.defaulttable
        return self.execute(f"select name,type from pragma_table_info('{table}')")
    

    
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
        if not tablename:
            tablename = self.defaulttable
            
        if tablename in self.getTableNames():
            if exist_ok:
                return []
            else:
                raise RuntimeError(f"table {tablename} already exists!")
                
        cmd = f"CREATE TABLE {tablename} "
        if len(fields) > 1:
            cmd += "("
        else:
            return self.execute(cmd)
        
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
    