import numpy as np
import random
import math
import numba
from socnet import calculate_infected_varying

# Ajuste do Modelo de Redes - 10-05-2020
# Evolucao COVID-19 - Modelo 2- 16-03-2020

# 1.3<R0<5 => 6>coeficiente>2
def leidepotencias(xmin,coef,corte):
    return min((xmin * (random.random() ** (-1/coef)))-1,corte)

def chisquare(vetor1, vetor2):
    tamanho = min(len(vetor1),len(vetor2))
    soma = 0
    for n in range(tamanho):
        soma += (vetor1[n] - vetor2[n]) ** 2
    return math.sqrt(soma/tamanho)

def primeiroscasos(numero,pacientes_recuperados):
    lista_iniciais = []
    for k in range(numero):
        if (k<pacientes_recuperados):
            lista_iniciais.append([0,-1,0,0,0,1,0])
        else:    
            lista_iniciais.append([0,-1,1,random.randint(0,13),0,1,0]) 
    return lista_iniciais

def p2casos(n_tot, n_i0r):
    i0a = [0 for _ in range(14)]
    i0r = [0 for _ in range(14)]
    for k in range(n_tot):
        if k < n_i0r:
            i0r[0] += 1
        else:
            i0a[random.randint(0, 13)] += 1
    return i0a, i0r

def p2rodarede(tam_inicial,coeficiente,tamanho_populacao,parcelaquarentena,max_contagio_quarentena,pacientes_recuperados,tempo,numsequencias):
    i0a, i0r = p2casos(tam_inicial, pacientes_recuperados)
    piq = [parcelaquarentena for _ in range(tempo)]
    pop = int(tamanho_populacao)
    
    result = calculate_infected_varying(tempo,pop,coeficiente,piq,numsequencias,max_contagio_quarentena,14,i0a,i0r,False)

    return result.mean

def pyrodarede(tam_inicial,coeficiente,tamanho_populacao,parcelaquarentena,max_contagio_quarentena,pacientes_recuperados,tempo,numsequencias):

    max_quarentena = max_contagio_quarentena

    Lista_final = []
    
    for i in range(tempo):
        Lista_final.append(0)
    
    for k in range(numsequencias):
        lista_inicial = primeiroscasos(tam_inicial,pacientes_recuperados)
        #print(k, end=' ')
        lista_todos = lista_inicial
        populacao_disponivel = tamanho_populacao
        for dia in range(tempo):
            populacao_contaminada = len(lista_todos)
            Lista_final[dia] += populacao_contaminada/numsequencias
            for paciente in range(populacao_contaminada):
                if (lista_todos[paciente][2]==1):
                    if (lista_todos[paciente][3]<14):
                        numero_novos = int(round(leidepotencias(1,coeficiente,100)))
                        if(lista_todos[paciente][6]==1):
                            if(lista_todos[paciente][4]+numero_novos>max_quarentena):
                                numero_novos = max_quarentena - lista_todos[paciente][4]
                                if(numero_novos<0):
                                    numero_novos = 0
                        contaminados_novos = 0
                        for novos in range(numero_novos):
                            if (random.randint(1,tamanho_populacao)<populacao_disponivel):
                                contaminados_novos += 1
                                populacao_disponivel -= 1
                                if(random.random()<parcelaquarentena):
                                    lista_todos.append([dia,paciente,1,0,0,1,1])
                                else:
                                    lista_todos.append([dia,paciente,1,0,0,1,0])
                        lista_todos[paciente][3] += 1
                        lista_todos[paciente][4] += contaminados_novos
                    else:
                        lista_todos[paciente][2] = 0
                        lista_todos[paciente][5] = 0
    
    return Lista_final



