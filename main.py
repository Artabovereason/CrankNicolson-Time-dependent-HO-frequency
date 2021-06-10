import numpy as np
import time
import matplotlib.pyplot as plt
import os
import imageio
import math
from scipy.integrate import simps
from numpy import trapz
from scipy.optimize import curve_fit
start = time.clock()

"""
It requires three parameters :
        ntp   : number of time periods
        k     : gap between each time step
        omega : the frequency of oscillation of time-dependent potential

In cases in which the time-dependent potential is not oscillatory
in time omega is to be set to 0.

When time_steps.t_val(ntp,k,omega) is called, it generates an array
of all the time steps at which the wavefunction is to be evaluated
"""

class time_steps(object):
    def __init__(self,ntp,k,omega):
        self.ntp   = ntp
        self.k     = k
        self.omega = omega

    def t_val(self):
        ntp   = self.ntp
        k     = self.k
        omega = self.omega
        try:
                t_scale = ntp*2*np.pi/omega
        except ZeroDivisionError:
                t_scale = ntp*2*np.pi
        t_val = []       #storing the time values for each time step
        ts    = 0
        count = 0
        while ts<(t_scale):
            t_val.append(ts)
            ts    = ts + k
            count = count + 1
        return t_val
'''=========================================================================='''

"""
Parameters :
        h       : step size for x-coordinate values
        k       : step size for time-coordinate values
        x_range : range of x-coordinate values
        n       : number of x-coordinates to be included
        lam     : lambda value for A and B matrices
        omega   : The frequency of oscillation of time-dependent potential

Some arrays are also defined here:
         x      : array to store the x-coordinate values
         y      : array to store psi(xi) at each xi
         t_val  : array to store all time-coordinate values
"""

h       = 0.01                                              #step size in x coordinate
k       = 0.05                                               #step size in t coordinate
x_range = (-4,4)
n       = int((x_range[1]- x_range[0])/h)+1                           #no. of x points
lam     = (1j*k)/(4*(h**2))                        #lambda value of L and U matrices
omega   = float(input('Enter the value of omega : '))

x       = np.linspace(x_range[0],x_range[1],n)
y       = np.zeros(n)
z       = 0.000001                                     #initial slope to calculate Psi
y[1]    = z*h

ntp     = 50 #nombre periode
tsteps  = time_steps(ntp,k,omega)
t_val   = tsteps.t_val()
print('number of time steps = ',len(t_val))

'''=========================================================================='''



"""
Here we define the time-dependent potential V(x,t).
Here x implies position and t implies time.
The constants dist, epsilon and gamma are given according
to the potential as discussed in report.

If a different potential is to be studied change b to the
potential of interest.
"""
dist    = 2            #a value for the potential 2
epsilon = 1          #epsilon value for the potential 1
gamma   = 0.25          #gamma value for the potential 0.025

def V(x,t):
    '''takes in the x coordinate and time
       returns the time dependent potential'''
    #b = np.cos(omega*t)*(x**2)
    #b = -((2*epsilon)/dist**2)*(x**2)+(epsilon/(dist**4))*(x**4) + gamma*np.cos(omega*t)*(x**3)
    b = (2+np.cos(omega*t))*(x**2)/2
    return b

'''=========================================================================='''
'''defining the function to carry out Numerov method'''
def Numerov(x,y1,y2,E):
    '''returns y[i+1] value'''
    u = 1 - (1/6.)*(h**2)*(V(x,t)-E)
    return ((12-10*u)*y1-u*y2)/u

'''=========================================================================='''
'''defining a function to carry out Numerov for a given E'''
def Psi(E):
    for i in range(2,n):
        y[i] = Numerov(x[i],y[i-1],y[i-2],E)
    N_const = 0                 #Inverse of square of Normalisation constant
    for j in y:
        N_const = N_const + j*j*h
    A1 = 1.0/np.sqrt(N_const)
    m  = A1*y
    return(m[-1],m)

