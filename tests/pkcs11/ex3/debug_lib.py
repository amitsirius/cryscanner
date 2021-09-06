import gdb
import logging
import gdb.printing
import time
import os
import cProfile

apis = ['C_GenerateKey']

class SimpleCommand(gdb.Command):
        fo=open("log.txt","w+")
        fi=open("scratch.txt", "w+")
        def __init__(self, itrr):
            self.itrr = itrr
            super(SimpleCommand, self).__init__("simple_command", gdb.COMMAND_USER)
	
        def print_args(self):
            print('=> START arguments')
            gdb.execute('info args')
            print('=> END arguments')

        def print_stacktrace(self):
            print('=> START stack frame')
            cur_frame = gdb.selected_frame()
            while cur_frame is not None:
                print(cur_frame.name())
                # get the next frame
                cur_frame = cur_frame.older()
            print('=> END stack frame')

        def parse_bt(self):
           line = self.fi.readline()
           gdb.execute("set logging off")
           gdb.execute("set logging file log.txt")
           gdb.execute("set logging on")
           print (line)
           gdb.execute("set logging off")
           gdb.execute("set logging file scratch.txt")
           gdb.execute("set logging on")

        def parse_array(self, ft, arg, s1):
            gdb.execute("set logging file tmp_scratch.txt")
            gdb.execute("set logging on")
            gdb.execute(s1)
            gdb.execute("set logging off")
            #tmp_line = ft.readline()
            check_line = 'struct '+arg+'\n'
            tmp_line = ft.readlines()
            ft = open("tmp_scratch.txt", "w+")
            gdb.execute("set logging on")
            for x in tmp_line:
                #print('T',x)
                #print('C',check_line, end='')
                if 'pValue' in x:
                    s1 = 'print/x *((char *)'+arg+'.pValue)'
                    gdb.execute(s1)
                    gdb.execute("set logging off")
                    line = ft.readline()
                    val = line.split('=')
                    check_line += 'pValue = '+val[1]
                else:
                    check_line += x
            gdb.execute("set logging file log.txt")
            gdb.execute("set logging on")
            print(check_line, end='')
            gdb.execute("set logging off")
            pass
           
        def parse_args(self):
            line = self.fi.readline()
            try:
                while(line != ''):
                    if '=> INFO ARGS-END' in line:
                        break
                    arg = line.split(' =')[0]
                    s = "ptype "+arg
                    gdb.execute("set logging off")
                    ft = open("tmp_scratch.txt", "w+")
                    gdb.execute("set logging file tmp_scratch.txt")
                    gdb.execute("set logging on")
                    gdb.execute(s)
                    gdb.execute("set logging off")
                    gdb.execute("set logging file log.txt")
             
                    gdb.execute("set logging on")
                    tmp_line = ft.readline()
                    if 'struct' in tmp_line:
                        while(tmp_line != ''):
                            check_line = tmp_line
                            tmp_line = ft.readline()
                        if 'pTemplate' in s:
                            gdb.execute("set logging off")
                            for i in range(5):
                                ft = open("tmp_scratch.txt", "w+")
                                argu = arg+'['+str(i)+']'
                                s1 = 'print/x ' +argu
                                self.parse_array(ft, argu,s1);
                            line = self.fi.readline()
                            return
                            continue
                        
                        print ('struct '+arg)
                        if '} *' in check_line:
                            s1 = 'print/x *' +arg
                        else:
                            s1 = 'print/x ' +arg
                        try:
                            gdb.execute(s1)
                        except:
                            pass
             
                    else:
                        s1 = 'print/x '+arg
                        print (s+' '+line)
                    line = self.fi.readline()
            except:
                pass

            gdb.execute("set logging off")
            gdb.execute("set logging file scratch.txt")
            gdb.execute("set logging on")

        def invoke(self, arg, from_tty):
            #profiler = cProfile.Profile()
            #profiler.enable()
            # when we call simple_command from gdb, this method
            # is invoked
            for x in range(self.itrr):
                gdb.execute("set logging file scratch.txt")
                gdb.execute("set print pretty on")
                gdb.execute("set print repeats 0")
                print("Hello from simple_command")
                gdb.execute('start')
             
                # Add breakpoints
                for api in apis:
                    bp = gdb.Breakpoint(api)
                print('')
                print('=> BREAKPOINT END')
             
                logging.basicConfig(filename="scratch.txt", level=logging.INFO)
             
                while True:
                    gdb.execute("set logging on")
                    # TODO fix finish command
                    #gdb.execute("finish")
                    gdb.execute("continue")
             
                    line = self.fi.readline()
                    inferiors = gdb.inferiors()
                    test = 0
                    for inf in gdb.inferiors():
                        print('INF PROC'+str(inf.pid))
                        if inf.pid:
                            print('Continue')
                        else:
                            print('EXIT!!')
                            test = 1
                    if test == 1:
                        break
                    # TODO: Note the api called and i/p params
                    #   TODO: Fetch different types of parameters
                    #       like structs, pointer to structs.
                    # TODO: Find a way to get output arguments.
                    # TODO: Push to log file
                    print('NEXT')
                    gdb.execute('step')
                    print('=> BREAKPOINT HIT!!')
                    print('=> Backtrace')
                    gdb.execute('backtrace')
                    print('=> INFO ARGS-START')
                    gdb.execute('info args')
                    print('=> INFO ARGS-END')
                    gdb.execute('set logging off')
                    gdb.execute('set logging on')
             
                    print('=> BEFORE PARSE')
                    gdb.execute("set logging off")
                    gdb.execute("set logging on")
             
                    # consume all commands
                    # line = self.fi.readline()
                    while(line != ''):
                        if 'INFO ARGS-START' in line:
                            self.parse_args()
                        if 'Backtrace' in line:
                            self.parse_bt()
                        line = self.fi.readline()
                print('=> AFTER CONSUMING COMMANDS')
                gdb.execute("set logging off")
            #profiler.disable()
            #profiler.print_stats()

SimpleCommand(1)
