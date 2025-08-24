from scipy import *
from numpy import *
from pylab import *
from geopy.geocoders import Nominatim
import random


# --------------------------------------------------------------
def Distance(P1,P2):
    if P1 == P2 :
        return 0.0
    d = sqrt((P1[0] - P2[0])** 2 +(P1[1] - P2[1])**2)
    return d

def TotalDistance(P,seq):
    dist = 0.0
    N = len(seq)
    for i in range(N - 1):
        dist += Distance(P[seq[i]],P[seq[i+1]])
    dist += Distance(P[seq[N-1]],P[seq[0]])
    return dist


# --------------------------------------------------------------
def readCities(PNames):
    P = [] #coordinates of cities
    geolocator = Nominatim(user_agent="Sakshi_APP")
    j=0
    with open('./india_cities.txt') as file :
        for line in file:
            city = line.rstrip('\n')
            if city == "":
                break
            theLocation = city + ",India"
            pt = geolocator.geocode(theLocation,timeout=10)
            if pt is None:
                print(f"city '{city}' not found !")
                continue
            y = round(pt.latitude,2)
            x = round(pt.longitude,2)
            print(f"city[{j:2d}]={city}({x:5.2f},{y:5.2f})")
            P.insert(j,[x,y])
            PNames.insert(j,city)
            j += 1
    return P

# --------------------------------------------------------------
def Plot(seq,P,dist,PNames):
    Pt = [P[seq[i]] for i in range(len(seq))]
    Pt += array(Pt)
    title('Total distance =' + str(round(dist,2)))
    plot (Pt[:, 0],Pt[:, 1],'-o')
    for i in range(len(P)):
        annotate(PNames[i],(P[i][0],P[i][1]))
    show()

# --------------------------------------------------------------
def swap(P,seq,dist,N1,N2,temp,ncity):
    N1L = (N1 - 1)% nCity
    N1R = (N1 + 1)% nCity
    N2L = (N2 - 1)% nCity 
    N2R = (N2 + 1)% nCity

    I1,I2 = seq[N1], seq[N2]
    I1L, I1R = seq[N1L], seq[N1R]
    I2L, I2R = seq[N2L], seq[N2R]

    delta = 0.0 
    delta += Distance(P[I1L],P[I2]) + Distance(P[I1],P[I2R])
    delta -= Distance(P[I1L],P[I1]) + Distance(P[I2],P[I2R])

    if N1 != N2L and N1R != N2 and N1R != N2L and N2 != N1L:
        delta += Distance(P[I2],P[I1R]) + Distance(P[I2L],P[I1])
        delta += Distance(P[I1],P[I1R]) + Distance(P[I2L],P[I2])

    prob = 1.0
    if delta > 0.0:
        prob = exp(-delta / temp)

    rndm = random.random()
    if rndm < prob:
        dist += delta
        seq[N1], seq[N2] = I2 , I1
        return dist, True
    else :
        return dist, False

# --------------------------------------------------------------
def reverse(P,seq,dist,N1,N2,temp,nCity):
    N1L = (N1 - 1)% nCity
    N2R = (N2 + 1)% nCity

    if(N1 != N2R) and (N2 != N1L):
        delta = Distance(P[seq[N1L]],P[seq[N2]]) \
              + Distance(P[seq[N1]],P[seq[N2R]]) \
              - Distance(P[seq[N1L]],P[seq[N1]]) \
              - Distance(P[seq[N2]],P[seq[N2R]])
    else:
        return dist, False

    prob = 1.0
    if delta > 0.0:
        prob = exp(-delta / temp)

    rndm = random.random()
    if rndm < prob:
        dist += delta
        i, j = N1, N2
        while i < j:
            seq[i],seq[j] = seq[j], seq[i]
            i += 1
            j -= 1
        return dist, True
    else:
        return dist, False
        
# --------------------------------------------------------------
if __name__ == '__main__':
    PNames = []
    P = readCities(PNames)
    nCity = len(P)

    maxTsteps = 250
    fCool = 0.9
    maxSwaps = 2000
    maxAccepted = 10* nCity

    seq = arange(0,nCity,1)
    dist = TotalDistance(P,seq)
    temp = 10.0 * dist

    print(f"\n nCity= {nCity:3d} dist= {dist:.3f} temp= {temp:.3f}\n")
    Plot(seq,P,dist,PNames)

    oldDist = 0.0
    convergenceCount = 0

    for t in range(1,maxTsteps + 1):
        if temp < 1.0e-6:
            break

        accepted = 0
        iteration = 0

        while iteration <= maxSwaps:
            N1 = ransom.randint(0,nCity - 1)
            N2 = ransom.randint(0,nCity - 1)
            if N1 > N2:
                N1, N2 = N2, N1

            chk = ransom.uniform(0,1)
            if chk < 0.5 and (N1 + 1 != N2) and (N1 !=(N2+1)% nCity):
                dist, flag = swap(P,seq,dist,N1,N2,temp,nCity)
            else:
                dist,flag = reverse(P,seq,dist,N1,N2,temp,nCity)

            if flag:
                accepted +=1
            iteration +=1

            print(f"Iteration:{t} temp={temp:.6f} dist={dist:.6f}")
            print("seq =",seq,"\n")

            if abs(dist - oldDist) < 1.0e-4:
                convergenceCount += 1
            else:
                convergenceCount = 0

            if convergenceCount >= 4:
                break

            if (t% 25) == 0:
                Plot(seq,P,dist,PNames)

            temp *= fCool
            oldDist = dist

    Plot(seq,P,dist,PNames)














