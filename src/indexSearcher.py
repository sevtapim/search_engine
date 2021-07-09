"""
Author: Sevtap Fernengel
File name: indexSearcher.py
Description: this file contains the code to search keywords
using the index file index.txt

Usage: to start a new session simply execute

python3.2 indexSearcher.py

During a session you can ask to the system things like:

1. AND(teacher NOT(OR(student students)))
2. AND(multimedia NOT(megabytes))
3. AND(students)
4. OR(teachers)

"""
import re
import copy

class InvalidQuery(Exception):
    '''
    Class used when the query validation fails and
    an exception of type InvalidQuery is raised. '''

    #CONSTRUCTOR
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class Engine:

    ''' The Engine class is instantiated only once during a session.
    The Engine reads the index file and returns the matching document ids
    Attributes: indexDB '''

    #CONSTRUCTOR
    def __init__(self):
        ''' Used to load the index file into memory '''
        globalIndex = dict()
        docIndex = None
        with open('index.txt') as indexFile:
            currentDocId = ''
            for line in indexFile:
                docId, dummy, word = line.split()
                if currentDocId != docId:
                    currentDocId = docId
                    docIndex = dict()
                    globalIndex[currentDocId] = docIndex
                docIndex[word] = "True"
        self.indexDB = globalIndex

    def searchQuery(self, queryObj):
        ''' Given a search query, this function goes through the whole list of
        documents in indexDB and checks if a document fulfills the search criteria;
        if yes, then document id is added to the result list.
        At the end the result list is sent back. '''

        matchList = []

        for docId, docIndex in self.indexDB.items():
            if BooleanProcessor.process(queryObj.translate(docIndex)) == "True":
                matchList.append(docId)

        return matchList

class Query():
    ''' This class is used for query related pre-processing and validation.
    Our search queries are given in a special format using boolean operators
    (AND, OR, NOT). The queries may contain nested parentheses to allow for
     complex queries. Therefore this class is used for:
    1. converting the string query into tokens
    2. validating the search query
    3. translating the search query into True, False statements '''

    def __init__(self, query):
        ''' During initialization, we perform reformatting and tokenization. '''
        self.qStr = query
        self.query = query
        self.reformat()
        self.tokens = self.tokenize()

    def __str__(self):
        return self.query

    def validate(self):
        ''' We check if the given query contains balanced number
        of parentheses, if not then an InvalidQuery exception is raised. '''
        #ideally this method should contain lots of checks
        pStack = []
        tokens = copy.deepcopy(self.tokens)
        while tokens:
            nextSymbol = tokens.pop()
            if nextSymbol == '(':
                pStack.append('(')
            elif nextSymbol == ')':
                if pStack: pStack.pop()
        if pStack:
            raise InvalidQuery("Unbalanced parentheses in your query ## {0} ##".format(self.qStr))

    def reformat(self):
        ''' When tokenizing the string query, we make use of parentheses,
        wherever we see a parentheses, we add space around it,
        so that str.split function can deliver us the tokens. '''
        par = "("
        nPar = " ( "
        rPar = ')'
        nRPar = ' ) '
        self.query = self.query.replace(par, nPar).replace(rPar, nRPar)

    def tokenize(self):
        ''' Returns a list of tokens, this way the following query,
        AND(OR(students teachers) NOT(music))
        turns into a list of tokens in reverse order for easy processing:
        [), ), music, (, NOT, ), teachers, students, (, OR, (, AND] '''
        return list(reversed(self.query.split()))

    def translate(self, vocabulary):
        ''' This function goes through the tokens and for each keyword in the
        search query like students or teachers, checks if this keyword exists in the
        dictionary of a document, and if it does it replaces the keyword with
        True otherwise with False.
        So for a given tokens list:
        [), ), music, (, NOT, ), teachers, students, (, OR, (, AND]
        The output might look like:
        [), ), True, (, NOT, ), False, False, (, OR, (, AND] '''

        keywordPattern = re.compile(r'(AND|OR|NOT|\(|\))')
        tokens = copy.deepcopy(self.tokens)
        for i, token in enumerate(tokens):
            if not keywordPattern.match(token):
                tokens[i] = vocabulary.get(token, "False")
        return tokens