'''=========================================================================='''
'''finding the eigenvalues'''
def Eigen():
    Eigenvalues = []
    a           = np.linspace(min(V(x,t)),1,20)
    P           = np.array([Psi(i)[0] for i in a])
    for i in range(len(P)-1):
        if (P[i]<0 and P[i+1]>0) or (P[i]>0 and P[i+1]<0):
            low  = a[i]
            high = a[i+1]
            mid  = (low + high)/2.
            while abs(Psi(mid)[0]) > h:
                mid = (low + high)/2.
                if P[i] < 0:
                    if Psi(mid)[0] < 0:
                        low = mid
                    else:
                        high = mid
                elif P[i] > 0:
                    if Psi(mid)[0] > 0:
                        low = mid
                    else:
                        high = mid
            Eigenvalues.append(mid)
    return Eigenvalues

'''=========================================================================='''
'''Storing the instantaneous ground state at each time step'''
Psi_gs = {}
Eigenvalue_stock = []
for t in t_val:
    Eigenvalue = Eigen()[0]
    Eigenvalue_stock.append(Eigen()[0])
    Psi_gs[t] = Psi(Eigenvalue)[1]
    #print('Psi_ground_state at t = ',t,' generated with eigenvalue = ',Eigenvalue)
print('All Psi_gs generated')

'''=========================================================================='''
'''Defining functions to make A and B dictionaries'''
def a(i,j):
    '''A matrix elements'''
    if i==j:
        return 1 + 2*lam + 1j*k*V(x[i-1],t)/2
    elif abs(i-j) == 1:
        return -lam

def b(i,j):
    '''B matrix elements'''
    if i==j:
        return 1 - 2*lam - 1j*k*V(x[i-1],t)/2
    elif abs(i-j) == 1:
        return lam

def comp_conj(number):
    '''returns the complex conjugate of a number'''
    return number.real-(number.imag)*1j

'''=========================================================================='''
'''Storing the A and B matrix for each time step'''
A_val = {}                   #stores the A matrix for each time step
B_val = {}                   #stores the B matrix for each time step
for t in t_val:
    a_val={}
    b_val={}
    for i in range(1,n+1):
        if (i-1)!=0 :
            a_val[(i,i-1)]=a(i,i-1)
            b_val[(i,i-1)]=b(i,i-1)
        a_val[(i,i)]=a(i,i)
        b_val[(i,i)]=b(i,i)
        if (i+1)!=n+1 :
            a_val[(i,i+1)]=a(i,i+1)
            b_val[(i,i+1)]=b(i,i+1)
    A_val[t] = a_val
    B_val[t] = b_val
'''=========================================================================='''
L_val = {}                   #stores the L and U matrix for each time step
U_val = {}
for t in t_val:
    a_val = A_val[t]
    def l(i,j):
        if (i,j) in l_val:
            return l_val[(i,j)]
        else:
            if i==j:
                l_val[(i,j)]=1
                return 1
            elif (j == i-1):
                l_val[(i,j)] = a_val[i,i-1]/u(i-1,i-1)
                return a_val[i,i-1]/u(i-1,i-1)

    def u(i,j):
        if (i,j) in u_val:
            return u_val[(i,j)]
        else:
            if i==j:
                if i==1:
                    u_val[(i,j)] = a_val[1,1]
                    return a_val[1,1]
                else:
                    u_val[i,j] = a_val[i,i]-(l(i,i-1)*u(i-1,i))
                    return a_val[i,i]-(l(i,i-1)*u(i-1,i))
            elif (j==i+1):
                u_val[(i,j)] = a_val[i,j]
                return a_val[i,j]

    l_val={}
    u_val={}

    for i in range(1,n+1):
        l_val[(i,i)]=l(i,i)
        if (i-1)!=0 : l_val[(i,i-1)]=l(i,i-1)
        u_val[(i,i)]=u(i,i)
        if (i+1)!=n+1 : u_val[(i,i+1)]=u(i,i+1)
    L_val[t] = l_val
    U_val[t] = u_val

