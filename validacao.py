# -*- coding: utf-8 -*-
"""
Created on Tue Jun 18 10:18:52 2019
@author: João Victor Ribeiro de Jesus
"""

from __future__ import print_function


# GALAXIAS COMO SENDO REFERENTE À CLASSIFICACAO '0'
def compararClassificacao1(objetos):

    acertos = 0
    erros = 0

    VP = 0
    VN = 0
    FP = 0
    FN = 0

    estrelasExistentes = 0
    galaxiasExistentes = 0
    totalVarianciaGalaxias = 0
    totalVarianciaEstrelas = 0

    for objeto in objetos:

        if 1 == objeto["classificacaoGerada"]:
            galaxiasExistentes += 1
            totalVarianciaGalaxias += objeto["variancia"]
        if 0 == objeto["classificacaoGerada"]:
            estrelasExistentes += 1
            totalVarianciaEstrelas += objeto["variancia"]

        if 'GALAXY' in objeto["classificacao"] and 1 == objeto["classificacaoGerada"]:
            acertos += 1
            VP += 1

        elif 'STAR' in objeto["classificacao"] and 1 == objeto["classificacaoGerada"]:
            erros += 1
            FP += 1

        elif 'GALAXY' in objeto["classificacao"] and 0 == objeto["classificacaoGerada"]:
            erros += 1
            FN += 1

        elif 'STAR' in objeto["classificacao"] and 0 == objeto["classificacaoGerada"]:
            acertos += 1
            VN += 1

    mediaG = totalVarianciaGalaxias / galaxiasExistentes

    #print('Galaxias acertadas:', acertosGalaxias, 'Galaxias erradas:', errosGalaxias, 'Estrelas acertadas:', acertosEstrelas, 'Estrelas erradas:', errosEstrelas)

    return acertos, erros, estrelasExistentes, galaxiasExistentes, mediaG, VP, VN, FP, FN


# GALAXIAS COMO SENDO REFERENTE À CLASSIFICACAO '0'
def compararClassificacao0(objetos):

    acertos = 0
    erros = 0

    VP = 0
    VN = 0
    FP = 0
    FN = 0

    estrelasExistentes = 0
    galaxiasExistentes = 0
    totalVarianciaGalaxias = 0
    totalVarianciaEstrelas = 0

    for objeto in objetos:

        if 0 == objeto["classificacaoGerada"]:
            galaxiasExistentes += 1
            totalVarianciaGalaxias += objeto["variancia"]
        if 1 == objeto["classificacaoGerada"]:
            estrelasExistentes += 1
            totalVarianciaEstrelas += objeto["variancia"]

        if 'GALAXY' in objeto["classificacao"] and 0 == objeto["classificacaoGerada"]:
            acertos += 1
            VP += 1

        elif 'STAR' in objeto["classificacao"] and 0 == objeto["classificacaoGerada"]:
            erros += 1
            FP += 1

        elif 'GALAXY' in objeto["classificacao"] and 1 == objeto["classificacaoGerada"]:
            erros += 1
            FN += 1

        elif 'STAR' in objeto["classificacao"] and 1 == objeto["classificacaoGerada"]:
            acertos += 1
            VN += 1


    mediaG = totalVarianciaGalaxias / galaxiasExistentes

    #print('Galaxias acertadas:', acertosGalaxias, 'Galaxias erradas:', errosGalaxias, 'Estrelas acertadas:', acertosEstrelas, 'Estrelas erradas:', errosEstrelas)

    return acertos, erros, estrelasExistentes, galaxiasExistentes, mediaG, VP, VN, FP, FN