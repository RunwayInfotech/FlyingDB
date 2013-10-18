'''
    Copyright (C) 2013 Paul Lee
    
    Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
    documentation files (the "Software"), to deal in the Software without restriction, including without limitation
    the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and
    to permit persons to whom the Software is furnished to do so, subject to the following conditions:
    
    The above copyright notice and this permission notice shall be included in all copies or substantial portions of
    the Software.
    
    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
    THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
    TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
    
'''

# ---------------------------------------------------------------------
# FlyingDB
#
# Paul Lee
# 10/18/2013
#
# ---------------------------------------------------------------------

import sqlite3 as lite
import sys
import os
import shutil


GENERATED_DIR = 'generated/'
ANDROID_DIR = GENERATED_DIR + 'android/'
IOS_DIR = GENERATED_DIR + 'ios/'

# ---------------------------------------------------------------------
#
#  Extract database meta-data
#
#
# ---------------------------------------------------------------------

# Static Column Indexes for table data returned
COL_ORDER_INDEX = 0
COL_NAME_INDEX = 1
COL_TYPE_INDEX = 2

def getTableData(dbName, tableName):
    con = lite.connect(dbName)
    with con:
        cur = con.cursor()
        cur.execute('PRAGMA table_info(' + tableName + ')')
        data = cur.fetchall()
        return data

def getTableNames(dbName):
    tableList = []
    con = lite.connect(dbName)
    with con:
        cur = con.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        rows = cur.fetchall()
        for row in rows:
            tableList.append(row[0])
    return tableList


# ---------------------------------------------------------------------
#
#  Create JAVA POJOs
#
#
# ---------------------------------------------------------------------
def createJavaClass(prefix, tableName, tableData):
    outFile = open(ANDROID_DIR + prefix + tableName + '.java', 'w')
    outFile.write('//**********************************************************\n')
    outFile.write('//************** AUTOGENERATED with FLYINGDB ***************\n')
    outFile.write('//**********************************************************\n\n')
    outFile.write('package com.flyingboba.flyingdb;\n\n\n')
    outFile.write('public class ' + prefix + tableName + ' {\n')
    
    memberDeclarations = ''
    constructorParams = ''
    constructorInitStatements = ''
    javaGets = ''
    javaSets = ''
    for d in tableData:
        memberDeclarations += '\tprivate String ' + objCFormat(tableName, d[COL_NAME_INDEX]) + ';\n'
        javaGets += createJavaGet(objCFormat(tableName, d[COL_NAME_INDEX]))
        javaSets += createJavaSet(objCFormat(tableName, d[COL_NAME_INDEX]))
        constructorInitStatements += '\t\tset' + capitalize(objCFormat(tableName, d[COL_NAME_INDEX])) + '(' + objCFormat(tableName, d[COL_NAME_INDEX]) + ');\n'
    
    for i in range(0, len(tableData)-1):
        constructorParams += 'String ' +  objCFormat(tableName, tableData[i][COL_NAME_INDEX]) + ', '
    constructorParams += 'String ' +  objCFormat(tableName, tableData[len(tableData)-1][COL_NAME_INDEX])
    
    outFile.write('\n')
    
    outFile.write(memberDeclarations)
    
    outFile.write('\n')
    
    outFile.write('\tpublic ' + prefix + tableName + '(' + constructorParams + ') {\n')
    outFile.write(constructorInitStatements)
    outFile.write('\t}\n')
    
    outFile.write('\n')
    
    outFile.write(javaSets)
    outFile.write(javaGets)
    
    outFile.write('}')
    outFile.close()

def createJavaGet(memberName):
    getString = ''
    getString += '\tpublic String get' + capitalize(memberName) + '() {\n'
    getString += '\t\treturn ' + memberName + ';\n'
    getString += '\t}\n\n'
    return getString

def createJavaSet(memberName):
    setString = ''
    setString += '\tpublic void set' + capitalize(memberName) + '(String ' + memberName + ') {\n'
    setString += '\t\tthis.' + memberName + ' = ' + memberName + ';\n'
    setString += '\t}\n\n'
    return setString

