import sys
import os
import random
import statistics
import time
import matplotlib.pyplot as plt

#unsatclslist=[]

def generatertd(stepsperex,filename):
    srtlist=sorted(stepsperex)
    lslen=len(srtlist)
    cumdist=[]
    for i in range(lslen):
        cumdist.append((i+1)/lslen)
    plt.xlabel('run time[Steps]')
    plt.ylabel('P')
    plt.xscale('log')
    plt.title('RTD '+filename)
    plt.plot(srtlist,cumdist)
    plt.show()
    print(cumdist)

def readInstance(fName):    
    ''' Reused solution for lab execercise - sat sol checker with few modifications.
    This method will also generate a new dict varclsindex and returns in output list
    which will map varible to clauses to be used in soltion check '''
    file = open(fName, 'r')
    tVariables  = -1    
    tClauses    = -1    
    clause      = []    
    variables   = []    
    current_clause = []
    varclsindex = {}    
    clscnt=0
    
    for line in file:        
        data = line.split()        
        if len(data) == 0:            
            continue        
        if data[0] == 'c':            
            continue        
        if data[0] == 'p':            
            tVariables  = int(data[2])            
            tClauses    = int(data[3])            
            continue        
        if data[0] == '%':            
            break        
        if tVariables == -1 or tClauses == -1:            
            print ("Error, unexpected data")            
            sys.exit(0)        
        ##now data represents a clause        
        for var_i in data:            
            literal = int(var_i)
            if literal == 0:                
                clause.append(current_clause)                
                current_clause = []                
                continue            
            var = literal            
            if var < 0:                
                var = -var            
            if var not in variables:                
                variables.append(var)
                varclsindex[var]=[clscnt]   
            else:           
                varclsindex[var].append(clscnt)      
            current_clause.append(literal)    
        clscnt+=1

    if tVariables != len(variables):        
        print ("Unexpected number of variables in the problem")        
        print ("Variables", tVariables, "len: ",len(variables))        
        print (variables)        
        sys.exit(0)    
    if tClauses != len(clause):        
        print ("Unexpected number of clauses in the problem")        
        sys.exit(0)    
    file.close()    
    return [variables, clause,varclsindex]

def solutionStatus(instance, sol, flipvar,clssatvaldict):
    ''' Reused solution for lab execercise - sat sol checker with few modifications.
    This method will only recheck satifibility of clauses effected by flip by using varclsindex 
    i.e. sat[2], which maps var to clauses. Flip var==-1 for complete solution check'''

    clause = instance[1]
    unsat_clause = 0
    iter=0
    for clause_i in clause:
        if flipvar==-1 or iter in instance[2][flipvar]:
            cStatus = False
            tmp = []
            for var in clause_i:
                if var < 0:
                    if (1 - sol[-var]) == 1:
                      cStatus = True
                    tmp.append([var, sol[-var]])
                else:
                    tmp.append([var, sol[var]])
                    if sol[var] == 1:
                        cStatus = True
            if not cStatus:
                clssatvaldict[iter]=0
            else:
                clssatvaldict[iter]=1
        iter+=1

    unsat_clause=len(clssatvaldict)-sum(clssatvaldict.values())
               
    return unsat_clause

def gsat(sat,sol,unsatclss,clssatvaldict):
    ''' delate a list to tie break later and netgain as -ve inifinity'''
    tiebrklist=[]
    netgain=float("-inf")
    for var in sol:
        ''' Flip each variable in sol and call solution status to find out total unsat claused'''
        tmpsol=sol.copy()
        tempsatclsdict=clssatvaldict.copy()
        tmpsol[var]=1-tmpsol[var]
        unsatclsstmp = solutionStatus(sat, tmpsol,var, tempsatclsdict)

        ''' Track net gain, if higher netgain reintialise tiebreaklist variable flipped to tielist
        else append to the list '''
        if netgain < ( unsatclss - unsatclsstmp):
            netgain = ( unsatclss - unsatclsstmp)
            tiebrklist=[var]
        elif netgain==( unsatclss - unsatclsstmp):
            tiebrklist.append(var)

    '''randomly select one variable in the list and flip itm if only one element that element is returned'''

    selvar=random.choice(tiebrklist)
    
    #print('GSAT - Selected variable with max net gain:',selvar,'Net Gain:',netgain)
    return selvar

def randomwalk(sat,sol,clssatvaldict):
    '''get all indexes of unsat clausess'''
    unsatclsind = [i for i in clssatvaldict if clssatvaldict[i]==0]

    ''' randomly select a unsatisfied clause and then variable and return variable'''
    rancls=random.choice(unsatclsind)
    ranvar=random.choice(sat[1][rancls])
    if ranvar < 0:
        ranvar=-ranvar 
    #print('Random Walk Selected Variable ',ranvar)
    return ranvar

