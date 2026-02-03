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
Explicação 
## Em Ré Com Salto Fixo : ERCSF
Explicação 
# Sequêncial com Salto Fixo : SCSF
Explicação 

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