'''=========================================================================='''
'''Generation of Psi(x,t)'''
Psi_0           = Psi_gs[t_val[0]]
PSI_t           = {}                   #stores the Psi at each time
PSI_t[t_val[0]] = Psi_0      #set the initial Psi here
Psi             = PSI_t[t_val[0]]
for t in range(1,len(t_val)):
    #print('Psi(at t = %f) generated' %t)
    bv    = []
    b_val = B_val[t_val[t-1]]
    l_val = L_val[t_val[t]]
    u_val = U_val[t_val[t]]
    for i in range(1,len(Psi)+1):
        if (i-1)!=0: x1 = b_val[(i,i-1)]*Psi[i-2]
        else: x1 = 0
        x2 = b_val[(i,i)]*Psi[i-1]
        if i!=len(Psi) : x3 = b_val[(i,i+1)]*Psi[i]
        else: x3 = 0
        bv.append(x1+x2+x3)
    z_val    = {}
    z_val[1] = bv[0]
    for i in range(2,len(bv)+1):
        z_val[i] = bv[i-1]-(z_val[i-1]*l_val[(i,i-1)])
    x_val    = {}
    x_val[n] = z_val[n-1]/u_val[(n-1,n-1)]
    for i in range(n-1,0,-1):
        x_val[i] = (z_val[i]-(u_val[(i,i+1)]*x_val[i+1]))/u_val[(i,i)]
    nindx = sorted(x_val.keys())

    npsi  = []
    for i in nindx:
        npsi.append(x_val[i])
    PSI_t[t_val[t]] = npsi
    Psi = npsi
'''=========================================================================='''
Coeff = {}                  #saves coefficients(c) for each time step
def C(Psi,yn):
    '''returns the coefficient cn of Psi in yn'''
    ip = 0
    for i in range(len(Psi)):
        ip = ip + Psi[i]*yn[i]*h
    return ip
for i in t_val:
    Coeff[i] = C(Psi_gs[i],PSI_t[i])

'''=========================================================================='''
Coeff2 = {}                 #saves cc* for each time step
for i in t_val:
    cn2 = (Coeff[i]*comp_conj(Coeff[i])).real
    Coeff2[i] = cn2


'''=========================================================================='''

C1_val = np.array([i for i in Coeff.values()] )
C2_val = np.array([i for i in Coeff2.values()])
"""
@('c(1)2 values are = ',C2_val)
print('c(1) values are = ' ,C1_val)
"""

end = time.clock()
print('time taken to run the program is ',end-start,' seconds')
'''=========================================================================='''

"""
plt.figure()
plt.title('omega = %.3f' %omega)
plt.xlabel('$\dfrac{\omega}{2\pi}$t  -------->')
plt.ylabel('${C_1}^2$  -------->')
plt.ylim(0,1.1)
if omega!=0:
	plt.plot([(i*omega)/(2*np.pi) for i in t_val],[i for i in Coeff2.values()])
else:
        C2_val = np.array([i for i in Coeff2.values()])
        plt.plot(t_val,C2_val)
plt.show()
"""

'''=========================================================================='''

"""
plt.figure()
plt.title('Representation of width $\sigma$ of the gaussian through time')
plt.xlabel('<----$t$---->')
plt.ylabel('$\sigma$')
#plt.ylim(-105,+105)
plt.legend()
plt.plot(t_val, sigma_width , color='black' , label ='width' ) #
plt.plot(t_val, abs(C1_val ), color='blue'  , label ='normalisation'  )     #
plt.show()
"""

'''=========================================================================='''


sigma_width = []
for i in range(len(t_val)):
    sigma_width.append(1/max(np.absolute(PSI_t[t_val[i]])*np.sqrt(math.pi)) )

def function(x):
    return [-1/ ((i) ** 2) for i in x]

valeur_valeur = []
berry_phase   = []
for m in range(len(t_val)):
    valeur_valeur.append(sigma_width[m])

