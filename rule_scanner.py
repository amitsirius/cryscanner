from pyparsing import *
from order import Order
from object import Object 
from constraint import Constraint
from forbidden import Forbidden

class parseRules:
    def __init__ (self):
        self.m_obj = {}
        self.m_order = []
        self.m_constraints = []
        self.m_forbidden = None

    def __parseOrder(self, order):
        for line in order[0].splitlines():
            line = line.lstrip()
            self.m_order.append(Order(self.m_obj, line)) 

    def __parseForbidden(self, forbidden):
        l = []
        for line in forbidden[0].splitlines():
            line = line.lstrip()
            l.extend([x.strip() for x in line.split(',')])
            print(l)
        self.m_forbidden = Forbidden(self.m_obj, l)

    def __parseConstraints(self, constraints):
        for line in constraints[0].splitlines():

            Container_t = Optional(Word(alphanums)) + Suppress(Literal(':')) 
            Operation_t = Suppress(Container_t)+oneOf('EQ RAND PRIME REPLAY PASSWORD EQV') + Suppress(Literal('(')) 

            Container = Container_t.parseString(line)[0]
            Operation = Operation_t.parseString(line)[0]

            eq = ''
            rhs = ''
            lhs = ''
            if Operation != 'EQV':
                Object_t = Suppress(Operation_t) + Word(alphanums+'_') + Suppress(Literal(':'))
                Operand_t = Suppress(Object_t) + Word(alphanums+'_'+'.[]') 
                Object = Object_t.parseString(line)[0]
                Operand = Operand_t.parseString(line)[0]
                obj = self.m_obj[Object]
                if Operation == 'EQ':
                    eq_t = Suppress(Operand_t) + oneOf('> >= <= < ==')
                    eq = eq_t.parseString(line)[0]
                    rhs_t = Suppress(eq_t) + OneOrMore(Word(alphanums) + Suppress(Optional(oneOf('|| &&')))) +Suppress(Literal(')'))
                    rhs = rhs_t.parseString(line)
            elif Operation == 'EQV':
                Object = ''
                Operand = ''
                lhs_t = Suppress(Operation_t) + Word(alphanums+'_')
                eq_t = Suppress(lhs_t) + oneOf('& | ^')
                rhs_t = Suppress(eq_t) + Word(alphanums+'_') + Suppress(Literal(')'))
                lhs = lhs_t.parseString(line)[0]
                eq = eq_t.parseString(line)[0]
                rhs = rhs_t.parseString(line)[0]

            
                #print(eq)
                #print(rhs)

            self.m_constraints.append(Constraint(Container, Operation,  Operand, eq, rhs, lhs, obj))
                
            #print(Operation)
            #print(Object)
            #print(Operand)
            #print("\n")

    def __parseObjects(self, objects):
        for line in objects[0].splitlines():
            sname_t = Word(alphanums) + Suppress(Literal(':'))
            fname_t = Suppress(sname_t) + Word(alphanums+'_') + Suppress(Literal('('))
            vars_t = Word(alphanums+'_') + Suppress(Optional(Literal(',')))
            var_t = Suppress(fname_t) + ZeroOrMore(vars_t) + Suppress(Literal(')'))
         
            # sudo name
            sname = sname_t.parseString(line)[0]
            # function name
            fname = fname_t.parseString(line)[0]
            # parse variable names and create dict
            var = var_t.parseString(line)
            var_val = [None] * len(var.asList())
            #print(var.asList(), type(var.asList()))
            var_dict = dict(zip(var, var_val))
            #print(var_dict)

            # create Object and fill vars
            self.m_obj[sname] = Object(fname)
            self.m_obj[sname].addVarList(var_dict)
            #print("fname: ",self.m_obj[sname].getfname())
            #print("vars: ",self.m_obj[sname].getVarList())

    def parse(self, fileName):

        # Parse different sections of the rule file 
        # OBJECT
        # a: abc(int b)
        # ORDER
        # a
        # CONSTRAINTS
        # b > 100
        # FORBIDDEN
        # xyz()

        object_marker = LineStart() + Literal('OBJECTS') + LineEnd()
        order_marker = LineStart() + Literal('ORDER') + LineEnd()
        constraint_marker = LineStart() + Literal('CONSTRAINTS') + LineEnd()
        forbidden_marker = LineStart() + Literal('FORBIDDEN') + LineEnd()
        markers = object_marker ^ order_marker ^ constraint_marker ^ forbidden_marker

        object_section = Group(
                    Suppress(object_marker) + SkipTo(markers | stringEnd).setResultsName('object')
                    ).setResultsName('objects', listAllMatches=True)
        order_section = Group(
                    Suppress(order_marker) + SkipTo(markers | stringEnd).setResultsName('order')
                    ).setResultsName('orders', listAllMatches=True)
        constraint_section = Group(
                    Suppress(constraint_marker) + SkipTo(markers | stringEnd).setResultsName('constr')
                    ).setResultsName('constraints', listAllMatches=True)
        forbidden_section = Group(
                    Suppress(forbidden_marker) + SkipTo(markers | stringEnd).setResultsName('forbidden')
                    ).setResultsName('forbiddens', listAllMatches=True)
        sections = object_section ^ order_section ^ constraint_section ^ forbidden_section
        
        text = StringStart() + SkipTo(sections | StringEnd())
        doc = Optional(text) + ZeroOrMore(sections)
        result = doc.parseFile(fileName)
        p = result.objects[0].asList()
        #print("### P:",p[0], type(p[0]))
        #print("Object List: ", result.objects.asList(), type(result.objects.asList()))
        #print("Order List: ", result.orders)
        #print("Constraint List: ", result.constraints)
        #print("forbidden List: ", result.forbiddens)

        # Fill Object List
        self.__parseObjects(result.objects[0].asList())

        # FIll Order
        self.__parseOrder(result.orders[0].asList())

        # Fill Constraints
        self.__parseConstraints(result.constraints[0].asList())

        # Fill Forbidden
        self.__parseForbidden(result.forbiddens[0].asList())

        # TODO remove these if not required
        self.object_section = object_section
        self.order_section = order_section
        self.constraint_section = constraint_section
        self.forbidden_section = forbidden_section

    def getObjects(self):
        return self.m_obj

    def getOrder(self):
        return self.m_order
        pass

    def getConstraints(self):
        return self.m_constraints

    def getForbidden(self):
        return self.m_forbidden
        pass


