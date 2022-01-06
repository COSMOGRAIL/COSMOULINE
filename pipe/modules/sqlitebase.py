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

import re, datetime, io

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

DEBUG = False

class SQLInterface():
    def __init__(self, path):
        self.path = path
        self.defaulttable = "imgdb"
        
    def __str__(self):
        return f"sqlite3 database at {self.path}"
    
    def execute(self, sqlstatements):
        if not (type(sqlstatements) is list):
            sqlstatements = [sqlstatements]
        
        conn = sq.connect(self.path)
        results = []
        for sqlstatement in sqlstatements:
            if DEBUG:
                print(sqlstatement)
            # in case there is reg exprs, must add a function to the connection:
            if 'regexp' in sqlstatement.lower():
                conn.create_function("REGEXP", 2, regexp)
            with conn:
                cur = conn.cursor()

                cur.execute(sqlstatement)
                result = cur.fetchall()
            results.append(result)
        conn.commit()
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
                for field in fields:
                    self.addFields(fields, tablename=tablename)
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
                
    def dropFields(self, fields, talbename=None):
        """
        soooo sqlite 3.35 can do this. But not sure we'll  have it on everyone's computer ...
        hence we copy the table without those columns, destroy the old table
        and rename the new one to the old name.
        """
        if not talbename:
            tablename = self.defaulttable
        tmptable = tablename+"___tmp___"
        allfields = self.getFieldNames(tablename)
        alltypes  = [typeToSQLiteType[t] for t in self.getFieldTypes(tablename)]
        transferfields = [f"{f} {t}" for f, t in zip(allfields,alltypes) if not f in fields]
        
        transfieldstr = ','.join(transferfields)
        req1 = f'create table {tmptable}({transfieldstr})'
        req2 = f'insert into {tmptable} select {transfieldstr} from {tablename}'
        req3 = f'drop table {tablename}'
        req4 = f'alter table {tmptable} rename to {tablename}'
        self.execute([req1, req2, req3, req4])
        
        
                
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
        result = self.execute(req)
        

        if returnType == "dict":
            if not filter:
                names = self.getFieldNames(tablename=tablename) 
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
                filter = self.getFieldNames(tablename=tablename) 
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
            self.getFieldTypes(tablename))])

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
                 zip(row,maxWidths,self.getFieldTypes())]), file=output)

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
    