for w in range(len(t_val)):
    if w==0: berry_phase.append(0)
    else :
        #berry_phase.append(simps( function(valeur_valeur[:w]) , valeur_valeur[:w] , dx=k ) )
        berry_phase.append(simps( function(valeur_valeur[:w]) , t_val[:w] , dx=k ) )

derivee_sigma = [] # je calcul la dérivée du width : sigma
derivee_sigma.append(0)
for i in range(1,len(t_val)-1):
    derivee_sigma.append(  (sigma_width[i-1]- sigma_width[i+1])/(2*k) )
derivee_sigma.append(0)

rapport_sigma = [] #je fait le rapport dérivée sigma / 2*sigma pour obtenir le coefficient alpha
for i in range(1,len(t_val)-1):
    rapport_sigma.append( derivee_sigma[i-1]/(2*sigma_width[i]) )

autre_derivee = []
autre_derivee.append(0)
for i in range(1,len(t_val)-1):
    autre_derivee.append( 0.5 *  ( np.log(sigma_width[i-1])- np.log(sigma_width[i+1]))/(2*k)     )
autre_derivee.append(0)


"""
plt.figure()
plt.title('Representation of width $\sigma$ of the gaussian through time')
plt.xlabel('<----$t$---->')
plt.ylabel('$\sigma$')
#plt.ylim(-105,+105)
plt.legend()
plt.plot(t_val                , sigma_width  , color='blue'   , label ='$\sigma$' )
plt.plot(t_val[1:len(t_val)-1],derivee_sigma , color='red'    , label ='$\dot{\sigma}$'  )     #
plt.plot(t_val[1:len(t_val)-1],rapport_sigma , color='green'  , label ='$\dot{\sigma}/\sigma$'  )     #
plt.show()
"""

'''=========================================================================='''
dimension_periode = np.linspace(0, max(t_val), ntp )
zeros = []
for i in range(len(dimension_periode)):
    zeros.append(0)

'''=========================================================================='''
le_potentiel = [] #ça permet de tracé l'évolution du potentiel en fonction du temps

for i in range(len(t_val)):
    le_potentiel.append(V(1,i))
'''=========================================================================='''

'''
L'invariant Omega ici défini comme Omega = sigma**2 * dérivée de la phase de Berry
'''
Omega_invar = []
for i in range(1,len(t_val)-1):
    Omega_invar.append( sigma_width[i]*sigma_width[i]* (berry_phase[i-1]-berry_phase[i+1])/(2*k) )

'''=========================================================================='''

'''
On aimerais construire un Q-oscillateur harmonique, pour lequel sa position q serais
Q=q/sigma
'''

'''
def test(x, a, b):
    return a * np.sin(b * x)

param, param_cov = curve_fit(test, t_val, sigma_width)

print("Sine funcion coefficients:")
print(param)
print("Covariance of coefficients:")
print(param_cov)
print(param[0])
print(param[1])

ans = []
for i in range(len(t_val)):
    ans.append( (param[0]*(np.sin(param[1]*t_val[i]))) )


plt.plot(t_val, sigma_width, 'o', color ='red', label ="data")
plt.plot(t_val, ans, '--', color ='blue', label ="optimized data")
plt.legend()
plt.show()
'''

'''=========================================================================='''

'''
On construit l'invariant de Ermakov
'''

valeur_moyenne_I      = []


sigma_carree = []
for i in range(len(sigma_width)):
    sigma_carree.append((sigma_width[i])**2)

'''=========================================================================='''
'''
Moyenne de (1/sigma2 +(dérivee sigma)2)x2
'''

premiere_moyenne      = []
premiere_nouvelle_var = []
for i in range(len(sigma_width)):
    if i==0 or i==int(len(sigma_width)-1):
        premiere_nouvelle_var.append( (x**2)/(sigma_carree[i])                                                       )
    else:
        premiere_nouvelle_var.append( (x**2)/(sigma_carree[i]) + (x**2)*(sigma_width[i-1]- sigma_width[i+1])/(2*k)   )

