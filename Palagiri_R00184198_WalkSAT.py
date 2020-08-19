import sys
import os
import random
import collections
import time
import statistics
import matplotlib.pyplot as plt

directory=os.getcwd()
datadir=directory+"\\data\\"
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
    This method will also generate a new dict varclsindex which will map varible to clauses to be used in soltion check '''
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
    This method will only recheck satifibility of clauses effected by flip by using varclsindex, which maps var to clauses.
    Flip var==-1 for complete solution check'''

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

def intialassignment(sol):
    ''' create an intial random assignment by randomly assigning 0 or 1 to all variables.'''
    d = {el:0 for el in sol}
    for el in d:
        d[el]=random.randint(0,1)
    return d

def calcneggain(tmpclssatvaldict,clssatvaldict,varclsmap):

    ''' Method to calculated negative gain. Get all index of clauses that are satified and has variable being flipped into list
    satclsind. Get indexs of all clauses that are satisfied post flipping variable and in satclsind into newsatind. 
    Length of satclsind - Length of newsatind is the negative gain.
     '''
    satclsind = [i for i in clssatvaldict if clssatvaldict[i]==1 and i in varclsmap]
    newsatind= [i for i in tmpclssatvaldict if i in satclsind and tmpclssatvaldict[i]==1]
    return len(satclsind) - len(newsatind)
    
def selectvar(sat,sol,clssatvaldict,p,tabu):
    
    ''' randomly select a unsatisfied clause'''
    unsatclsind = [i for i in clssatvaldict if clssatvaldict[i]==0]
    #print('Unsatisfied Clauses:',unsatclsind)
    rancls=random.choice(unsatclsind)
    #print('Random Clause Selected:',rancls)
    clause=sat[1][rancls]
    neggain0list=[]
    netgaindict={}
    
    ''' For each variable in clause, calculate neg gain. 
    '''
    for var in clause:
        if var < 0:
            cvar=-var
        else:
            cvar=var
        #print('CVAR:',cvar,'Tabu:',tabu)    
        ''' if cvar in tabu then continue with new variable'''
        if cvar in tabu:
            continue
        ''' copy solution and  clssatvaldict (used to track status of each clause into new variables), 
        flip the variable in new sol variable and check solution status. Solution status will update tmpclssatvaldict
        with new status of each clause.''' 
        tmpsol=sol.copy()
        tmpclssatvaldict=clssatvaldict.copy()
        tmpsol[cvar]=1-tmpsol[cvar]
        tmpunsatclause=solutionStatus(sat, tmpsol,cvar,tmpclssatvaldict)

        '''Calculate negative gain based on tmpclssatvaldict and clssatvaldict'''
        neggain=calcneggain(tmpclssatvaldict,clssatvaldict,sat[2][cvar])

        ''' if negative gain is 0 append to a list to tie break later, store negative gain agains each variables in a dict'''
        if  neggain == 0:
            neggain0list.append(cvar)
            netgaindict[cvar]= neggain
        else:
            netgaindict[cvar]= neggain
    
    #print('Negative gain 0 list',neggain0list,'Negative gain dictionary:',netgaindict)
    
    ''' if all variables are in tabu, return -1'''
    if len(netgaindict)==0:
        return -1

    ''' Randomly select one variable having negative gain === 0, if such variables exist'''
    if len(neggain0list) !=0:
        selvar=random.choice(neggain0list)
        #print('Sel Var:',selvar,neggain0list,netgaindict)
        return selvar

    ''' If no negative gain 0 variables exist, select one either randomly based on probability p or one with minimal neg
    gain'''
    if random.random() < p:
        #print('Selecting Random Variable from BC')
        selvar=random.choice(list(netgaindict.keys()))
    else:
        #print('Selecting variable with min neg gain, tie breaking when more than 1')
        minvallist={i:netgaindict[i] for i in netgaindict if netgaindict[i]==min(netgaindict.values())}
        selvar=random.choice(list(minvallist.keys()))
        #print('minvallist:',minvallist)

    #print('Sel Var:',selvar)
    return selvar