def adaptavalores(dados_completos,pos_inicial,pos_final,numsequencias,numrevisao,numressorteio,nomearquivo,semente,minpop,maxpop,mincoef,maxcoef,minparcela,maxparcela,minpac):

    passo = 0.001
    passopop = 1
    Final = []
    for i in range(5):
        Final.append(0)
    
    dados = dados_completos[pos_inicial:pos_final]
    random.seed(semente)
    tempo = pos_final - pos_inicial
    tam_inicial = dados_completos[pos_inicial]
    MAX_POP = maxpop
    minpop = minpop
    MAX_Q = 6
    MIN_Q = 0
    F = open(nomearquivo,'w') 
    F.write('Modelo de Redes Sociais - Adaptativo\n')
    F.write(nomearquivo)
    F.write('\nParametros;;;;;Dados (primeira linha - dados reais)\n')
    F.write('Coeficiente;Parcela_em_quarentena;Tam_Pop;Max_contagio;Pac_Recup;Erro;')
    for n in range(pos_inicial,pos_final):
        F.write('{0:5d};'.format(dados_completos[n]))
    F.write('\n')
    max_quarentena_min = MIN_Q
    max_quarentena_max = MAX_Q
    lista_max_quarentenas = []
    parcelaquarentena_min = minparcela
    parcelaquarentena_max = maxparcela
    lista_parcelaquarentenas = []
    coeficiente_min = mincoef
    coeficiente_max = maxcoef
    lista_coeficientes = []
    tamanho_populacao_min = minpop
    tamanho_populacao_max = MAX_POP
    lista_tamanho_populacoes = []
    pacientes_recuperados_min = minpac
    pacientes_recuperados_max = dados[0]
    lista_pacientes_recuperados = []
    erro = 50000
    numressorteio_tmp = 0
    numressorteios = 1
    parcelaquarentena_med = (parcelaquarentena_max + parcelaquarentena_min)/2
    max_quarentena_med = round((max_quarentena_min+max_quarentena_max)/2)
    pacientes_recuperados_med = round((minpac + dados[0])/2)
    passo_coef = (coeficiente_max - coeficiente_min)/4
    passo_pop = round((tamanho_populacao_max - tamanho_populacao_min)/4)
    erro_prep = erro
    #print('Pré-processamento')
    for r1 in range(4):
        coeficiente = coeficiente_min + r1 * passo_coef
        #print(4-r1,end=' ')
        for r2 in range(4):
            tamanho_populacao = tamanho_populacao_min + r2 * passo_pop
            medias = p2rodarede(tam_inicial, coeficiente, tamanho_populacao,parcelaquarentena_med,max_quarentena_med,pacientes_recuperados_med,tempo,numsequencias//2)
            errotmp = chisquare(medias, dados)
            if(errotmp<erro_prep):
                coeficiente_min_tmp = max(mincoef,coeficiente-passo_coef)
                coeficiente_max_tmp = coeficiente + passo_coef
                tamanho_populacao_min_tmp = max(minpop,tamanho_populacao-passo_pop)
                tamanho_populacao_max_tmp = min(MAX_POP,tamanho_populacao+passo_pop)
                erro_prep = errotmp
    
    coeficiente_min = coeficiente_min_tmp
    coeficiente_max = coeficiente_max_tmp
    tamanho_populacao_min = tamanho_populacao_min_tmp
    tamanho_populacao_max = tamanho_populacao_max_tmp
        
    for n in range(numrevisao):
        # if (n % 20 == 0): 
        #     print(n, end=' ')
        numressorteio_tmp += 1
        max_quarentena = random.randint(max_quarentena_min, max_quarentena_max)       # sorteio - limites (0,6)
        parcelaquarentena = parcelaquarentena_min + random.random() * (parcelaquarentena_max - parcelaquarentena_min)          # sorteio - limites (0,1)
        coeficiente = coeficiente_min + random.random() * (coeficiente_max - coeficiente_min)           # sorteio - limites (3.5-5.5)
        tamanho_populacao = random.randint(tamanho_populacao_min, tamanho_populacao_max)
        # Bacalho...
        if pacientes_recuperados_min > pacientes_recuperados_max:
            pacientes_recuperados_min, pacientes_recuperados_max = pacientes_recuperados_max, pacientes_recuperados_min
        pacientes_recuperados = random.randint(pacientes_recuperados_min, pacientes_recuperados_max)

        medias = p2rodarede(tam_inicial, coeficiente, tamanho_populacao,parcelaquarentena,max_quarentena,pacientes_recuperados,tempo,numsequencias)

        errotmp = chisquare(medias, dados)
        
        #Busca local em torno do coeficiente e do tamanho de populacao
        if(errotmp<erro):
            coeficientetmp1 = max(mincoef,coeficiente - passo)
            coeficientetmp2 = min(maxcoef,coeficiente + passo)
            medias1 = p2rodarede(tam_inicial, coeficientetmp1, tamanho_populacao,parcelaquarentena,max_quarentena,pacientes_recuperados,tempo,numsequencias)
            medias2 = p2rodarede(tam_inicial, coeficientetmp2, tamanho_populacao,parcelaquarentena,max_quarentena,pacientes_recuperados,tempo,numsequencias)
            errotmp1 = chisquare(medias1, dados)
            errotmp2 = chisquare(medias2, dados)
            if(errotmp1<errotmp):
                while (errotmp1<errotmp):
                    errotmp = errotmp1
                    medias = medias1
                    coeficiente = coeficientetmp1
                    coeficientetmp1 = max(mincoef,coeficiente - passo)
                    medias1 = p2rodarede(tam_inicial, coeficientetmp1, tamanho_populacao,parcelaquarentena,max_quarentena,pacientes_recuperados,tempo,numsequencias)
                    errotmp1 = chisquare(medias1, dados)
            elif(errotmp2<errotmp):
                while (errotmp2<errotmp):
                    errotmp = errotmp2
                    medias = medias2
                    coeficiente = coeficientetmp2
                    coeficientetmp2 = min(maxcoef,coeficiente + passo)
                    medias2 = p2rodarede(tam_inicial, coeficientetmp2, tamanho_populacao,parcelaquarentena,max_quarentena,pacientes_recuperados,tempo,numsequencias)
                    errotmp2 = chisquare(medias2, dados)
                
            poptmp1 = max(minpop,tamanho_populacao - passopop)
            poptmp2 = min(maxpop,tamanho_populacao + passopop)
            medias1 = p2rodarede(tam_inicial, coeficiente,poptmp1,parcelaquarentena,max_quarentena,pacientes_recuperados,tempo,numsequencias)
            medias2 = p2rodarede(tam_inicial, coeficiente,poptmp2,parcelaquarentena,max_quarentena,pacientes_recuperados,tempo,numsequencias)
            errotmp1 = chisquare(medias1, dados)
            errotmp2 = chisquare(medias2, dados)
            if(errotmp1<errotmp):
                while (errotmp1<errotmp):
                    errotmp = errotmp1
                    medias = medias1
                    tamanho_populacao = poptmp1
                    poptmp1 = max(minpop,tamanho_populacao - passopop)
                    medias1 = p2rodarede(tam_inicial, coeficiente,poptmp1,parcelaquarentena,max_quarentena,pacientes_recuperados,tempo,numsequencias)
                    errotmp1 = chisquare(medias1, dados)
            elif(errotmp2<errotmp):
                while (errotmp2<errotmp):
                    errotmp = errotmp2
                    medias = medias2
                    tamanho_populacao = poptmp2
                    poptmp2 = min(maxpop,tamanho_populacao + passopop)
                    medias2 = p2rodarede(tam_inicial, coeficiente,poptmp2,parcelaquarentena,max_quarentena,pacientes_recuperados,tempo,numsequencias)
                    errotmp2 = chisquare(medias2, dados)
                
        
        if(errotmp<erro):
            #print('\n{0:5d};'.format(n),end=' ')
            #print('Erro - {0:5.2f};'.format(errotmp),end=' ')
            #print('Coef - {0:5.5f};'.format(coeficiente),end=' ')
            #print('Parc Q - {0:5.5f};'.format(parcelaquarentena),end=' ')
            #print('Tam Pop - {0:5d};'.format(tamanho_populacao),end=' ')
            #print('Max. Q - {0:5d};'.format(max_quarentena),end=' ')
            #print('Pac. Recup. - {0:5d}\n'.format(pacientes_recuperados),end=' ')
            numressorteio_tmp = 0
            erro = errotmp
            
            F.write('{0:5.5f};'.format(coeficiente))
            F.write('{0:5.5f};'.format(parcelaquarentena))
            F.write('{0:5d};'.format(tamanho_populacao))
            F.write('{0:5d};'.format(max_quarentena))
            F.write('{0:5d};'.format(pacientes_recuperados))
            F.write('{0:5.5f};'.format(erro))
            Final[0]=tamanho_populacao
            Final[1]=coeficiente
            Final[2]=parcelaquarentena
            Final[3]=max_quarentena
            Final[4]=pacientes_recuperados
            lista_max_quarentenas.append(max_quarentena)
            lista_parcelaquarentenas.append(parcelaquarentena)
            lista_coeficientes.append(coeficiente)
            lista_tamanho_populacoes.append(tamanho_populacao)
            lista_pacientes_recuperados.append(pacientes_recuperados)
            
            for m in range(tempo):
                F.write('{0:5.5f};'.format(medias[m]))
            F.write('\n')    
            
            if (max_quarentena >= round((max_quarentena_min + max_quarentena_max)/2,0)):
                max_quarentena_max = max_quarentena
            else:
                max_quarentena_min = max_quarentena
        
            if (parcelaquarentena > (parcelaquarentena_min + parcelaquarentena_max)/2):
                parcelaquarentena_max = parcelaquarentena
            else:
                parcelaquarentena_min = parcelaquarentena
        
            if (coeficiente > (coeficiente_min + coeficiente_max)/2):
                coeficiente_max = coeficiente
            else:
                coeficiente_min = coeficiente
        
            if (tamanho_populacao >= round((tamanho_populacao_min + tamanho_populacao_max)/2,0)):
                tamanho_populacao_max = tamanho_populacao
            else:
                tamanho_populacao_min = tamanho_populacao
                
                    
            if (pacientes_recuperados >= round((pacientes_recuperados_min + pacientes_recuperados_max)/2,0)):
                pacientes_recuperados_max = pacientes_recuperados
            else:
                pacientes_recuperados_min = pacientes_recuperados

        
        if ((numressorteio_tmp % numressorteio == 0) and len(lista_max_quarentenas)>2):
            #print('Ressorteio!')
            parte = (numressorteios % 4) /4
            max_quarentena_min = round(MIN_Q + parte * (min(lista_max_quarentenas) - MIN_Q))
            max_quarentena_max = round(max(lista_max_quarentenas) + parte * (MAX_Q - max(lista_max_quarentenas)))
            parcelaquarentena_min = minparcela + parte * (min(lista_parcelaquarentenas) - minparcela)
            parcelaquarentena_max = max(lista_parcelaquarentenas) + parte * (maxparcela - max(lista_parcelaquarentenas))
            coeficiente_min = mincoef + parte * (min(lista_coeficientes) - mincoef)
            coeficiente_max = max(lista_coeficientes) + parte * (maxcoef - max(lista_coeficientes))
            tamanho_populacao_min = round(minpop + parte * (min(lista_tamanho_populacoes) - minpop))
            tamanho_populacao_max = round(max(lista_tamanho_populacoes) + parte *(MAX_POP -  max(lista_tamanho_populacoes)))
            pacientes_recuperados_min = round(minpac + parte * (min(lista_pacientes_recuperados)-minpac))
            pacientes_recuperados_max = round(max(lista_pacientes_recuperados) + parte * (dados[0]-max(lista_pacientes_recuperados)))
            numressorteio_tmp = 1
            numressorteios += 1
            
        if (numressorteios % 4 == 0):
            #print('Revisão!')
            max_quarentena_min = MIN_Q
            max_quarentena_max = MAX_Q
            parcelaquarentena_min = minparcela
            parcelaquarentena_max = maxparcela
            coeficiente_min = mincoef
            coeficiente_max = maxcoef
            tamanho_populacao_min = minpop
            tamanho_populacao_max = MAX_POP
            pacientes_recuperados_min = minpac
            pacientes_recuperados_max = dados[0]
            numressorteio_tmp = 0
            numressorteios += 1
            if (len(lista_max_quarentenas)>3):
                lista_max_quarentenas.pop(0)
                lista_parcelaquarentenas.pop(0)
                lista_coeficientes.pop(0)
                lista_tamanho_populacoes.pop(0)
                lista_pacientes_recuperados.pop(0)

    #print('\nPronto!')
    F.close()
    
    return Final
 

def previsaoredes(vetor,numdias,tam_amostra,num_sequencias,tam_ressorteio,arquivo,minpop,maxpop,mincoef,maxcoef,minparc,maxparc,minrecuperados,semente):
    if (vetor[-12]>1000):
        fator = math.pow(10,(math.floor(math.log(vetor[-1],10))-2))
    else:
        fator = 1
    #print(fator)
    vetordiv = [int(x // fator) for x in vetor]
    contazero = 0
    tamanho_vetor = len(vetordiv)
    temp = []
    for i in range(tamanho_vetor):
        if (vetordiv[i] < 1):
            contazero += 1
        else:
            temp.append(vetordiv[i])
            
    vetordiv = temp    
    tamanho_vetor2 = len(vetordiv)
    minpop = minpop // fator
    maxpop = maxpop // fator
    minrecuperados = minrecuperados // fator
    resultado_ajuste = adaptavalores(vetordiv,0,tamanho_vetor2,tam_amostra,num_sequencias,tam_ressorteio,arquivo,semente,minpop,maxpop,mincoef,maxcoef,minparc,maxparc,minrecuperados)
    extrapolacao = p2rodarede(vetordiv[0],resultado_ajuste[1],resultado_ajuste[0],resultado_ajuste[2],resultado_ajuste[3],resultado_ajuste[4],tamanho_vetor2+numdias,tam_amostra)
    extrapolacao_mult = [round(EX * fator,6) for EX in extrapolacao]
    for j in range(contazero):
        extrapolacao_mult.insert(0,1)
    return extrapolacao_mult


def previsaoredeslp(vetor,numdias,tam_amostra,num_sequencias,tam_ressorteio,arquivo1,arquivo2,tamvetor1,minpop,maxpop,mincoef,maxcoef,minparc,maxparc,minrecuperados,semente):
    if (vetor[-12]>1000):
        fator = math.pow(10,(math.floor(math.log(vetor[-1],10))-2))
    else:
        fator = 1
    #print(fator)
    vetordiv = [int(x // fator) for x in vetor]
    contazero = 0
    tamanho_vetor = len(vetordiv)
    temp = []
    for i in range(tamanho_vetor):
        if (vetordiv[i] < 1):
            contazero += 1
        else:
            temp.append(vetordiv[i])
            
    vetordiv = temp    
    tamanho_vetor2 = len(vetordiv)
    vetordiv1 = vetordiv[0:tamvetor1]
    vetordiv2 = vetordiv[tamvetor1:]
    minpop = minpop // fator
    maxpop = maxpop // fator
    #print(minpop,maxpop)
    minrecuperados = minrecuperados // fator
    resultado_ajuste1 = adaptavalores(vetordiv1,0,len(vetordiv1),tam_amostra,num_sequencias,tam_ressorteio,arquivo1,semente,minpop,maxpop,mincoef,maxcoef,minparc,maxparc,minrecuperados)
    extrapolacao1 = p2rodarede(vetordiv1[0],resultado_ajuste1[1],resultado_ajuste1[0],resultado_ajuste1[2],resultado_ajuste1[3],resultado_ajuste1[4],len(vetordiv1),tam_amostra)
    extrapolacao_mult1 = [round(EX * fator,6) for EX in extrapolacao1]
    if (len(extrapolacao_mult1)>14):
        minrecuperados2 = int(max(0,2*extrapolacao_mult1[0]-extrapolacao_mult1[-1]))
    else:
        minrecuperados2 = 0
    resultado_ajuste2 = adaptavalores(vetordiv2,0,len(vetordiv2),tam_amostra,num_sequencias,tam_ressorteio,arquivo2,semente,minpop,maxpop,mincoef,maxcoef,minparc,maxparc,minrecuperados2)
    extrapolacao2 = p2rodarede(vetordiv2[0],resultado_ajuste2[1],resultado_ajuste2[0],resultado_ajuste2[2],resultado_ajuste2[3],resultado_ajuste2[4],len(vetordiv2)+numdias,tam_amostra)
    for j in range(contazero):
        extrapolacao_mult1.insert(0,1)
    extrapolacao_mult2 = [round(EX * fator,6) for EX in extrapolacao2]
    extrapolacao_mult1.extend(extrapolacao_mult2)
    return extrapolacao_mult1