for i in range(len(t_val)):
    premiere_moyenne.append( simps( np.conj(PSI_t[t_val[i]])* premiere_nouvelle_var[i]* PSI_t[t_val[i]] , x , dx=h ) )

'''=========================================================================='''
'''
Moyenne de sigma2 dérivée seconde par x
'''

deuxieme_moyenne      = []
deuxieme_nouvelle_var = []

list_derivee_seconde = []
for i in range(int(len(t_val))):
    derivee_seconde_prems = []
    derivee_seconde_prems.append(0)
    for w in range(int(1),int(len(x)-1)):
        derivee_seconde_prems.append( sigma_carree[i]* (PSI_t[t_val[i]][int(w-1)]-2*PSI_t[t_val[i]][w]+PSI_t[t_val[i]][int(w+1)])/(h*h)    )
    derivee_seconde_prems.append(0)
    list_derivee_seconde.append(derivee_seconde_prems)

for i in range(len(t_val)):
    deuxieme_moyenne.append(  simps( np.conj(PSI_t[t_val[i]])* list_derivee_seconde[i]                      , x , dx=h )  )

'''=========================================================================='''
'''
Moyenne de sigma x * dérivée sigma * dérivée par x
'''

troisiem_moyenne      = []
troisiem_nouvelle_var = []

list_derivee_premiere = []
for i in range(int(len(t_val))):
    derivee_premiere_prems = []
    derivee_premiere_prems.append(0)
    for w in range(int(1),int(len(x)-1)):
        derivee_premiere_prems.append( (PSI_t[t_val[i]][int(w-1)]-PSI_t[t_val[i]][int(w+1)])/(2*h)    )
    derivee_premiere_prems.append(0)
    list_derivee_premiere.append(derivee_premiere_prems)

for i in range(len(t_val)):
    troisiem_moyenne.append(  simps( 1j*np.conj(PSI_t[t_val[i]])*sigma_width[i]*derivee_sigma[i]*x[i]* list_derivee_premiere[i]                     , x , dx=h )  )



'''=========================================================================='''
'''
Moyenne de sigma dérivée par x * x * dérivée sigma
'''

quatriem_moyenne      = []
quatriem_nouvelle_var = []

#list_derivee_premiere = []
"""for i in range(int(len(t_val))):
    derivee_premiere_prems = []
    derivee_premiere_prems.append(0)
    for w in range(int(1),int(len(x)-1)):
        derivee_premiere_prems.append( sigma_width[i]* derivee_sigma[i] )
    derivee_premiere_prems.append(0)
    list_derivee_premiere.append(derivee_premiere_prems)
"""
derivee_x_derivee_sigma = []
derivee_x_derivee_sigma.append(0)
for i in range(1,int(len(t_val)-1)):
    derivee_x_derivee_sigma.append((derivee_sigma[i-1]- derivee_sigma[i+1])/(2*h) )
derivee_x_derivee_sigma.append(0)

derivee_x_psi = []
#derivee_x_psi.append(0)
for i in range(1,int(len(t_val)-1)):
    derivee_x_psi.append(0)
    for w in range(1,int(len(x)-1)):
        derivee_x_psi.append( (PSI_t[t_val[i]][w-1]-PSI_t[t_val[i]][w+1])/(2*h)  )
    derivee_x_psi.append(0)
#derivee_x_psi.append(0)

for i in range(len(t_val)):
    quatriem_moyenne.append( simps( 1j*np.conj(PSI_t[t_val[i]])* PSI_t[t_val[i]]*(derivee_sigma[i]+ x[i]*derivee_x_derivee_sigma[i] )+np.conj(PSI_t[t_val[i]])*x[i]*derivee_sigma[i]*derivee_x_psi[i]  , x , dx=h ))