# ---------------------------------------------------------------------
#
#  Create ObjC POJOs
#
#
# ---------------------------------------------------------------------
def createObjCClass(prefix, tableName, tableData):
    outFile = open(IOS_DIR + prefix + tableName+'.h', 'w')
    outFile.write('//**********************************************************\n')
    outFile.write('//************** AUTOGENERATED with FLYINGDB ***************\n')
    outFile.write('//**********************************************************\n\n')
    outFile.write('#import <Foundation/Foundation.h>\n\n')
    outFile.write('@interface ' + prefix + tableName + ' : NSObject\n\n')
    for d in tableData:
        outFile.write('@property (strong) NSString* ' + objCFormat(tableName, d[COL_NAME_INDEX]) + ';\n')
    outFile.write('\n')
    outFile.write(' - (id) init;\n')
    initWithString = ' - (id) initWith' + capitalize(objCFormat(tableName,tableData[0][COL_NAME_INDEX])) + ': (NSString*) param' + capitalize(objCFormat(tableName,tableData[0][COL_NAME_INDEX]))
    for i in range(1, len(tableData)):
        initWithString += ' with' + capitalize(objCFormat(tableName,tableData[i][COL_NAME_INDEX])) + ': (NSString*) param' + capitalize(objCFormat(tableName,tableData[i][COL_NAME_INDEX]))
    initWithString += ';\n'
    outFile.write(initWithString)
    outFile.write('\n@end')
    outFile.close()
    
    # Create the .m file
    outFile = open(IOS_DIR + prefix + tableName+'.m', 'w')
    outFile.write('//**********************************************************\n')
    outFile.write('//************** AUTOGENERATED with FLYINGDB ***************\n')
    outFile.write('//**********************************************************\n\n')
    outFile.write('#import "' + prefix + tableName + '.h"\n\n')
    outFile.write('@implementation ' + prefix + tableName + '\n\n')
    for d in tableData:
        outFile.write('@synthesize ' + objCFormat(tableName,d[COL_NAME_INDEX]) + ';\n')
    outFile.write('\n')
    outFile.write('- (id) init\n')
    outFile.write('{\n')
    initWithStringNil = 'initWith' + capitalize(objCFormat(tableName, tableData[0][COL_NAME_INDEX])) + ': nil'
    for i in range(1, len(tableData)):
        initWithStringNil += ' with' + capitalize(objCFormat(tableName, tableData[i][COL_NAME_INDEX])) + ': nil'
    outFile.write('\treturn [self ' + initWithStringNil + '];\n')
    outFile.write('}\n')
    
    outFile.write(initWithString)
    outFile.write('{\n')
    outFile.write('\tself = [super init];\n')
    outFile.write('\tif(self)\n')
    outFile.write('\t{\n')
    for d in tableData:
        outFile.write('\t\t' + objCFormat(tableName, d[COL_NAME_INDEX]) + ' = ' + 'param' + capitalize(objCFormat(tableName, d[COL_NAME_INDEX])) + ';\n')
    outFile.write('\t}\n')
    outFile.write('\treturn self;\n')
    outFile.write('}\n')
    outFile.write('\n@end')
    
    outFile.close()

# ---------------------------------------------------------------------
#
#  Utility functions
#
#
# ---------------------------------------------------------------------

# id is reserved in objective c
# if a column is named id, then rename so that it becomes prefix + 'Id'
def objCFormat(prefix, string) :
    if string=='id' :
        return decapitalize(prefix) + 'Id'
    return string

# Return the string with the first letter lower cased
def decapitalize(string):
    return string[0].lower() + string[1:]

# Return the string with the first letter upper cased
def capitalize(string):
    return string[0].upper() + string[1:]


# ---------------------------------------------------------------------
#
#  Create Android Query Methods
#
#
# ---------------------------------------------------------------------


def createJavaQueryMethods(prefix, tableName, tableData):
    queryMethods = '\n\n\t// -----------------------------------------------------------------------------'
    queryMethods += '\n\t// ' + tableName + ' Query Methods'
    queryMethods += '\n\t// -----------------------------------------------------------------------------'
    queryMethods += '\n' + createJavaSelectMethods(prefix, tableName, tableData)
    queryMethods += '\n' + createJavaInsertMethods(prefix, tableName, tableData)
    queryMethods += '\n' + createJavaUpdateMethods(prefix, tableName, tableData)
    queryMethods += '\n' + createJavaDeleteMethods(tableName)
    return queryMethods

