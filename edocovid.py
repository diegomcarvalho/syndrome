import numpy as np
from scipy.integrate import odeint
import random
import math
import numba


#modelo 2 - 21/03/2020
def model2(w, t, c0, c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12, c13):
    return model_jit(w, t, c0, c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12, c13)

@numba.jit
def model_jit(w, t, c0, c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12, c13):
    #variaveis
    S = w[0]
    Q = w[1]
    E = w[2]
    A = w[3]
    I = w[4]
    D = w[5]
    R = w[6]
    M = w[7]

    #constantes
    beta = c0
    theta = c1
    p = c2
    lambda0 = c3
    sigma = c4
    rho = c5
    epsilonA = c6
    epsilonI = c7
    gammaA = c8
    gammaI = c9
    gammaD = c10
    dI = c11
    dD = c12
    delta = c13

    #equacoes
    dSdt = -beta * S * (I + theta * A) - p * S + lambda0 * Q
    dQdt = p * S - lambda0 * Q - delta * Q
    dEdt = beta * S * (I + theta * A) - sigma * E + delta * Q
    dAdt = sigma * (1 - rho) * E - epsilonA * A - gammaA * A
    dIdt = sigma * rho * E - gammaI * I - dI * I - epsilonI * I
    dDdt = epsilonA * A + epsilonI * I - dD * D - gammaD * D
    dRdt = gammaA * A + gammaI * I + gammaD * D
    dMdt = dD * D + dI * I
    dwdt = [dSdt, dQdt, dEdt, dAdt, dIdt, dDdt, dRdt, dMdt]
    return dwdt


def rodamodelo2dia(vetor_condicao, c0, c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12, c13):
    #timespan
    t = np.linspace(0, 1, 20)
#resolucao
    w = odeint(model2, vetor_condicao, t, args=(c0, c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12, c13))
#retorna valor um ano depois
    return w[-1, :]


@numba.jit
def EQM(vetor1, vetor2):
    tamanho = min(len(vetor1), len(vetor2))
    soma = 0
    for n in range(tamanho):
        soma += (vetor1[n] - vetor2[n]) ** 2
    return soma/tamanho

def rodacontagio_D_acum(vetor_coeficientes, vetor_inicial, tempo):
    Lista = []
    S = []
    Q = []
    E = []
    A = []
    I = []
    D = []
    R = []
    M = []
    D_Acum = []

    Lista.append(vetor_inicial)
    S.append(vetor_inicial[0])
    Q.append(vetor_inicial[1])
    E.append(vetor_inicial[2])
    A.append(vetor_inicial[3])
    I.append(vetor_inicial[4])
    D.append(vetor_inicial[5])
    R.append(vetor_inicial[6])
    M.append(vetor_inicial[7])
    D_Acum.append(vetor_inicial[5])

    c = vetor_coeficientes
    for k in range(tempo):
        Lista.append(rodamodelo2dia(Lista[k], c[0], c[1], c[2], c[3],
                                    c[4], c[5], c[6], c[7], c[8], c[9], c[10], c[11], c[12], c[13]))
        S.append(Lista[k+1][0])
        Q.append(Lista[k+1][1])
        E.append(Lista[k+1][2])
        A.append(Lista[k+1][3])
        I.append(Lista[k+1][4])
        D.append(Lista[k+1][5])
        R.append(Lista[k+1][6])
        M.append(Lista[k+1][7])
        #D_Acum.append(D_Acum[-1] + Lista[k+1][4] * c[7] + Lista[k+1][3] * c[6] - Lista[k+1][5] * c[12])
        D_Acum.append(D_Acum[-1] + Lista[k+1][4] * c[7] + Lista[k+1][3] * c[6])

    return D_Acum

def rodacontagio_M_acum(vetor_coeficientes, vetor_inicial, tempo):
    Lista = []
    S = []
    Q = []
    E = []
    A = []
    I = []
    D = []
    R = []
    M = []
    M_Acum = []

    Lista.append(vetor_inicial)
    S.append(vetor_inicial[0])
    Q.append(vetor_inicial[1])
    E.append(vetor_inicial[2])
    A.append(vetor_inicial[3])
    I.append(vetor_inicial[4])
    D.append(vetor_inicial[5])
    R.append(vetor_inicial[6])
    M.append(vetor_inicial[7])
    M_Acum.append(1)

    c = vetor_coeficientes
    for k in range(tempo):
        Lista.append(rodamodelo2dia(Lista[k], c[0], c[1], c[2], c[3],
                                    c[4], c[5], c[6], c[7], c[8], c[9], c[10], c[11], c[12], c[13]))
        S.append(Lista[k+1][0])
        Q.append(Lista[k+1][1])
        E.append(Lista[k+1][2])
        A.append(Lista[k+1][3])
        I.append(Lista[k+1][4])
        D.append(Lista[k+1][5])
        R.append(Lista[k+1][6])
        M.append(Lista[k+1][7])
        #D_Acum.append(D_Acum[-1] + Lista[k+1][4] * c[7] + Lista[k+1][3] * c[6] - Lista[k+1][5] * c[12])
        M_Acum.append(M_Acum[-1] + Lista[k+1][5] * c[12])

    return M_Acum