for i in range(len(t_val)):
    valeur_moyenne_I.append(np.real(0.5*(premiere_moyenne[i] - deuxieme_moyenne[i]+troisiem_moyenne[i]+quatriem_moyenne[i] ) ) ) #-troisiem_moyenne[i]-quatriem_nouvelle_var[i]

#print(valeur_moyenne_I)

derivee_moyenne_I = []
derivee_moyenne_I.append(0)
for i in range(1,len(t_val)-1):
    derivee_moyenne_I.append((valeur_moyenne_I[i-1]-valeur_moyenne_I[i+1])/(2*k))
derivee_moyenne_I.append(0)

moyenne_I  = []
moyenne_dI = []
def Average(lst):
    return sum(lst) / len(lst)
average = Average(valeur_moyenne_I)
print("Average of Invariant =", round(average, 4))
for i in range(1,len(valeur_moyenne_I)-1):
    moyenne_I.append(average)
average = Average(derivee_moyenne_I)
print("Average of derivativeInvariant =", round(average, 4))
for i in range(1,len(valeur_moyenne_I)-1):
    moyenne_dI.append(average)


plt.rcParams["figure.figsize"] = (13,13) #taille de mon image
filenames = []
for k in range(len(t_val)):
    # plot the line chart
    fig, axs = plt.subplots(3,3)
    #st = fig.suptitle("Quantum Harmonic Oscillator with time-dependent frequency, $\omega$=%.2f"%omega +" over %.1f period"  %ntp, fontsize=20)
    st = fig.suptitle("Quantum Harmonic Oscillator with time-dependent frequency", fontsize=20)


    '''======================================================================='''
    ''' 0 0
    —————————————
    | X |   |   |
    —————————————
    |   |   |   |
    —————————————
    |   |   |   |
    —————————————
    '''

    axs[0,0].set_title('Width of the Gaussian function')
    axs[0,0].set_ylabel(' ')
    axs[0,0].set_xlabel('time $t$ in s')
    axs[0,0].plot(t_val    , sigma_width           , color='blue' , label= 'width'               ) #
    axs[0,0].plot(t_val[k] , sigma_width[k] , 'ro' , color='red'  , label= 'instantaneous width' ) #
    axs[0,0].legend(loc="upper right", prop={'size': 9})
    '''======================================================================='''
    ''' 0 1
    —————————————
    |   | X |   |
    —————————————
    |   |   |   |
    —————————————
    |   |   |   |
    —————————————
    '''
    axs[0,1].set_title('Energy fluctuation over time')
    axs[0,1].set_ylabel(' ')
    axs[0,1].set_xlabel('time $t$ in s')
    axs[0,1].plot(t_val    , Eigenvalue_stock          , color='black' , label = 'Eigen'               )
    axs[0,1].plot(t_val[k] , Eigenvalue_stock[k], 'ro' , color='red'   , label = 'instantaneous Eigen' )
    axs[0,1].legend(loc="upper right", prop={'size': 9})

    '''======================================================================'''
    ''' 0 2
    —————————————
    |   |   | X |
    —————————————
    |   |   |   |
    —————————————
    |   |   |   |
    —————————————
    '''

    '''======================================================================'''
    ''' 1 0
    —————————————
    |   |   |   |
    —————————————
    | X |   |   |
    —————————————
    |   |   |   |
    —————————————
    '''
    axs[1,0].set_title('Potential well oscillation')
    axs[1,0].set_ylabel(' ')
    axs[1,0].set_xlabel('time $t$')
    axs[1,0].plot(t_val    , [V(1,k) for k in t_val]          , color='black' , label = 'potential'               )
    axs[1,0].plot(t_val[k] , V(1,k)                 , 'ro'    , color='red'   , label = 'instantaneous potential' )
    axs[1,0].legend(loc="upper right", prop={'size': 9})

    '''======================================================================'''
    ''' 1 1
    —————————————
    |   |   |   |
    —————————————
    |   | X |   |
    —————————————
    |   |   |   |
    —————————————
    '''
    axs[1,1].set_title('$t=$%.3f' %t_val[k])
    axs[1,1].set_ylabel(' ')
    axs[1,1].set_xlabel('space $x$')
    axs[1,1].plot(x, [V(i,k) for i in x]            , color='black' , label ='potential')
    axs[1,1].plot(x, np.absolute(PSI_t[t_val[k]])   , color='red'   , label ='wavefunction gs')
    axs[1,1].set_ylim(-0.5,2.5)
    axs[1,1].legend(loc="best", prop={'size': 9})


    '''======================================================================'''
    ''' 1 2
    —————————————
    |   |   |   |
    —————————————
    |   |   | X |
    —————————————
    |   |   |   |
    —————————————
    '''

    '''======================================================================'''
    ''' 2 0
    —————————————
    |   |   |   |
    —————————————
    |   |   |   |
    —————————————
    | X |   |   |
    —————————————
    '''
    axs[2,0].set_title('Berry phase $beta=$%.3f' %berry_phase[k])
    axs[2,0].set_ylabel('$beta(t)$ in degrees')
    axs[2,0].set_xlabel('time $t$ in s')
    axs[2,0].plot(t_val   , berry_phase         , color='blue' , label ='phase'  )
    axs[2,0].plot(t_val[k], berry_phase[k] ,'ro', color='red'  , label ='instantaneous' ) #
    axs[2,0].legend(loc="best", prop={'size': 9})

    '''======================================================================'''
    ''' 2 1
    —————————————
    |   |   |   |
    —————————————
    |   |   |   |
    —————————————
    |   | X |   |
    —————————————
    '''

    axs[2,1].set_title('alpha coefficient')
    axs[2,1].set_ylabel(' ')
    axs[2,1].set_xlabel('time $t$ in s')
    axs[2,1].plot(t_val[1:len(t_val)-1], autre_derivee[1:len(t_val)-1], color='black'  , label ='$alpha(t)$'  )########## important

    if k==0 or k>len(t_val)-2:
        print('')
    else: axs[2,1].plot(t_val[k], rapport_sigma[k-1] ,'ro', color='red'   , label ='instantaneous' ) #
    axs[2,1].legend(loc="upper right", prop={'size': 9})


    '''======================================================================'''
    ''' 2 2
    —————————————
    |   |   |   |
    —————————————
    |   |   |   |
    —————————————
    |   |   | X |
    —————————————
    '''
    axs[2,2].set_title('Invariant plot')
    axs[2,2].plot(t_val[2:len(t_val)-1], Omega_invar[1:len(Omega_invar)]   , color='black'   , label = '$\Omega$'            )
    axs[2,2].plot(t_val[1:len(t_val)-1], valeur_moyenne_I[1:len(t_val)-1]  , color='red'     , label = '$I$' )
    axs[2,2].plot(t_val[1:len(t_val)-1], moyenne_I                         , color='magenta' , label = 'Mean $I$'            )
    axs[2,2].plot(t_val[1:len(t_val)-1], derivee_moyenne_I[1:len(t_val)-1] , color='green'   , label = '$dI$' )
    axs[2,2].plot(t_val[1:len(t_val)-1], moyenne_dI                        , color='yellow'  , label = 'Mean $dI$'           )
    axs[2,2].legend(loc="best", prop={'size': 9})

    '''======================================================================'''
    plt.subplots_adjust(
                        left=0.1,
                        bottom=0.1,
                        right=0.9,
                        top=0.9,
                        wspace=0.3,
                        hspace=0.3 # 0.7
                        )

    filename = f'{k}.png'
    filenames.append(filename)

    # save frame
    plt.savefig(filename)
    plt.close()
# build gif
with imageio.get_writer('mygif.gif', mode='I') as writer:
    for filename in filenames:
        image = imageio.imread(filename)
        writer.append_data(image)

# Remove files
for filename in set(filenames):
    os.remove(filename)

end = time.clock()
print('time taken to run the full program is ',end-start,' seconds')