def createJavaSelectMethods(prefix, tableName, tableData):
    queryString = 'SELECT '
    for d in tableData:
        queryString += d[COL_NAME_INDEX] +', '
    queryString = queryString.rstrip(', ')
    templateFile = open('Templates/Java/Select.txt', 'r')
    templateString = templateFile.read()
    templateFile.close()
    
    templateString = templateString.replace('[POJO]', prefix + tableName)
    templateString = templateString.replace('[TABLE_NAME_CAPITAL]', capitalize(tableName))
    templateString = templateString.replace('[SELECT_QUERY]', queryString)
    templateString = templateString.replace('[TABLE_NAME]', tableName)
    
    newPojoString = 'new ' + prefix + tableName + '('
    for i in range(0, len(tableData)):
        newPojoString += 'result.getString(' + str(i) + '), '
    newPojoString = newPojoString.rstrip(', ') + ')'
    templateString = templateString.replace('[NEW_POJO]', newPojoString)
    
    return templateString

def createJavaInsertMethods(prefix, tableName, tableData):
    fields = ''
    values = ''
    pojoMembers = ''
    for d in tableData:
        # Do not set key on insert
        if d[5] != 1:
            fields += 'String a' + capitalize(d[COL_NAME_INDEX]) + ', '
            values += 'values.put("' + d[COL_NAME_INDEX] + '", a' + capitalize(d[COL_NAME_INDEX]) + ');\n\t\t'
            pojoMembers += 'pojo.get' + capitalize(objCFormat(tableName, d[COL_NAME_INDEX])) + '(), '
    fields = fields.rstrip(', ')
    pojoMembers = pojoMembers.rstrip(', ')
    templateFile = open('Templates/Java/Insert.txt', 'r')
    templateString = templateFile.read()
    templateFile.close()
    templateString = templateString.replace('[TABLE_NAME_CAPITAL]', capitalize(tableName))
    templateString = templateString.replace('[TABLE_NAME]', tableName)
    templateString = templateString.replace('[TABLE_FIELDS]', fields)
    templateString = templateString.replace('[VALUES]', values)
    
    pojoInsertString = '\n\n\tpublic long add' + capitalize(tableName) + '(' + prefix + tableName + ' pojo) {'
    pojoInsertString += '\n\t\treturn add' + capitalize(tableName) + '(' + pojoMembers + ');'
    pojoInsertString += '\n\t}'
    
    templateString += pojoInsertString
    return templateString

def createJavaUpdateMethods(prefix, tableName, tableData):
    fields = ''
    values = ''
    pojoMembers = ''
    for d in tableData:
        # Do not set key on update
        if d[5] != 1:
            fields += 'String a' + capitalize(d[COL_NAME_INDEX]) + ', '
            values += 'values.put("' + d[COL_NAME_INDEX] + '", a' + capitalize(d[COL_NAME_INDEX]) + ');\n\t\t'
            pojoMembers += 'pojo.get' + capitalize(objCFormat(tableName, d[COL_NAME_INDEX])) + '(), '
    fields = fields.rstrip(', ')
    pojoMembers = pojoMembers.rstrip(', ')
    templateFile = open('Templates/Java/Update.txt', 'r')
    templateString = templateFile.read()
    templateFile.close()
    templateString = templateString.replace('[TABLE_NAME_CAPITAL]', capitalize(tableName))
    templateString = templateString.replace('[TABLE_NAME]', tableName)
    templateString = templateString.replace('[TABLE_FIELDS]', fields)
    templateString = templateString.replace('[VALUES]', values)
    
    pojoUpdateString = '\n\n\tpublic long update' + capitalize(tableName) + '(' + prefix + tableName + ' pojo, String fieldName, String fieldValue) {'
    pojoUpdateString += '\n\t\treturn update' + capitalize(tableName) + '(' + pojoMembers + ', fieldName, fieldValue);'
    pojoUpdateString += '\n\t}'
    
    templateString += pojoUpdateString
    return templateString

def createJavaDeleteMethods(tableName):
    templateFile = open('Templates/Java/Delete.txt', 'r')
    templateString = templateFile.read()
    templateFile.close()
    templateString = templateString.replace('[TABLE_NAME]', tableName)
    templateString = templateString.replace('[TABLE_NAME_CAPITAL]', capitalize(tableName))
    
    return templateString

