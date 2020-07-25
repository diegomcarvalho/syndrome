def adaptavalores(dados_completos,pos_inicial,pos_final,numsequencias,numrevisao,numressorteio,semente,minpop,maxpop,mincoef,maxcoef,minparcela,maxparcela,minpac):

    passo = 0.001
    passopop = 1
    Final = []
    for i in range(5):
        Final.append(0)
    Final.append([])
    dados = dados_completos[pos_inicial:pos_final]
    random.seed(semente)
    tempo = pos_final - pos_inicial
    tam_inicial = dados_completos[pos_inicial]
    MAX_POP = maxpop
    minpop = minpop
    MAX_Q = 6
    MIN_Q = 0
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
    # Pré-processamento
    print('Pré-processamento')
    for r1 in range(4):
        coeficiente = coeficiente_min + r1 * passo_coef
        print(4-r1,end=' ')
        for r2 in range(4):
            tamanho_populacao = tamanho_populacao_min + r2 * passo_pop
            medias = rodarede(tam_inicial, coeficiente, tamanho_populacao,parcelaquarentena_med,max_quarentena_med,pacientes_recuperados_med,tempo,numsequencias//2)
            errotmp = math.sqrt(EQM(medias,dados))
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

    #Loop principal    
    for n in range(numrevisao):
        if (n % 20 == 0): 
            print(n, end=' ')
        numressorteio_tmp += 1
        max_quarentena = random.randint(max_quarentena_min, max_quarentena_max)       # sorteio - limites (0,6)
        parcelaquarentena = parcelaquarentena_min + random.random() * (parcelaquarentena_max - parcelaquarentena_min)          # sorteio - limites (0,1)
        coeficiente = coeficiente_min + random.random() * (coeficiente_max - coeficiente_min)           # sorteio - limites (3.5-5.5)
        tamanho_populacao = random.randint(tamanho_populacao_min,tamanho_populacao_max)
        pacientes_recuperados = random.randint(pacientes_recuperados_min, pacientes_recuperados_max)

        #rodarede(tam_inicial,coeficiente,tamanho_populacao,parcelaquarentena,max_contagio_quarentena,pacientes_recuperados,tempo,numsequencias)
        
        medias = rodarede(tam_inicial, coeficiente, tamanho_populacao,parcelaquarentena,max_quarentena,pacientes_recuperados,tempo,numsequencias)

        errotmp = math.sqrt(EQM(medias,dados))
        
        #Busca local em torno do coeficiente e do tamanho de populacao
        if(errotmp<erro):
            coeficientetmp1 = max(mincoef,coeficiente - passo)
            coeficientetmp2 = min(maxcoef,coeficiente + passo)
            medias1 = rodarede(tam_inicial, coeficientetmp1, tamanho_populacao,parcelaquarentena,max_quarentena,pacientes_recuperados,tempo,numsequencias)
            medias2 = rodarede(tam_inicial, coeficientetmp2, tamanho_populacao,parcelaquarentena,max_quarentena,pacientes_recuperados,tempo,numsequencias)
            errotmp1 = math.sqrt(EQM(medias1,dados))
            errotmp2 = math.sqrt(EQM(medias2,dados))
            if(errotmp1<errotmp):
                while (errotmp1<errotmp):
                    errotmp = errotmp1
                    medias = medias1
                    coeficiente = coeficientetmp1
                    coeficientetmp1 = max(mincoef,coeficiente - passo)
                    medias1 = rodarede(tam_inicial, coeficientetmp1, tamanho_populacao,parcelaquarentena,max_quarentena,pacientes_recuperados,tempo,numsequencias)
                    errotmp1 = math.sqrt(EQM(medias1,dados))
            elif(errotmp2<errotmp):
                while (errotmp2<errotmp):
                    errotmp = errotmp2
                    medias = medias2
                    coeficiente = coeficientetmp2
                    coeficientetmp2 = min(maxcoef,coeficiente + passo)
                    medias2 = rodarede(tam_inicial, coeficientetmp2, tamanho_populacao,parcelaquarentena,max_quarentena,pacientes_recuperados,tempo,numsequencias)
                    errotmp2 = math.sqrt(EQM(medias2,dados))
                
            poptmp1 = max(minpop,tamanho_populacao - passopop)
            poptmp2 = min(maxpop,tamanho_populacao + passopop)
            medias1 = rodarede(tam_inicial, coeficiente,poptmp1,parcelaquarentena,max_quarentena,pacientes_recuperados,tempo,numsequencias)
            medias2 = rodarede(tam_inicial, coeficiente,poptmp2,parcelaquarentena,max_quarentena,pacientes_recuperados,tempo,numsequencias)
            errotmp1 = math.sqrt(EQM(medias1,dados))
            errotmp2 = math.sqrt(EQM(medias2,dados))
            if(errotmp1<errotmp):
                while (errotmp1<errotmp):
                    errotmp = errotmp1
                    medias = medias1
                    tamanho_populacao = poptmp1
                    poptmp1 = max(minpop,tamanho_populacao - passopop)
                    medias1 = rodarede(tam_inicial, coeficiente,poptmp1,parcelaquarentena,max_quarentena,pacientes_recuperados,tempo,numsequencias)
                    errotmp1 = math.sqrt(EQM(medias1,dados))
            elif(errotmp2<errotmp):
                while (errotmp2<errotmp):
                    errotmp = errotmp2
                    medias = medias2
                    tamanho_populacao = poptmp2
                    poptmp2 = min(maxpop,tamanho_populacao + passopop)
                    medias2 = rodarede(tam_inicial, coeficiente,poptmp2,parcelaquarentena,max_quarentena,pacientes_recuperados,tempo,numsequencias)
                    errotmp2 = math.sqrt(EQM(medias2,dados))
                
        
        if(errotmp<erro):
            print('\n{0:5d};'.format(n),end=' ')
            print('Erro - {0:5.2f};'.format(errotmp),end=' ')
            print('Coef - {0:5.5f};'.format(coeficiente),end=' ')
            print('Parc Q - {0:5.5f};'.format(parcelaquarentena),end=' ')
            print('Tam Pop - {0:5d};'.format(int(tamanho_populacao)),end=' ')
            print('Max. Q - {0:5d};'.format(max_quarentena),end=' ')
            print('Pac. Recup. - {0:5d}\n'.format(pacientes_recuperados),end=' ')
            #numressorteio_tmp = 0
            erro = errotmp
            
            Final[0]=tamanho_populacao
            Final[1]=coeficiente
            Final[2]=parcelaquarentena
            Final[3]=max_quarentena
            Final[4]=pacientes_recuperados
            Final[5]=medias
            lista_max_quarentenas.append(max_quarentena)
            lista_parcelaquarentenas.append(parcelaquarentena)
            lista_coeficientes.append(coeficiente)
            lista_tamanho_populacoes.append(tamanho_populacao)
            lista_pacientes_recuperados.append(pacientes_recuperados)
            
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

        if (erro/dados[-1]<0.01):
            break

    print('\nPronto!\n')
    
    return Final