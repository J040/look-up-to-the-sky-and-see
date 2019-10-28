# -*- coding: utf-8 -*-
"""
Created on Tue Jun 18 10:18:52 2019
@author: João Victor Ribeiro de Jesus
"""

from __future__ import print_function
import os, sys
import cv2
import numpy as np
from copy import copy, deepcopy

import buscaCaracteristicas
import kmeans
import requisicoes
import validacao
import matrizConfusao

def gerarAcertos (objetos, dados, altura, largura, ra, dec, qtd_objetos) :

    # REALIZAÇÃO DO KMEANS
    classificacoes = kmeans.aplicarIA(dados)

    # ACRESCENTA AS COORDENADAS RA E DEC, ALÉM DA CLASSIFICAÇÃO CORRETA AO OBJETO ROTULADO (objeto["ra"],objeto["dec"],objeto["classificacao"])
    print('Gerando taxa de acerto...')
    requisicoes.gerarTaxaAcerto(objetos, altura, largura, ra, dec)


    # ATRIBUIR CLASSIFICAÇÃO AO OBJETO
    for i in range(len(objetos)):
        objetos[i]["classificacaoGerada"] = classificacoes[i]


    # VERIFICAR SE '0' OU '1' SERÁ CONSIDERADO GALÁXIA (NA CLASSIFICACAO)
    acertos0, erros0, estrelas0, galaxias0, mediaVarianciaGalaxias0, VP0, VN0, FP0, FN0 = validacao.compararClassificacao0(objetos)
    acertos1, erros1, estrelas1, galaxias1, mediaVarianciaGalaxias1, VP1, VN1, FP1, FN1 = validacao.compararClassificacao1(objetos)

    print('\nClassificação 0 - Estrelas:', estrelas0, 'Galáxias:', galaxias0, 'Media Variancia Galaxias:', mediaVarianciaGalaxias0)
    print('Classificação 1 - Estrelas:', estrelas1, 'Galáxias:', galaxias1, 'Media Variancia Galaxias:', mediaVarianciaGalaxias1)

    print('Quantidade de objetos classificados:', qtd_objetos)

    # DESENHA O RETANGULO ENVOLVENTE NOS OBJETOS CLASSIFICADOS PELO KMEANS E APAGA ESTRELAS
    if mediaVarianciaGalaxias0 < mediaVarianciaGalaxias1:
        classeGalaxia = 0
        classeEstrela = 1
        print('\nNúmero de acertos e erros com galáxias sendo referentes à classificação 0:', acertos0, erros0, 'Porcentagem:', acertos0 / (acertos0 + erros0), '%')
        print('VP (Galaxias = Galaxias reais) | VN (Estrelas = Estrelas reais) | FP (Estrelas classificadas como galáxias) | FN (Galáxias classificadas como estrelas)')
        print('Matriz de confusão - VP:', VP0, 'VN:', VN0, 'FP:', FP0, 'FN:', FN0)
    else:
        classeGalaxia = 1
        classeEstrela = 0
        print('\nNúmero de acertos e erros com galáxias sendo referentes à classificação 1:', acertos1, erros1, 'Porcentagem:', acertos1 / (acertos1 + erros1), '%')
        print('VP (Galaxias = Galaxias reais) | VN (Estrelas = Estrelas reais) | FP (Estrelas classificadas como galáxias) | FN (Galáxias classificadas como estrelas)')
        print('Matriz de confusão - VP:', VP1, 'VN:', VN1, 'FP:', FP1, 'FN:', FN1)


    # GERAR VETOR COM A CLASSIFICACAO REAL (com valores 0's e 1's)
    classificacoesReal = matrizConfusao.gerarVetores(objetos,classificacoes, classeGalaxia, classeEstrela)

    # DEIXANDO O VETOR DAS CLASSIFICAÇÕES GERADAS DO MESMO FORMATO COM O VETOR DAS CLASSIFICACOES REAIS
    classificacoesGerada = []
    for i in classificacoes:
        classificacoesGerada.append(i)

    return classificacoesGerada, classeEstrela, classeGalaxia, classificacoesReal

def executar (objetos, dados, qtd_objetos) :

        zeros = 0
        uns = 0

        # REALIZAÇÃO DO KMEANS
        classificacoes = kmeans.aplicarIA(dados)

        for i in classificacoes:
            if i == 0:
                zeros += 1
            else:
                uns += 1

        # ATRIBUIR CLASSIFICAÇÃO AO OBJETO
        for i in range(len(objetos)):
            objetos[i]["classificacaoGerada"] = classificacoes[i]

        print('Quantidade de objetos classificados:', qtd_objetos)

        if zeros > uns:
            classeGalaxia = 1
            classeEstrela = 0

        else:
            classeGalaxia = 0
            classeEstrela = 1

        return classificacoes, classeEstrela, classeGalaxia