def setupJavaDatabaseAdapter(queryMethods):
    templateFile = open('Templates/Java/DatabaseAdapter.txt', 'r')
    dbAdapterFile = open(ANDROID_DIR + '/DatabaseAdapter.java', 'w')
    templateString = templateFile.read()
    templateString = templateString.replace('[QUERY_METHODS]', queryMethods)
    dbAdapterFile.write(templateString)
    templateFile.close()
    dbAdapterFile.close()

def setupJavaDatabaseHelper(dbName, dbVersion, dbPath):
    templateFile = open('Templates/Java/DatabaseHelper.txt', 'r')
    dbHelperFile = open(ANDROID_DIR + '/DatabaseHelper.java', 'w')
    templateString = templateFile.read()
    templateString = templateString.replace('[DATABASE_FILE_NAME]', dbName)
    templateString = templateString.replace('[DATABASE_VERSION]', dbVersion)
    templateString = templateString.replace('[DATABASE_PATH]', dbPath)
    dbHelperFile.write(templateString)
    templateFile.close()
    dbHelperFile.close()

# ---------------------------------------------------------------------
#
#  Create iOS Query Methods
#
#
# ---------------------------------------------------------------------

def createObjCQueryMethods(prefix, tableName, tableData):
    queryMethods = '\n\n// -----------------------------------------------------------------------------'
    queryMethods += '\n// ' + tableName + ' Query Methods'
    queryMethods += '\n// -----------------------------------------------------------------------------'
    queryMethods += '\n' + createObjCSelectMethods(prefix, tableName, tableData)
    queryMethods += '\n' + createObjCInsertMethods(prefix, tableName, tableData)
    queryMethods += '\n' + createObjCUpdateMethods(prefix, tableName, tableData)
    queryMethods += '\n' + createObjCDeleteMethods(tableName)
    return queryMethods

def createObjCQueryPrototypes(prefix, tableName, tableData):
    prototypes = '\n\n// -----------------------------------------------------------------------------'
    prototypes += '\n// ' + tableName + ' Query Method Prototypes'
    prototypes += '\n// -----------------------------------------------------------------------------'
    prototypes += '\n' + createObjCSelectPrototypes(prefix, tableName, tableData)
    prototypes += '\n' + createObjCInsertPrototypes(prefix, tableName, tableData)
    prototypes += '\n' + createObjCUpdatePrototypes(prefix, tableName, tableData)
    prototypes += '\n' + createObjCDeletePrototypes(tableName)
    return prototypes

def createObjCSelectMethods(prefix, tableName, tableData):
    queryString = 'SELECT '
    for d in tableData:
        queryString += d[COL_NAME_INDEX] +', '
    queryString = queryString.rstrip(', ')
    templateFile = open('Templates/ObjC/Select.txt', 'r')
    templateString = templateFile.read()
    templateFile.close()
    
    templateString = templateString.replace('[POJO]', prefix + tableName)
    templateString = templateString.replace('[TABLE_NAME_CAPITAL]', capitalize(tableName))
    templateString = templateString.replace('[SELECT_QUERY]', queryString)
    templateString = templateString.replace('[TABLE_NAME]', tableName)
    
    newPojoString = '[[' + prefix + tableName + ' alloc] \n\t\t\t\tinitWith' + capitalize(objCFormat(tableName, tableData[0][COL_NAME_INDEX])) + ':'
    newPojoString += '[[NSString alloc] initWithUTF8String: (char*) sqlite3_column_text(statement, 0)]'
    for i in range(1, len(tableData)):
        newPojoString += '\n\t\t\t\twith' + capitalize(objCFormat(tableName, tableData[i][COL_NAME_INDEX])) + ':'
        newPojoString += '[[NSString alloc] initWithUTF8String: (char*) sqlite3_column_text(statement, ' + str(i) + ')]'
    newPojoString += ']'
    templateString = templateString.replace('[NEW_POJO]', newPojoString)
    
    return templateString

