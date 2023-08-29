# -*- coding: utf-8 -*-

"""
MAIN IDEA OF THIS: BE BACKWARDS COMPATIBLE WITH KIRBYBASE

So I'll try to translate everything so that the database
commands throughout the pipeline need not be changed.


@author: frederic dux
"""

import sqlite3 as sq

import re, datetime, io

# used to test columns against regexprs:
def regexp(expr, item):
    if not item:
        item = ""
    reg = re.compile(expr)
    return reg.search(item) is not None

# converting between python types and sqlite types:
typeToSQLiteType = {"str":"text",
                    "float":"real",
                    "int":"integer",
                    "bool":"bool"}
# and reverse:
SQLiteTypeTotype = {v:k for k,v in typeToSQLiteType.items()}

DEBUG = False

class KirbyBase():
    def __init__(self, dbname, fast=False):
        # unlike KirbyBase, can store multilpe tables in an SQlite base.
        # thus give a default one:
        self.defaulttable = "images"
        
        self.debug = DEBUG 
        
        self.dbname = dbname
                
        # "fast" when adding or updating tons of rows in series, 
        # open the connection only once and store it in this object.
        self.fast = fast
        if self.fast:
            self.conn = sq.connect(dbname)
        else:
            # then open the connetion at each execute
            self.conn = None
        
    def __del__(self):
        if self.fast:
            self.conn.close()
        
    def __str__(self):
        return "sqlite3 database interface"
    
    def __repr__(self):
        return self.__str__()
    
    def execute(self, dbname, sqlstatements):
        """
        name: path to the database
        sqlstatements: list of string or string containing sql commands. 
        
        Normally we would pass an extra tuple of parameters and let
        the python sqlite3 library to handle the injection into the sql
        command strings. (security to avoid sql injections).
        But pretty useless here imo, not a database to a website.
        
        So we just pass a list of strings that are executed one by one.
        (Or just a string, which is then executed the same way.)
        """
        if not (type(sqlstatements) is list):
            sqlstatements = [sqlstatements]
        if self.fast:
            conn = self.conn
        else: 
            conn = sq.connect(self.dbname)
        results = []
        with conn:
            # context manager: locks the database while we execute every sql 
            # statement.
            for sqlstatement in sqlstatements:
                if self.debug:
                    print(sqlstatement)
                # in case there is reg exprs, 
                # must add a function to the connection:
                if 'regexp' in sqlstatement.lower():
                    conn.create_function("REGEXP", 2, regexp)
                
                cur = conn.cursor()
                # execute and fetch the result:
                cur.execute(sqlstatement)
                result = cur.fetchall()
                    
                results.append(result)
            # at the end, commit our changes
            conn.commit()
        if not self.fast:
            conn.close()
        if len(results) == 1:
            return results[0]
        return results
    
    
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
        """
        just a wrapper around accessing the dictionary typeToSQLiteType
        defined at the top of this file.
        """
        try:
            typ = typeToSQLiteType[typ]
        except KeyError:
            msg = f"Unknown type encountered while creating db: {typ}"
            raise NotImplementedError(msg)
        return typ


    def getTableNames(self, dbname):
        # pretty self exlpanatory: get the names of all 
        # the tables in our database.
        tabs = self.execute(dbname, 
                    "SELECT name FROM sqlite_master WHERE type='table';")
        return [t[0] for t in tabs]
    
    def getColumns(self, dbname, tablename=None):
        if not tablename:
            tablename = self.defaulttable
        return self.execute(dbname, 
                    f"select name,type from pragma_table_info('{tablename}')")
    
    def getFieldNames(self, dbname, tablename=None):
        if not tablename:
            tablename = self.defaulttable 
        return [c[0] for c in self.getColumns(dbname, tablename)]

    def getFieldTypes(self, dbname, tablename=None):
        if not tablename:
            tablename = self.defaulttable 
        return [SQLiteTypeTotype[c[1].lower()] 
                         for c in self.getColumns(dbname, tablename)]
    
    def getColumnType(self, dbname, field, tablename=None):
        if not tablename:
            tablename = self.defaulttable 
        fields = self.getFieldNames(dbname, tablename)
        types = self.getFieldTypes(dbname, tablename)
        if not field in fields:
            raise AssertionError(f"no such field ({field}) in table {tablename}")
        matchindex = fields.index(field)
        return types[matchindex]

    def create(self, dbname, fields, tablename=None, exist_ok=True):
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
            
        if tablename in self.getTableNames(dbname):
            if exist_ok:
                self.addFields(dbname, fields, tablename=tablename)
                return []
            else:
                raise RuntimeError(f"table {tablename} already exists!")
                
        cmd = f"CREATE TABLE {tablename} (recno INTEGER NOT NULL PRIMARY KEY,"
        
        
        cmd += self._formatFields(fields)
        cmd = cmd[:-1] + ")"
        return self.execute(dbname, cmd)
    
    def addFields(self, dbname, listoffields, tablename=None, exist_ok=True):
        if not tablename:
            tablename = self.defaulttable
            
        if not tablename in self.getTableNames(dbname):
            raise RuntimeError(f"table {tablename} does not exists!")
            
        alreadytherecols = self.getColumns(dbname, tablename)
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
                self.execute(dbname, f"alter table {tablename} add {name} {typ}")
                
    def dropFields(self, dbname, fields, tablename=None):
        """
        soooo sqlite 3.35 can do this. 
        But not sure we'll  have it on everyone's computer ...
        hence we copy the table without those columns, destroy the old table
        and rename the new one to the old name.
        """
        if not tablename:
            tablename = self.defaulttable
        tmptable = tablename+"___tmp___"
        allfields = self.getFieldNames(dbname, tablename)
        alltypes  = [typeToSQLiteType[t] 
                               for t in self.getFieldTypes(dbname, tablename)]
        transferfields = [f"{f} {t}" for f, t in zip(allfields,alltypes) 
                                                           if not f in fields]
        # prepare the transfer of the columns:
        transfieldstr = ','.join(transferfields)
        req2 = f'insert into {tmptable} select {transfieldstr} from {tablename}'
        # now just modify the one with the recno
        for i in range(len(transferfields)):
            if 'recno' in transferfields[i].lower():
                transferfields[i] += " NOT NULL PRIMARY KEY"
        transfieldstr = ','.join(transferfields)
        req1 = f'create table {tmptable}({transfieldstr})'
        
        req3 = f'drop table {tablename}'
        req4 = f'alter table {tmptable} rename to {tablename}'
        self.execute(dbname, [req1, req2, req3, req4])
        
        
                
    def insertBatch(self, dbname, listOfDics, tablename=None):
        if not tablename:
            tablename = self.defaulttable
            
        for dic in listOfDics:
            self.insert(dbname, dic, tablename=tablename)
        
    def insert(self, dbname, dic, tablename=None):
        if not tablename:
            tablename = self.defaulttable
        colnames, colvals = "(", "("
        for name, val in dic.items():
            colnames += f"{name},"
            # if val is None, call it NULL:
            if val is None:
                val = "NULL"
            if self.getColumnType(dbname, field=name, tablename=tablename) == 'str':
                colvals += f"'{val}',"
            else:
                colvals += f"{val},"
        colnames, colvals = colnames[:-1]+")", colvals[:-1]+")"
        cmd = f"insert into {tablename} {colnames} values {colvals}"
        return self.execute(dbname, cmd)


    def select(self, dbname, fields, searchData, filter=None, useRegExp=False, 
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
            if not str(searchstr).strip()[0] in ["=", "<", ">", "==", "!"]:
                if useRegExp and self.getColumnType(dbname, field, tablename) == "str":
                    searchstr = f" REGEXP '{searchstr}'"
                else:
                    if self.getColumnType(dbname, field, tablename) == "str":
                        searchstr = f"=='{searchstr}'"
                    else:
                        searchstr = f"=={searchstr}"
            conditions.append( f"{field}{searchstr}")
        conditions = " and ".join(conditions)
        if len(conditions) > 0:
            req += f"where {conditions} "
        
        orders = []
        for field in sortFields:
            if field in sortDesc: 
                orders.append(f"{field} DESC")
            else:
                orders.append(f"{field} ASC")
        orders = ",".join(orders)
        if len(orders) > 0:
            req += f"order by {orders} "
        result = self.execute(dbname, req)
        

        if returnType == "dict":
            if not filter:
                names = self.getFieldNames(dbname, tablename=tablename) 
            else:
                names = filter
            
            resultdic = [{name:val for name,val in zip(names, res)} for res in result]
            return resultdic
        
        elif returnType == 'report':
            """
            this part was adaped 99.9% from the KirbyBase code 
            """
            # How many records before a formfeed.
            numRecsPerPage = 0
            # Put a line of dashes between each record?
            rowSeparator = False
            delim = ' | '
            
            if not filter:
                filter = self.getFieldNames(dbname, tablename=tablename) 
            # columns of physical rows
            columns = list(zip(*[filter] + result))

            # get the maximum of each column by the string length of its 
            # items
            maxWidths = [max([len(str(item)) for item in column]) 
             for column in columns]
            # Create a string of dashes the width of the print out.
            rowDashes = '-' * (sum(maxWidths) + len(delim)*
             (len(maxWidths)-1))

            # select the appropriate justify method
            justifyDict = {'str':str.ljust,'int':str.rjust,'float':str.rjust,
             'bool':str.ljust,datetime.date:str.ljust,
             datetime.datetime:str.ljust}

            # Create a string that holds the header that will print.
            headerLine = delim.join([justifyDict[fieldType](item,width) 
             for item,width,fieldType in zip(filter,maxWidths,
            self.getFieldTypes(dbname, tablename))])

            # Create a StringIO to hold the print out.
            output=io.StringIO()

            # Variable to hold how many records have been printed on the
            # current page.
            recsOnPageCount = 0

            # For each row of the result set, print that row.
            for row in result:
                # If top of page, print the header and a dashed line.
                if recsOnPageCount == 0:
                    print(headerLine, file=output)
                    print(rowDashes, file=output)

                # Print a record.
                print(delim.join([justifyDict[fieldType](
                 str(item),width) for item,width,fieldType in 
                 zip(row,maxWidths,self.getFieldTypes(dbname))]), file=output)

                # If rowSeparator is True, print a dashed line.
                if rowSeparator: print(rowDashes, file=output)

                # Add one to the number of records printed so far on
                # the current page.
                recsOnPageCount += 1

                # If the user wants page breaks and you have printed 
                # enough records on this page, print a form feed and
                # reset records printed variable.
                if numRecsPerPage > 0 and (recsOnPageCount ==
                 numRecsPerPage):
                    print('\f', end=' ', file=output)
                    recsOnPageCount = 0
            # Return the contents of the StringIO.
            return output.getvalue()
        
        return result
    
    
    def update(self, dbname, fields, searchData, updates, filter=None, 
               useRegExp=False, tablename=None):
        if not tablename:
            tablename = self.defaulttable

        req = f"update {tablename} "
        if type(updates) is dict:
            sets = []
            for k, v in updates.items():
                if self.getColumnType(dbname, k, tablename) == "str":
                    sets.append(f"{k}='{v}'")
                else:
                    sets.append(f"{k}={v}")
            sets = ','.join(sets)
        elif type(updates) is list:
            assert type(filter) is list 
            assert len(filter) == len(updates)
            sets = []
            for k, v in zip(filter, updates):
                if self.getColumnType(dbname, k, tablename) == "str":
                    sets.append(f"{k}='{v}'")
                else:
                    sets.append(f"{k}={v}")
            sets = ','.join(sets)
        
        req += f"set {sets} "
        conditions = []
        for searchstr, field in zip(searchData, fields):
            if str(searchstr).strip() == "*":
                #joker, skip this condition.
                continue
            if not str(searchstr).strip()[0] in ["=", "<", ">", "==", "!"]:
                if useRegExp and self.getColumnType(dbname, field, tablename) == "str":
                    searchstr = f" REGEXP '{searchstr}'"
                else:
                    if self.getColumnType(dbname, field, tablename) == "str":
                        searchstr = f"=='{searchstr}'"
                    else:
                        searchstr = f"=={searchstr}"
            conditions.append( f"{field}{searchstr}")
        conditions = " and ".join(conditions)
        if len(conditions) > 0:
            req += f"where {conditions} "
        # also, kirbybase gives us the number of affected rows when 
        # doing an update. Let's do this as well:
        reqs = [req, "select total_changes()"]
        result = self.execute(dbname, reqs)
        return result[-1][0][0]
    
    
    def pack(self, dbname):
        """
        A KirbyBase method to remove the black lines from the text file.
        In the case fo an SQLite database this is not needed, but we keep it
        for retro-compatibility with the KirbyBase backend.

        """
        pass
    def validate(self, dbname):
        """
        same as the "pack" method above. 
        """
        pass
    
    
# KBError Class -- copying from KirbyBase.
class KBError(Exception):
    """Exception class for Database Management System.

    Public Methods:
        __init__ - Create an instance of exception.
    """
    #----------------------------------------------------------------------
    # init
    #----------------------------------------------------------------------
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

    # I overrode repr so I could pass error objects from the server to the
    # client across the network.
    def __repr__(self):
        format = """KBError("%s")"""
        return format % (self.value)
    
    

if __name__ == "__main__":
    minimaldbfields = ['imgname:str', 'treatme:bool', 'gogogo:bool', 
                       'whynot:str', 'testlist:bool', 'testcomment:str',
                       'telescopename:str', 'setname:str', 'rawimg:str',
                       'scalingfactor:float', 'pixsize:float','date:str',
                       'datet:str','jd:str','mjd:float',
                       'telescopelongitude:str', 'telescopelatitude:str', 
                       'telescopeelevation:float', 'exptime:float',
                       'gain:float', 'readnoise:float', 'rotator:float', 
                       'saturlevel:float',
                       'preredcomment1:str', 'preredcomment2:str', 
                       'preredfloat1:float', 'preredfloat2:float']
    dbname = "toast2.db"
    db = KirbyBase(imgdb)
    db.create(dbname, minimaldbfields)
    db.addFields(dbname, ["imgname:str"])
    
    db.insert(dbname, {'imgname':'wow', 'gogogo':True, 'pixsize':0.25})
    
    print(db.select(dbname, ["recno"], ["*"], 
                    filter=["recno", "imgname", "gogogo", "pixsize"], 
                    returnType='report'))
    # db.dropFields(dbname, ["pixsize"])
    # print(db.select(dbname, ["recno"], ["*"], 
                    # filter=["recno", "imgname", "gogogo"], returnType='report'))
    # assert "pixsize" not in db.getFieldNames(dbname)
    # db.create(dbname, minimaldbfields)
    # assert "pixsize" in db.getFieldNames(dbname)
    # print(db.select(dbname, ["recno"], ["*"], 
    #                 filter=["recno", "imgname", "gogogo", "pixsize"], returnType='report'))
    # db.insertBatch(dbname, [
    #     {'imgname':'wow', 'gogogo':True, 'pixsize':0.25},
    #     {'imgname':'wow2', 'gogogo':True, 'pixsize':0.25},
    #     {'imgname':'wow3', 'gogogo':True, 'pixsize':0.25},
    #     {'imgname':'wow4', 'gogogo':True, 'pixsize':0.25},
    #     {'imgname':'wow5', 'gogogo':True, 'pixsize':0.25},
    #     {'imgname':'wow', 'gogogo':True, 'pixsize':0.25},
    #     {'imgname':'wow', 'gogogo':True, 'pixsize':0.25},
    #     {'imgname':'wow', 'gogogo':True, 'pixsize':0.25},
    #     {'imgname':'wow', 'gogogo':True, 'pixsize':0.25},
    #     ])
    print(db.select(dbname, ["recno"], ["*"], 
                    filter=["recno", "imgname", "gogogo", "gain"], returnType='report'))
    db.update(dbname, ["recno"], [5], {'gain':0.2})
    #%%
    print(db.select(dbname, ["recno"], ["*"], 
                    filter=["recno", "imgname", "gogogo", "gain"], returnType='report'))