def intialassignment(sol):
    ''' create an intial random assignment by randomly assigning 0 or 1 to all variables.'''
    d = {el:0 for el in sol}
    for el in d:
        d[el]=random.randint(0,1)
    return d


def search(sat,maxtries,maxflips,wp):
  
    clssatvaldict={ i:0 for i in range(len(sat[1]))}   
    for i in range(maxtries):
        ''' sol - dictionary to track current solution, initial assignment method is used to 
        randomly initialize the values
        '''
        sol=intialassignment(sorted(sat[0]))
        #print('Initial Assignment:',list(sol.values()))
        
        for j in range(maxflips):
            ''' solutionStatus - Checks the status of current solution starting with initial solution
            returns total number of unsatisfied clausses. Updates classatvaldit with unsat clauses to 0 and 
            sat clauses to 1
            '''
            unsatclss = solutionStatus(sat, sol,-1,clssatvaldict)
            #unsatclslist.append(unsatclss)
            #print('Unsatisied Clauses:',[i for i in clssatvaldict if clssatvaldict[i]==0])
            #print('Total UnSat Clauses:',unsatclss)
            #print('------------------------------------------')
            #print('Try:',i+1,'Flip:',j+1)

            if unsatclss == 0:
                '''Return solution if satisfied'''
                return sol, clssatvaldict, 'Solution Found', i, j
            '''
                Select between GSAT Step and Random Walk Step, get the var to be fliped and flip the variable
            '''    
            if random.random() > wp:
                #print('GSAT Step')
                selvar=gsat(sat,sol,unsatclss,clssatvaldict)
            else:
                #print('Random Walk Step')
                selvar=randomwalk(sat,sol,clssatvaldict)

            sol[selvar]=1-sol[selvar]
            #print('Solution at Try',i+1,'and','Flip',j+1,':','Selvar',selvar,list(sol.values()))

    return sol, clssatvaldict, 'No Solution Found',i,j

''' Check length of arguments, return if arguments are incomplete'''            
if len(sys.argv) < 6:
    print ("Error - Incorrect input")
    print ("Expecting python BasicTSP.py [instance] ")
    sys.exit(0)

'''Get directory details'''
directory=os.getcwd()
datadir=directory+"\\data\\"

''' Print Arguments'''
print('Input Parameters:')
print('---------------------------------------------------------------------------------------------------------------')
print('File Name: ',sys.argv[1])
print('Executions: ',int(sys.argv[2]))
print('ReStarts: ',int(sys.argv[3]))
print('Iterations: ',int(sys.argv[4]))
print('wp: ',float(sys.argv[5]))
print('---------------------------------------------------------------------------------------------------------------')

rtd = input("Generate RTD (Y/N)") 

''' Read INstance File '''

print('Reading Instance File ')
print('---------------------------------------------------------------------------------------------------------------')

sat=readInstance(datadir+sys.argv[1])
stepsperex=[] #to track no. of steps per execution to find solution
timeperex=[] #to track no. of steps per iteration
tries=[]
solfound=0
print('Calling Search ')
print('---------------------------------------------------------------------------------------------------------------')
for k in range(int(sys.argv[2])):
    ''' Set different seed for each iteration based on student id.
    clssatvaldict - tracks validation status of each clause, initialized to 0.'''
    start_time = time.time()
    print('Execution ',k+1,', With Seed: ',184918+k*1000)
    print('*************************************************************************************************')
    random.seed(184918+k*1000)
    sol,clssatvaldict,text,restart,flip = search(sat,int(sys.argv[3]),int(sys.argv[4]),float(sys.argv[5]))
    print(text+' after Execution '+str(k+1)+', Try '+str(restart+1)+' and Flip '+str(flip+1))
    print('Best Solution: ',sol,'unSat Clauses:',len([i for i in clssatvaldict if clssatvaldict[i]==0]))
    stepsperex.append(((restart)*int(sys.argv[4]))+flip)
    timeperex.append(time.time() - start_time)
    tries.append(restart)
    if restart<9 or flip < 999:
        solfound+=1

print('Average No. of Steps per execution:',round(statistics.mean(stepsperex),2))
print('Average time per execution:',round(statistics.mean(timeperex),2), ' Seconds')
print('No. of times solution found:',solfound)
print('Mean steps:',round(statistics.mean(stepsperex),2))
print('Median steps:',round(statistics.median(stepsperex),2))
print('Standard Deviation steps:',round(statistics.stdev(stepsperex),2))
print('Variance in steps:',round(statistics.variance(stepsperex),2))
print('Max steps:',max(stepsperex))
print('Min steps:',min(stepsperex))
#print(stepsperex)
#print(unsatclslist)

if rtd.upper()=='Y':
    generatertd(stepsperex,sys.argv[1])
    
