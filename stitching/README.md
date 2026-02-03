## Como utilizar

### Entradas

#### Configuração dos fragmentos 
Ajuste o caminho do arquivo onde estão armazenadas as imagens em:

      frames = treat_input("/home/atosarruda/Documentos/IC - Erikson/DocAI/stitching/db/5")

Talvez o número 5 seja alterado conforme esse respositório avança.

#### Selecionar algoritmo
Ajuste qual algoritmo de seleção será utilizado para o stitching em :

    op = 1 # 1 - ERCS ; 2 - SCS ; 3 - ERCSF ; 4 SCSF

1) ERCS
2) SCS
3) ERCSF
4) SCSF


#### Tamanho do salto
Ajuste o tamanho do salto no caso do algoritmo 3 e 4 em :

    saltoFixo = 0 #Configura tamanho de salto caso op == 3 || 4;

### Referência Visual
<img width="532" height="67" alt="image" src="https://github.com/user-attachments/assets/d236bda3-5d1a-499e-88ab-385e218bc42d" />
<img width="532" height="67" alt="image" src="https://github.com/user-attachments/assets/dcec407a-8948-44a7-9d37-7196468e607d" />

## Em Ré Com Salto : ERCS
ERCS assume que existe sobreposição entre imagens próximas. Então, ele busca descartas as imagens redundantes a cada passo de comparação. 

A seleção de imagens a serem comparadas ocorre através de um alvo e um Pivô:

- #### Pivô 
  É a ultima imagem do vetor.
- #### Alvo
  É a imagem na posição do meio do vetor.
<img width="720" height="680" alt="ERCS X Padrão X SCS (1)" src="https://github.com/user-attachments/assets/23d66929-fe05-4638-992e-e1e13a62701d" />

### Caso 1 ( Comparação bem sucedida  )
Nesse caso avaliamos como o aloritmo se porta após conseguir fazer a colagem das duas imagens. 
1) É gerada uma nova imagem chamada de **mosaico** contendo a colagem da imagem Alvo e Pivô.
2) As imagens do entre o Alvo até o Pivô são dercaradas.
3) A imagem Alvo se torna o novo Pivô.
4) A imagem na pocisão do meio desse novo vetor se torna o novo Alvo.

___observação: no caso do vetor  ter um tamanho par, deve-se tentar alcançar a posição mais distante do vetor, com a função chão da divisão___

Os passos acima se repetem sempre que houver uma comparação bem sucedida. E se encerra caso o Alvo e o Pivô sejam a mesma imagem.

### Caso 2 ( Comparação mal sucedida )
Nesse caso avaliamos como o algoritmo se porta após falhar em fazer a colagem das duas imagens.
1) Torna a imagem seguinte a do Alvo como novo Alvo.
2) Compara o novo Alvo com o Pivô.

Caso a colagem seja bem sucessida volte ao caso 1. Caso não, volte ao caso 2.
Caso o Alvo seja igual ao Pivô, encerre.

## Sequêncial Com Salto : SCS
SCS assume as mesmas premissas que ERCS, porem inicia a colagem do primeiro elemento do vetor de imagens. Assim garante que a primeira imagem seja mantida no resultado final.

A seleção de imagens a serem comparadas ocorre através de um alvo e um Pivô:

- #### Pivô 
  É a primeira imagem do vetor.
- #### Alvo
  É a imagem na posição do meio do vetor.
  
<img width="720" height="680" alt="ERCS X Padrão X SCS (2)" src="https://github.com/user-attachments/assets/78c9b9d0-8823-405f-a2a7-5c5ad8926e8b" />
### Caso 1 ( Comparação bem sucedida  )
Nesse caso avaliamos como o aloritmo se porta após conseguir fazer a colagem das duas imagens. 
1) É gerada uma nova imagem chamada de **mosaico** contendo a colagem da imagem Alvo e Pivô.
2) As imagens do entre o Alvo até o Pivô são dercaradas.
3) A imagem Alvo se torna o novo Pivô.
4) A imagem na pocisão do meio desse novo vetor se torna o novo Alvo.

___observação: no caso do vetor  ter um tamanho par, deve-se tentar alcançar a posição mais distante do vetor, com a função teto da divisão___

Os passos acima se repetem sempre que houver uma comparação bem sucedida. E se encerra caso o Alvo e o Pivô sejam a mesma imagem.

### Caso 2 ( Comparação mal sucedida )
Nesse caso avaliamos como o algoritmo se porta após falhar em fazer a colagem das duas imagens.
1) Torna a imagem seguinte a do Alvo como novo Alvo.
2) Compara o novo Alvo com o Pivô.

Caso a colagem seja bem sucessida volte ao caso 1. Caso não, volte ao caso 2.
Caso o Alvo seja igual ao Pivô, encerre.
## Em Ré Com Salto Fixo : ERCSF
ERCSF altera o modo de escolher o alvo. No ERCS o alvo é escolhido através de uma divisão, tendo como parâmetro o tamanho do vetor. Para ERCSF o vetor alvo ocorre de modo fixo de acordo com um valor pré-determinado.

Básicamente, ele seleciona uma posição do vetor a partir do pivô com um valor fixo determinado. 

<img width="720" height="680" alt="ERCS X Padrão X SCS (4)" src="https://github.com/user-attachments/assets/e4177aa3-905c-45bd-a726-9642d7169ecc" />

# Sequêncial com Salto Fixo : SCSF
SCSF altera o modo de escolher o alvo. No SCS o alvo é escolhido através de uma divisão, tendo como parâmetro o tamanho do vetor. Para ERCSF o vetor alvo ocorre de modo fixo de acordo com um valor pré-determinado.

Básicamente, ele seleciona uma posição do vetor a partir do pivô com um valor fixo determinado. 

<img width="720" height="680" alt="ERCS X Padrão X SCS (3)" src="https://github.com/user-attachments/assets/bde97396-81d8-43e5-a819-a24707b2588f" />

## Desempenho

<div>
Resultados obtidos da execução do algoritmo em 31 notas fiscais.
<img width="720" height="680" alt="ERCS X Padrão X SCS" src="https://github.com/user-attachments/assets/e2ddac81-9880-41d8-968e-b5b562dd5465" />

  #### resultados
Sequêncial Com Salto Fixo em 2 **SCSF2** alcançou o maior desempenho. 
1) SCSF2
2) ERCSF2
3) ERCSF1
4) SCSF1 e SCSF3
5) SCS
6) ERCS
7) Padrão
8) ERCSF3

</div>  