def search(sat,maxflips,maxtries,p,tl):
    clssatvaldict={ i:0 for i in range(len(sat[1]))} 
    tabu=collections.deque(maxlen=tl)
    for i in range(maxtries):
        ''' sol - dictionary to track current solution, initial assignment method is used to 
        randomly initialize the values
        '''
        tabu.clear()
        sol=intialassignment(sorted(sat[0]))
        #print('Initial Assignment:',list(sol.values()))
        
        for j in range(maxflips):
            unsatclss = solutionStatus(sat, sol,-1,clssatvaldict)
            #unsatclslist.append(unsatclss)
            #print('Unsatisied Clauses:',[i for i in clssatvaldict if clssatvaldict[i]==0])
            #print('Total UnSat Clauses:',unsatclss)
            #print('------------------------------------------')
            #print('Try:',i+1,'Flip:',j+1)

            if unsatclss == 0:
                '''Return solution if satisfied'''
                return sol, clssatvaldict, 'Solution Found', i, j
            
            '''Method selectvar does walksat/skc with tabu and returns var to flip'''    
            selvar=  selectvar(sat,sol,clssatvaldict,p,tabu)
            '''Select variable to flip, if no variable is selected as all variables of the random clause in tabu
            continue to new flip, else flip the variable in current solution. '''
            if selvar == -1:
                continue

            sol[selvar]=1-sol[selvar]

            '''append variable selected to tabulist'''
            tabu.append(selvar)
            
    return sol, clssatvaldict, 'No Solution Found',i,j

''' Check length of arguments, return if arguments are incomplete'''            
if len(sys.argv) < 7:
    print ("Error - Incorrect input")
    print ("Expecting python Palagiri_R00184198_WalkSAT.py [instance] ")
    sys.exit(0)


''' Print Arguments'''
print('Input Parameters:')
print('---------------------------------------------------------------------------------------------------------------')
print('File Name: ',sys.argv[1])
print('Executions: ',int(sys.argv[2]))
print('Iterations: ',int(sys.argv[3]))
print('ReStarts: ',int(sys.argv[4]))
print('p: ',float(sys.argv[5]))
print('tl: ',int(sys.argv[6]))
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
    print('Execution',k+1,'with Seed',184918+k*1000)
    print('************************************************************************************************************')
    random.seed(184918+k*1000)  
    start_time = time.time()
    sol,clssatvaldict,text,restart,flip= search(sat,int(sys.argv[3]),int(sys.argv[4]),float(sys.argv[5]),int(sys.argv[6]))
    print(text+' after Execution '+str(k+1)+', Try '+str(restart+1)+' and Flip '+str(flip+1))
    print('Best Solution: ',sol,'unSat Clauses:',len([i for i in clssatvaldict if clssatvaldict[i]==0]))
    stepsperex.append(((restart)*int(sys.argv[3]))+flip)
    timeperex.append(time.time() - start_time)
    tries.append(restart)
    if restart<9 or flip < 999:
        solfound+=1

print('Average No. of Steps per execution:',round(statistics.mean(stepsperex),2))
print('Average time per execution:',round(statistics.mean(timeperex),2), ' Seconds')
print('No. of times solution found:',solfound)
#print(unsatclslist)
print('Mean steps:',round(statistics.mean(stepsperex),2))
print('Median steps:',round(statistics.median(stepsperex),2))
print('Standard Deviation steps:',round(statistics.stdev(stepsperex),2))
print('Variance in steps:',round(statistics.variance(stepsperex),2))
print('Max steps:',max(stepsperex))
print('Min steps:',min(stepsperex))
#print(stepsperex)

if rtd.upper()=='Y':
    generatertd(stepsperex,sys.argv[1])
    