class BooleanProcessor():
    ''' This class is used for processing boolean statements in this format
    AND(True False) or complex forms like AND(True OR(False True)).
    To process boolean operators we use the stack data type, the stack contains
    the operators and operands for the operation. After executing once boolena
    operator, the result is pushed back to the stack. Once we are done with the
    processing the result resides on top of the stack'''

    @staticmethod
    def process(tokens):
        ''' We are given the tokens. While reading next token, we create our
        operation stack, once we have all the data for a partial processing
        we use the sub functions to perform either an AND, OR, NOT opetation.'''

        def doAND(stack):
            ''' This code finds the result of an AND operation. If we are given,
            AND(X) then this is evaluated as AND(X True)'''
            result = True
            nextSymbol = stack.pop()
            while nextSymbol != "(":
                result = result and {"True":True, "False":False}[nextSymbol]
                nextSymbol = stack.pop()
            stack.append(str(result))

        def doOR(stack):
            ''' This code finds the result of an OR operation. If we are given,
            OR(X) then this is evaluated as OR(X False)'''
            result = False
            nextSymbol = stack.pop()
            while nextSymbol != "(":
                result = result or {"True":True, "False":False}[nextSymbol]
                nextSymbol = stack.pop()
            stack.append(str(result))

        def doNOT(stack):
            ''' This code finds the result of a NOT operation, if we are given,
            NOT( X Y Z) this will be interpreted as NOT(AND(X Y Z))
            '''
            result = True
            nextSymbol = stack.pop()
            while nextSymbol != "(":
                result = result and {"True":True, "False":False}[nextSymbol]
                nextSymbol = stack.pop()
            result = not result
            stack.append(str(result))

        opStack = []
        operationToPerform = tokens.pop()
        while tokens:
            activeToken = tokens.pop()
            if activeToken == "AND" or activeToken == "OR" or activeToken == "NOT":
                tokens.append(activeToken)
                res = BooleanProcessor.process(tokens)
                opStack.append(res)
            elif activeToken == ")":
                if operationToPerform == "AND":
                    doAND(opStack)
                elif operationToPerform == "OR":
                    doOR(opStack)
                elif operationToPerform == "NOT":
                    doNOT(opStack)
                return opStack.pop()
            else:
                opStack.append(activeToken)
        return opStack.pop()

class UI:
    ''' This class is use for interacting with the user.
    It has a reference to the engine. This way it can submit the search queries to the engine
    and gather the results and preent them to the user

    Attributes:
    engine
    '''

    #CONSTRUCTOR
    def __init__(self):
        # creates the engine
        self.engine = Engine()

    def sayHello(self):
        ''' Used for greeting the user when the session starts.'''

        print('*****************************************************************')
        print('* Welcome to the Python Christmas Project, Simple Search Engine *')
        print('*****************************************************************')

    def sayBye(self):
        ''' Used for indicating that the session has ended. '''
        print('***************************************')
        print('* Thanks for using our search engine! *')
        print('* Bye :)                              *')
        print('***************************************')

    def main(self):
        ''' This is the main loop, where when the session starts. As long as
         the user does not press ENTER the session continues. During a session
         a query is read, validated if the validation succeeds the query is searched
         using the engine.'''

        self.sayHello()
        while True:
            print('\nPlease enter your search query, press ENTER to quit')
            query = input('Query >> ')
            if query == '':
                break
            queryObj = Query(query)
            try:
                queryObj.validate()
            except InvalidQuery as iq:
                print(iq)
            else:
                try:
                    results = self.engine.searchQuery(queryObj)
                    print('In total {0} documents meet your criteria:\n'.format(len(results)))
                    for r in results:
                        print(r)
                except Exception:
                    print('Unable to process this query {0}'.format(query))
        self.sayBye()
        

if __name__ == '__main__':
    ui = UI()
    ui.main()