def residual_edo_D(params, data, param):
    beta = params['beta'].value
    theta = params['theta'].value
    p = params['p'].value
    lambda0 = params['lambda0'].value
    sigma = params['sigma'].value
    rho = params['rho'].value
    epsilonA = params['epsilonA'].value
    epsilonI = params['epsilonI'].value
    gammaA = params['gammaA'].value
    gammaI = params['gammaI'].value
    gammaD = params['gammaD'].value
    dI = params['dI'].value
    dD = params['dD'].value
    delta = params['delta'].value
    day = params['day'].value
    S0 = params['S0'].value
    Q0 = params['Q0'].value
    E0 = params['E0'].value
    A0 = params['A0'].value
    I0 = params['I0'].value
    D0 = params['D0'].value
    R0 = params['R0'].value
    M0 = params['M0'].value

    vet = (beta, theta, p, lambda0, sigma, rho, epsilonA,
           epsilonI, gammaA, gammaI, gammaD, dI, dD, delta)
    init_cond = (S0, Q0, E0, A0, I0, D0, R0, M0)

    model = rodacontagio_D_acum(vet, init_cond, day-1)
    return np.array(model)-np.array(data)


def residual_edo_M(params, data, param):
    beta = params['beta'].value
    theta = params['theta'].value
    p = params['p'].value
    lambda0 = params['lambda0'].value
    sigma = params['sigma'].value
    rho = params['rho'].value
    epsilonA = params['epsilonA'].value
    epsilonI = params['epsilonI'].value
    gammaA = params['gammaA'].value
    gammaI = params['gammaI'].value
    gammaD = params['gammaD'].value
    dI = params['dI'].value
    dD = params['dD'].value
    delta = params['delta'].value
    day = params['day'].value
    S0 = params['S0'].value
    Q0 = params['Q0'].value
    E0 = params['E0'].value
    A0 = params['A0'].value
    I0 = params['I0'].value
    D0 = params['D0'].value
    R0 = params['R0'].value
    M0 = params['M0'].value

    vet = (beta, theta, p, lambda0, sigma, rho, epsilonA,
           epsilonI, gammaA, gammaI, gammaD, dI, dD, delta)
    init_cond = (S0, Q0, E0, A0, I0, D0, R0, M0)

    model = rodacontagio_M_acum(vet, init_cond, day-1)
    return np.array(model)-np.array(data)


def eval_edo_D(params, forecast):
    beta = params['beta'].value
    theta = params['theta'].value
    p = params['p'].value
    lambda0 = params['lambda0'].value
    sigma = params['sigma'].value
    rho = params['rho'].value
    epsilonA = params['epsilonA'].value
    epsilonI = params['epsilonI'].value
    gammaA = params['gammaA'].value
    gammaI = params['gammaI'].value
    gammaD = params['gammaD'].value
    dI = params['dI'].value
    dD = params['dD'].value
    delta = params['delta'].value
    day = params['day'].value + forecast
    S0 = params['S0'].value
    Q0 = params['Q0'].value
    E0 = params['E0'].value
    A0 = params['A0'].value
    I0 = params['I0'].value
    D0 = params['D0'].value
    R0 = params['R0'].value
    M0 = params['M0'].value

    vet = (beta, theta, p, lambda0, sigma, rho, epsilonA,
           epsilonI, gammaA, gammaI, gammaD, dI, dD, delta)
    init_cond = (S0, Q0, E0, A0, I0, D0, R0, M0)

    model = rodacontagio_D_acum(vet, init_cond, day-1)
    return model


def eval_edo_M(params, forecast):
    beta = params['beta'].value
    theta = params['theta'].value
    p = params['p'].value
    lambda0 = params['lambda0'].value
    sigma = params['sigma'].value
    rho = params['rho'].value
    epsilonA = params['epsilonA'].value
    epsilonI = params['epsilonI'].value
    gammaA = params['gammaA'].value
    gammaI = params['gammaI'].value
    gammaD = params['gammaD'].value
    dI = params['dI'].value
    dD = params['dD'].value
    delta = params['delta'].value
    day = params['day'].value + forecast
    S0 = params['S0'].value
    Q0 = params['Q0'].value
    E0 = params['E0'].value
    A0 = params['A0'].value
    I0 = params['I0'].value
    D0 = params['D0'].value
    R0 = params['R0'].value
    M0 = params['M0'].value

    vet = (beta, theta, p, lambda0, sigma, rho, epsilonA,
           epsilonI, gammaA, gammaI, gammaD, dI, dD, delta)
    init_cond = (S0, Q0, E0, A0, I0, D0, R0, M0)

    model = rodacontagio_M_acum(vet, init_cond, day-1)
    return model