def createObjCInsertMethods(prefix, tableName, tableData):
    fields = ''
    values = ''
    params = ''
    maskList = ''
    firstTime = True
    for d in tableData:
        # Do not set key on insert
        if d[5] != 1:
            if firstTime == True:
                params += 'With' + capitalize(d[COL_NAME_INDEX]) + ": (NSString*) a" +  capitalize(d[COL_NAME_INDEX]) + " "
                firstTime = False
            else:
                params += 'with' + capitalize(d[COL_NAME_INDEX]) + ": (NSString*) a" +  capitalize(d[COL_NAME_INDEX]) + " "
            maskList += '\'%@\', '
            fields += d[COL_NAME_INDEX] + ', '
            values += 'a' + capitalize(d[COL_NAME_INDEX]) + ', '
    fields = fields.rstrip(', ')
    values = values.rstrip(', ')
    maskList = maskList.rstrip(', ')
    templateFile = open('Templates/ObjC/Insert.txt', 'r')
    templateString = templateFile.read()
    templateFile.close()
    templateString = templateString.replace('[TABLE_NAME_CAPITAL]', capitalize(tableName))
    templateString = templateString.replace('[PARAMS]', params)
    templateString = templateString.replace('[TABLE_NAME]', tableName)
    templateString = templateString.replace('[TABLE_FIELDS]', fields)
    templateString = templateString.replace('[@LIST]', maskList)
    templateString = templateString.replace('[VALUES]', values)
    return templateString

def createObjCUpdateMethods(prefix, tableName, tableData):
    fields = ''
    values = ''
    params = ''
    firstTime = True
    for d in tableData:
        # Do not set key on insert
        if d[5] != 1:
            if firstTime == True:
                params += 'With' + capitalize(d[COL_NAME_INDEX]) + ": (NSString*) a" +  capitalize(d[COL_NAME_INDEX]) + " "
                firstTime = False
            else:
                params += 'with' + capitalize(d[COL_NAME_INDEX]) + ": (NSString*) a" +  capitalize(d[COL_NAME_INDEX]) + " "
            fields += d[COL_NAME_INDEX] + '=\'%@\', '
            values += 'a' + capitalize(d[COL_NAME_INDEX]) + ', '
    fields = fields.rstrip(', ')
    values = values.rstrip(', ')
    templateFile = open('Templates/ObjC/Update.txt', 'r')
    templateString = templateFile.read()
    templateFile.close()
    templateString = templateString.replace('[TABLE_NAME_CAPITAL]', capitalize(tableName))
    templateString = templateString.replace('[PARAMS]', params)
    templateString = templateString.replace('[TABLE_NAME]', tableName)
    templateString = templateString.replace('[TABLE_FIELDS]', fields)
    templateString = templateString.replace('[VALUES]', values)
    return templateString


def createObjCDeleteMethods(tableName):
    templateFile = open('Templates/ObjC/Delete.txt', 'r')
    templateString = templateFile.read()
    templateFile.close()
    templateString = templateString.replace('[TABLE_NAME_CAPITAL]', capitalize(tableName))
    templateString = templateString.replace('[TABLE_NAME]', tableName)
    return templateString

def createObjCSelectPrototypes(prefix, tableName, tableData):
    templateString = '+ (NSMutableArray *) get[TABLE_NAME_CAPITAL]ListWithFieldName: (NSString*) fieldName withFieldValue: (NSString*) fieldValue withOrderBy: (NSString*) orderBy;'
    templateString = templateString.replace('[TABLE_NAME_CAPITAL]', capitalize(tableName))
    return templateString

def createObjCInsertPrototypes(prefix, tableName, tableData):
    templateString = '+ (NSString *) add[TABLE_NAME_CAPITAL][PARAMS];'
    params = ''
    firstTime = True
    for d in tableData:
        # Do not set key on insert
        if d[5] != 1:
            if firstTime == True:
                params += 'With' + capitalize(d[COL_NAME_INDEX]) + ": (NSString*) a" +  capitalize(d[COL_NAME_INDEX]) + " "
                firstTime = False
            else:
                params += ' with' + capitalize(d[COL_NAME_INDEX]) + ": (NSString*) a" +  capitalize(d[COL_NAME_INDEX])
    templateString = templateString.replace('[TABLE_NAME_CAPITAL]', capitalize(tableName))
    templateString = templateString.replace('[PARAMS]', params)
    return templateString

def createObjCUpdatePrototypes(prefix, tableName, tableData):
    templateString = '+ (int) update[TABLE_NAME_CAPITAL][PARAMS] withFieldName: (NSString *) fieldName withFieldValue: (NSString *) fieldValue;'
    params = ''
    firstTime = True
    for d in tableData:
        # Do not set key on insert
        if d[5] != 1:
            if firstTime == True:
                params += 'With' + capitalize(d[COL_NAME_INDEX]) + ": (NSString*) a" +  capitalize(d[COL_NAME_INDEX]) + " "
                firstTime = False
            else:
                params += ' with' + capitalize(d[COL_NAME_INDEX]) + ": (NSString*) a" +  capitalize(d[COL_NAME_INDEX])
    templateString = templateString.replace('[TABLE_NAME_CAPITAL]', capitalize(tableName))
    templateString = templateString.replace('[PARAMS]', params)
    return templateString

def createObjCDeletePrototypes(tableName):
    templateString = '+ (int) remove[TABLE_NAME_CAPITAL]WithFieldName: (NSString *) fieldName withFieldValue: (NSString *) fieldValue;'
    templateString = templateString.replace('[TABLE_NAME_CAPITAL]', capitalize(tableName))
    return templateString


def setupObjCDatabaseAdapterH(importFiles, queryPrototypes):
    templateHFile = open('Templates/ObjC/DatabaseAdapterH.txt', 'r')
    dbAdapterHFile = open(IOS_DIR + '/DatabaseAdapter.h', 'w')
    templateString = templateHFile.read()
    templateString = templateString.replace('[IMPORTS]', importFiles)
    templateString = templateString.replace('[QUERY_METHODS]', queryPrototypes)
    dbAdapterHFile.write(templateString)
    templateHFile.close()
    dbAdapterHFile.close()


def setupObjCDatabaseAdapterM(dbName, importFiles, queryMethods):
    templateMFile = open('Templates/ObjC/DatabaseAdapterM.txt', 'r')
    dbAdapterMFile = open(IOS_DIR + '/DatabaseAdapter.m', 'w')
    templateString = templateMFile.read()
    templateString = templateString.replace('[IMPORTS]', importFiles)
    templateString = templateString.replace('[DATABASE_FILE_NAME]', dbName)
    templateString = templateString.replace('[DATABASE_FILE_NAME_MINUS_EXTENSION]', os.path.splitext(dbName)[0])
    templateString = templateString.replace('[QUERY_METHODS]', queryMethods)
    dbAdapterMFile.write(templateString)
    templateMFile.close()
    dbAdapterMFile.close()


# ---------------------------------------------------------------------
#
#  Main function that calls all of the other functions
#
#
# ---------------------------------------------------------------------
def fly(dbName, prefix):
    
    if not os.path.exists(GENERATED_DIR):
        os.makedirs(GENERATED_DIR)
    else:
        shutil.rmtree(GENERATED_DIR)
    if not os.path.exists(ANDROID_DIR):
        os.makedirs(ANDROID_DIR)
    if not os.path.exists(IOS_DIR):
        os.makedirs(IOS_DIR)
    
    tables =  getTableNames(dbName)
    tableNames = ''
    javaQueryMethods = ''
    objCQueryMethods = ''
    objCQueryPrototypes = ''
    importFiles = ''
    
    for tableName in tables:
        tableData = getTableData(dbName, tableName)
        createJavaClass(prefix, tableName, tableData)
        createObjCClass(prefix, tableName, tableData)
        tableNames += '"' + tableName + '",'
        javaQueryMethods += createJavaQueryMethods(prefix, tableName, tableData)
        objCQueryMethods += createObjCQueryMethods(prefix, tableName, tableData)
        objCQueryPrototypes += createObjCQueryPrototypes(prefix, tableName, tableData)
        importFiles += '#import "' + prefix + tableName + '.h"\n';
    tableNames = tableNames.rstrip(',')
    
    setupJavaDatabaseAdapter(javaQueryMethods)
    setupJavaDatabaseHelper(dbName, '1', '/data/data/COM.YOUR.PACKAGE.NAME/databases/')
    
    setupObjCDatabaseAdapterH(importFiles, objCQueryPrototypes)
    setupObjCDatabaseAdapterM(dbName, importFiles, objCQueryMethods)


if len(sys.argv)<2:
    print 'Usage --  flyingdb.py sqliteFileName optionalClassPrefix\n\n'
    print 'Or\n\n'
    print 'flyingdb.py sqliteFileName'
elif len(sys.argv)==3:
    fly(sys.argv[1], sys.argv[2])
elif len(sys.argv)==2:
    fly(sys.argv[1],'')