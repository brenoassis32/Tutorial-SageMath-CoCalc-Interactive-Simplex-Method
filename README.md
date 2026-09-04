# Tutorial SageMath + CoCalc — Método Simplex Interativo, Renderização LaTeX e Simplex Duas Fases

Este repositório apresenta um tutorial para utilização do **SageMath no CoCalc** na resolução de problemas de **Programação Linear pelo Método Simplex**.

O objetivo principal é documentar uma adaptação necessária para que as expressões matemáticas produzidas pelas classes do módulo `interactive_simplex_method` voltem a ser renderizadas corretamente em **LaTeX/MathJax** no ambiente do CoCalc.

Além da correção da renderização, o tutorial apresenta um exemplo prático de **modelagem de um problema de Programação Linear**, sua representação no SageMath e sua resolução utilizando o **Método Simplex Interativo**.

> **Importante:** a solução apresentada neste repositório utiliza *monkey patching*, ou seja, as alterações são realizadas durante a execução do notebook. Dessa forma, não é necessário recompilar ou modificar permanentemente a instalação do SageMath.

---

## 📋 Conteúdo

- [Objetivo](#objetivo)
- [O problema](#o-problema)
- [Problema de renderização LaTeX](#problema-de-renderização-latex)
- [Como a solução funciona](#como-a-solução-funciona)
- [Alterações realizadas no SageMath](#alterações-realizadas-no-sagemath)
- [Exemplo prático de modelagem](#exemplo-prático-de-modelagem)
- [Definição do modelo no SageMath](#definição-do-modelo-no-sagemath)
- [Resolução pelo Método Simplex](#resolução-pelo-método-simplex)
- [Visualização gráfica](#visualização-gráfica)
- [Execução do Método Simplex](#execução-do-método-simplex)
- [Execução no CoCalc](#execução-no-cocalc)
- [Estrutura do repositório](#estrutura-do-repositório)
- [Alteração permanente no código-fonte do SageMath](#alteração-permanente-no-código-fonte-do-sagemath)
- [Proposta de correção](#proposta-de-correção)
- [Por que utilizar `_repr_latex_()`?](#por-que-utilizar-_repr_latex_)
- [Simplex Duas Fases](#Método-Simplex-das-Duas-Fases)
- [Limitações](#limitações)
- [Referências](#referências)
- [Licença](#licença)

---

# Objetivo

O objetivo deste projeto é utilizar o módulo:

    sage.numerical.interactive_simplex_method

para construir, visualizar e resolver problemas de **Programação Linear**.

Além da solução numérica, busca-se preservar uma apresentação matemática adequada, permitindo visualizar:

- função objetivo;
- restrições;
- condições de não negatividade;
- dicionários Simplex;
- solução ótima;
- valor ótimo;
- etapas do algoritmo Simplex.

O SageMath possui suporte nativo à geração de representações LaTeX por meio do método `_latex_()`. No ambiente Jupyter/CoCalc, essas representações são encaminhadas ao MathJax para renderização no navegador.

---

# O problema

O módulo `interactive_simplex_method` do SageMath permite trabalhar de forma interativa com problemas de Programação Linear.

Entretanto, determinadas versões do SageMath podem apresentar problemas na renderização das expressões matemáticas produzidas pelas classes utilizadas pelo Método Simplex Interativo quando executadas no ambiente **CoCalc/Jupyter**.

O problema está relacionado principalmente à forma como determinadas expressões LaTeX são retornadas para o mecanismo de visualização do notebook.

Entre os elementos que podem causar problemas estão construções como:

    \begin{equation*}
    ...
    \end{equation*}

e determinados comandos utilizados na representação interna do SageMath, como:

    \displaystyle
    \mspace{-6mu}
    \renewcommand{\arraystretch}{1.5}

A proposta deste projeto é adaptar essas representações para que possam ser processadas corretamente pelo **MathJax** utilizado no ambiente CoCalc.

---

# Problema de renderização LaTeX

No SageMath, a representação LaTeX de um objeto é normalmente obtida por meio do método:

    _latex_()

No ambiente Jupyter/IPython, entretanto, existe uma camada adicional de representação responsável por indicar ao notebook que determinado conteúdo deve ser renderizado como matemática.

Uma forma simplificada de visualizar esse processo é:

    Objeto SageMath
          │
          ▼
       _latex_()
          │
          ▼
      Código LaTeX
          │
          ▼
      _repr_latex_()
          │
          ▼
     IPython / MathJax
          │
          ▼
    Expressão matemática renderizada

O problema observado neste projeto ocorre quando a saída gerada pelas classes do Simplex contém construções que não são interpretadas adequadamente pelo mecanismo de renderização utilizado pelo CoCalc.

---

# Como a solução funciona

A solução implementada no notebook modifica, durante a execução, alguns métodos das classes responsáveis pelo Método Simplex Interativo.

As principais classes envolvidas são:

    InteractiveLPProblem
    InteractiveLPProblemStandardForm
    LPDictionary

A adaptação segue, de forma geral, estas etapas:

1. importar as classes utilizadas pelo Método Simplex;
2. preservar os métodos originais quando necessário;
3. redefinir `_repr_latex_()` para produzir uma representação compatível com MathJax;
4. remover ou substituir alguns comandos LaTeX problemáticos;
5. adaptar a saída de `run_simplex_method()`;
6. utilizar `HtmlFragment` para controlar a apresentação dos resultados intermediários.

---

# Alterações realizadas no SageMath

## 1. Importação das classes

Inicialmente são importadas as classes responsáveis pelo Simplex Interativo:

 ```python
from sage.numerical.interactive_simplex_method import (
    InteractiveLPProblem,
    InteractiveLPProblemStandardForm,
    LPDictionary,
)

from IPython.display import Latex, display
from sage.misc.html import HtmlFragment
```

---

## 2. Adaptação de `_repr_latex_()`

A classe `InteractiveLPProblem` recebe uma nova implementação de `_repr_latex_()`:

```python
def _repr_latex_(self):
    tex = self._latex_()

    tex = tex.replace(r"\displaystyle", "")
    tex = tex.replace(r"\mspace{-6mu}", "")
    tex = tex.replace(r"\end{aligned}", r"\end{array}")

    return r"\[" + tex + r"\]"
 ```

Depois, o novo método é associado à classe:

 ```python
InteractiveLPProblem._repr_latex_ = _repr_latex_
 ```

Essa alteração faz com que a representação do problema seja entregue explicitamente como uma expressão matemática em modo *display*:

    \[
    ...
    \]

---

## 3. Adaptação da representação do dicionário Simplex

Os dicionários utilizados durante o algoritmo também precisam de uma representação adequada para o ambiente do notebook.

Uma implementação possível é:

```python
def _repr_latex_dictionary_(self):
    tex = self._latex_()

    tex = tex.replace(
        r"\renewcommand{\arraystretch}{1.5} %notruncate",
        ""
    )

    tex = tex.replace(r"\mspace{-6mu}", "")

    return r"\[" + tex + r"\]"
```

O método é então associado à classe:

```python
LPDictionary._repr_latex_ = _repr_latex_dictionary_
```

---

## 4. Adaptação do `run_simplex_method()`

Outra alteração importante está relacionada ao método responsável pela execução e apresentação das etapas do Simplex.

Primeiramente, o método original pode ser preservado:

```python
InteractiveLPProblemStandardForm.run_simplex_method_original = (
    InteractiveLPProblemStandardForm.run_simplex_method
)
```

A partir disso, pode ser criada uma implementação adaptada para controlar a saída:

```python
def run_simplex_method_problem_latex(self):

    output = []

    d = self.initial_dictionary()

    # processamento das etapas do Simplex
    # ...

    return HtmlFragment("\n".join(map(str, output)))
```

Finalmente:

```python
InteractiveLPProblemStandardForm.run_simplex_method = (
    run_simplex_method_problem_latex
)
```

Essa abordagem permite controlar como os dicionários e resultados intermediários são enviados para o ambiente de apresentação do CoCalc.

> A implementação completa dessas alterações está disponível no notebook deste repositório.

---

# Exemplo prático de modelagem

Para demonstrar a utilização do SageMath, considere o seguinte problema de Programação Linear.

Uma empresa produz dois produtos, denominados **Produto 1** e **Produto 2**.

O lucro obtido por unidade produzida é:

- Produto 1: 20 unidades monetárias;
- Produto 2: 10 unidades monetárias.

A produção está sujeita às seguintes restrições:

- a capacidade total disponível é de 90 unidades de recurso;
- cada unidade do Produto 1 consome 3 unidades do recurso;
- cada unidade do Produto 2 consome 2 unidades do recurso;
- a produção do Produto 1 está limitada a 25 unidades.

Definindo:

- $x_1$ = quantidade produzida do Produto 1;
- $x_2$ = quantidade produzida do Produto 2.

O problema pode ser formulado como:

$$
\max Z = 20x_1 + 10x_2
$$

sujeito a:

$$
\begin{cases}
3x_1 + 2x_2 \leq 90,\\
x_1 \leq 25,\\
x_1,x_2 \geq 0.
\end{cases}
$$

---

# Definição do modelo no SageMath

O problema pode ser representado no SageMath por meio da matriz das restrições, do vetor dos lados direitos e dos coeficientes da função objetivo.

```python
A = ([3, 2],
     [1, 0])

b = (90, 25)

c = (20, 10)
```

A matriz das restrições é:

$$
A =
\begin{pmatrix}
3 & 2\\
1 & 0
\end{pmatrix}
$$

O vetor dos lados direitos é:

$$
b =
\begin{pmatrix}
90\\
25
\end{pmatrix}
$$

e os coeficientes da função objetivo são:

$$
c =
\begin{pmatrix}
20\\
10
\end{pmatrix}.
$$

O problema pode então ser criado utilizando `InteractiveLPProblem`:

```python
P = InteractiveLPProblem(
    A,
    b,
    c,
    ["x_1", "x_2"],
    problem_type="max",
    constraint_type=["<=", "<="],
    variable_type=[">=", ">="]
)
```

A representação do objeto:

```python
P
```

deve produzir uma expressão matemática semelhante a:

$$
\begin{array}{l}
\max \quad 20x_1 + 10x_2\\
3x_1 + 2x_2 \leq 90\\
x_1 \leq 25\\
x_1,x_2 \geq 0
\end{array}
$$

O objetivo da adaptação proposta neste projeto é justamente garantir que essa representação seja renderizada corretamente no CoCalc.

---

# Resolução pelo Método Simplex

Depois de definido o problema, podemos solicitar ao SageMath a solução ótima:

```python
print("Solução Ótima:", P.optimal_solution())
print("Valor Ótimo:", P.optimal_value())
```

O resultado esperado é:

    Solução Ótima: (25, 15/2)
    Valor Ótimo: 575

Portanto:

$$ x_1^* = 25 $$

e:

$$ x_2^* = \frac{15}{2} = 7,5. $$

O valor ótimo da função objetivo é:

$$ Z^* = 20(25)+10\left(\frac{15}{2}\right) $$

$$ Z^* = 500+75=575. $$

Assim, a solução ótima é:

$$ \boxed{ (x_1,x_2) = \left(25,\frac{15}{2}\right)} $$

com:

$$ \boxed{Z_{\max}=575} $$

---

# Visualização gráfica

Além da solução algébrica, o SageMath permite visualizar graficamente a região factível.

```python
Fig = P.plot()
Fig
```

O gráfico permite identificar:

- a região factível;
- as restrições do problema;
- os eixos coordenados;
- o ponto correspondente à solução ótima.

A visualização gráfica é particularmente útil para fins didáticos, pois permite relacionar a interpretação geométrica da Programação Linear com o processo algorítmico do Método Simplex.

---

# Execução do Método Simplex

Para acompanhar as etapas do algoritmo, pode-se executar:

```python
P.run_simplex_method()
```

O método apresenta os dicionários Simplex e as operações realizadas durante o processo de otimização.

Com as alterações apresentadas neste projeto, essas etapas são adaptadas para que as expressões matemáticas sejam corretamente apresentadas pelo MathJax no CoCalc.

O objetivo é permitir que o estudante acompanhe não apenas o resultado final, mas também a evolução do problema durante o algoritmo Simplex.

---

# Execução no CoCalc

A maneira mais simples de reproduzir os resultados deste projeto é utilizar o notebook:

    Tutorial_Interactive-Simplex-Method.ipynb

disponível neste repositório.

O notebook contém:

- configuração da renderização LaTeX;
- adaptação das classes do Simplex;
- definição do problema de Programação Linear;
- cálculo da solução ótima;
- representação gráfica;
- execução do Método Simplex Interativo.

## Passo a passo

1. Abra o projeto no CoCalc.
2. Abra o arquivo `Tutorial_Interactive-Simplex-Method.ipynb`.
3. Certifique-se de que o kernel utilizado é o SageMath.
4. Execute inicialmente as células responsáveis pela adaptação da renderização.
5. Execute as células de definição do problema.
6. Visualize a representação LaTeX do modelo.
7. Execute `P.run_simplex_method()` para acompanhar as etapas do Simplex.

> Como as alterações são realizadas em tempo de execução, elas precisam ser executadas novamente quando uma nova sessão do SageMath for iniciada.

---

# Estrutura do repositório

    Tutorial-SageMath-CoCalc-Interactive-Simplex-Method/
    │
    ├── LICENSE
    ├── README.md
    └── Tutorial_Interactive-Simplex-Method.ipynb

O arquivo principal é:

    Tutorial_Interactive-Simplex-Method.ipynb

Ele contém a implementação da adaptação e o exemplo prático de Programação Linear.

---

# Alteração permanente no código-fonte do SageMath

A solução apresentada neste projeto é adequada para utilização no CoCalc porque não exige alterações permanentes na instalação do SageMath.

Entretanto, caso o objetivo seja incorporar a correção diretamente ao SageMath, o arquivo relevante é:

    src/sage/numerical/interactive_simplex_method.py

As principais classes envolvidas são:

```python
InteractiveLPProblem
InteractiveLPProblemStandardForm
LPDictionary
```

Em particular, devem ser analisados:

- `_latex_()`;
- `_repr_latex_()`;
- `run_simplex_method()`;
- o uso de `HtmlFragment`;
- a geração dos dicionários Simplex;
- os ambientes LaTeX utilizados nas representações.

A correção permanente deve procurar respeitar a arquitetura de representação do próprio SageMath, em vez de simplesmente reproduzir o *monkey patch* utilizado neste notebook.

---

# Proposta de correção

Uma possível estratégia para uma alteração permanente no SageMath é:

    interactive_simplex_method.py
            │
            ├── InteractiveLPProblem
            │       └── _repr_latex_()
            │
            ├── InteractiveLPProblemStandardForm
            │       └── run_simplex_method()
            │
            └── LPDictionary
                    └── _repr_latex_()

O objetivo é garantir que:

1. `_latex_()` continue sendo responsável por gerar a representação matemática;
2. `_repr_latex_()` forneça uma representação compatível com IPython/Jupyter;
3. comandos LaTeX não suportados pelo MathJax sejam evitados ou substituídos;
4. a saída de `run_simplex_method()` seja compatível com o mecanismo de renderização do notebook;
5. a solução funcione não apenas no CoCalc, mas também em outros ambientes Jupyter utilizados pelo SageMath.

---

# Por que utilizar `_repr_latex_()`?

O método `_latex_()` e o método `_repr_latex_()` possuem papéis diferentes.

De forma simplificada:

    _latex_()
        ↓
    Gera o código LaTeX do objeto

enquanto:

    _repr_latex_()
        ↓
    Define como essa representação será apresentada
    no ambiente IPython/Jupyter

Essa distinção é importante para o problema tratado neste projeto.

Uma representação LaTeX válida para um compilador LaTeX tradicional não necessariamente será processada da mesma forma pelo MathJax utilizado em um notebook.

Por isso, a correção proposta atua principalmente na camada de apresentação.

---


# Método Simplex das Duas Fases

Além do **Método Simplex Interativo**, este projeto também disponibiliza uma implementação do **Método Simplex das Duas Fases**, desenvolvida para trabalhar de forma integrada com as estruturas do `interactive_simplex_method` do SageMath.

A implementação está disponível no arquivo:

```text
simplex_duas_fases.py
```

e possui um exemplo completo no notebook:

```text
Exemplo_Simplex_Duas_Fases.ipynb
```

O objetivo desta implementação é permitir a resolução de problemas de Programação Linear que **não possuem uma base inicial evidente**, especialmente problemas que apresentam restrições do tipo `>=` ou `=` e, consequentemente, necessitam de **variáveis artificiais**.

---

## O que é o Método Simplex das Duas Fases?

O Método Simplex das Duas Fases é uma estratégia utilizada para encontrar uma solução básica viável inicial antes da aplicação do Simplex ao problema original.

O procedimento é dividido em duas etapas:

```text
Problema de Programação Linear
             │
             ▼
        Construção da
          Fase I
             │
             ▼
   Introdução de variáveis
        artificiais
             │
             ▼
       Resolver Fase I
             │
       ┌─────┴─────┐
       │           │
       ▼           ▼
    objetivo       objetivo
     ≠ 0             = 0
       │              │
       ▼              ▼
   Inviável       Problema
                   viável
                      │
                      ▼
             Remoção das variáveis
                artificiais
                      │
                      ▼
                Fase II
                      │
                      ▼
             Solução ótima
```

### Fase I

A primeira fase tem como objetivo determinar se o problema original possui uma solução viável.

Para isso, são introduzidas **variáveis artificiais** nas restrições que necessitam de uma base inicial.

O problema auxiliar da Fase I minimiza a soma das variáveis artificiais:

$$
\min W = a_1 + a_2 + \cdots + a_k
$$

onde:

- $a_1,\ldots,a_k$ são as variáveis artificiais;
- $W$ é a função objetivo auxiliar.

Ao final da Fase I:

$$
W^* \neq 0
$$

indica que o problema original é **inviável**.

Por outro lado:

$$
W^* = 0
$$

indica que foi encontrada uma solução básica viável para o problema original e que é possível prosseguir para a Fase II.

---

## Fase II

Na Fase II, as variáveis artificiais deixam de fazer parte do problema.

O dicionário obtido ao final da Fase I é utilizado para construir o dicionário inicial da Fase II, agora utilizando novamente a **função objetivo original**.

O Simplex é então executado normalmente até que uma solução ótima seja encontrada.

O fluxo implementado no projeto é:

```text
P
│
▼
construir_fase_1()
│
▼
construir_forma_padrao_fase_1()
│
▼
Fase I
│
├── objetivo ≠ 0 → problema inviável
│
└── objetivo = 0
        │
        ▼
expulsar_artificiais_basicas()
        │
        ▼
dicionario_fase_2()
        │
        ▼
Fase II
        │
        ▼
solução ótima
```

---

## Implementação no SageMath

A implementação utiliza as classes fornecidas pelo módulo:

```python
from sage.numerical.interactive_simplex_method import (
    InteractiveLPProblem,
    InteractiveLPProblemStandardForm,
    LPDictionary,
)
```

A classe principal criada neste projeto é:

```python
simplex_duas_fases
```

Ela recebe um problema de Programação Linear construído com `InteractiveLPProblem`.

Exemplo:

```python
S = simplex_duas_fases(P)
```

Depois, o processo completo pode ser executado com:

```python
resultado = S.resolver()
```

O método `resolver()` executa automaticamente a Fase I e, caso o problema seja viável, prossegue para a Fase II.

---

## Construção da Fase I

O método:

```python
construir_fase_1()
```

analisa as restrições do problema original.

São tratados os seguintes tipos:

```text
<=
>=
=
```

Para uma restrição do tipo `<=`, é adicionada uma variável de folga.

Por exemplo:

$$
3x_1 + 2x_2 \leq 90
$$

é transformada em:

$$
3x_1 + 2x_2 + R_1 = 90
$$

Para uma restrição do tipo `>=`, é introduzida uma variável de excesso e uma variável artificial:

$$
3x_1 + 2x_2 \geq 90
$$

torna-se:

$$
3x_1 + 2x_2 - R_1 + a_1 = 90
$$

Para uma igualdade:

$$
3x_1 + 2x_2 = 90
$$

é introduzida uma variável artificial:

$$
3x_1 + 2x_2 + a_1 = 90
$$

As variáveis artificiais são identificadas e armazenadas pela implementação para que possam ser removidas posteriormente.

---

## Função objetivo da Fase I

Depois da transformação das restrições, a implementação cria um problema auxiliar cujo objetivo é minimizar as variáveis artificiais:

$$
\min W = a_1+a_2+\cdots+a_k
$$

As demais variáveis recebem coeficiente zero na função objetivo da Fase I.

Dessa forma, o Simplex procura levar todas as variáveis artificiais para zero.

---

## Verificação da viabilidade

Após a execução do Simplex na Fase I, é analisado o valor da função objetivo auxiliar.

A implementação utiliza:

```python
self.valor_fase_I = self.D3.objective_value()
```

Se:

```python
self.valor_fase_I != 0
```

o problema original é considerado inviável:

```text
Problema original inviável.
```

Se:

```python
self.valor_fase_I == 0
```

o problema é considerado viável e a execução prossegue para a Fase II:

```text
Problema original viável. Siga para a Fase II.
```

---

## Expulsão das variáveis artificiais

Depois de uma Fase I bem-sucedida, as variáveis artificiais não podem permanecer na base para a resolução do problema original.

Para isso, a implementação utiliza:

```python
expulsar_artificiais_basicas()
```

O procedimento procura variáveis não artificiais capazes de entrar na base e realiza o pivotamento necessário.

Uma característica importante da implementação é que uma variável artificial **não é escolhida como variável entrante** durante esse processo.

O objetivo é obter uma base composta somente por variáveis relacionadas ao problema original.

---

## Construção do dicionário da Fase II

Depois da remoção das variáveis artificiais, o método:

```python
dicionario_fase_2()
```

constrói o dicionário inicial da Fase II.

Nesse processo:

1. as variáveis artificiais são identificadas;
2. as artificiais básicas são expulsas da base;
3. as variáveis artificiais são removidas das variáveis não básicas;
4. as colunas correspondentes às artificiais são removidas;
5. a função objetivo original é reconstruída;
6. o dicionário da Fase II é criado;
7. são realizadas verificações para garantir que nenhuma variável artificial permaneça.

O resultado é armazenado em:

```python
self.D4
```

---

## Execução do Simplex

A implementação utiliza o método:

```python
simplex_maior_coeficiente()
```

para realizar as iterações do Simplex.

A variável entrante é escolhida utilizando o critério do **maior coeficiente positivo na função objetivo**.

O procedimento geral é:

```text
1. Verificar se o dicionário é ótimo
2. Identificar as variáveis candidatas a entrar
3. Escolher o maior coeficiente positivo
4. Identificar a variável que sai
5. Realizar o pivotamento
6. Construir o novo dicionário
7. Repetir até encontrar a solução ótima
```

O método também possui um limite padrão de:

```python
max_iter=100
```

iterações, evitando uma execução indefinida em situações problemáticas.

---

## Exemplo de utilização

Considere um problema de Programação Linear definido no SageMath:

```python
A = (
    (1, 1),
    (2, 1)
)

b = (4, 5)

c = (3, 2)
```

O problema pode ser criado utilizando:

```python
P = InteractiveLPProblem(
    A,
    b,
    c,
    ["x_1", "x_2"],
    problem_type="max",
    constraint_type=["==", ">="],
    variable_type=[">=", ">="]
)
```

A classe das Duas Fases pode então ser instanciada:

```python
S = simplex_duas_fases(P)
```

e o problema pode ser resolvido com:

```python
resultado = S.resolver()
```

Ao executar o método, são realizadas as seguintes etapas:

```text
FASE I
   ↓
Construção do problema auxiliar
   ↓
Introdução das variáveis artificiais
   ↓
Simplex da Fase I
   ↓
Teste de viabilidade
   ↓
Remoção das artificiais
   ↓
Construção do dicionário da Fase II
   ↓
FASE II
   ↓
Simplex
   ↓
Solução ótima
```

---

## Acompanhamento das iterações

A implementação foi desenvolvida com finalidade principalmente didática.

Durante a execução são apresentados os dicionários Simplex e informações sobre as iterações, incluindo:

- dicionário inicial;
- variável que entra;
- variável que sai;
- novo dicionário;
- valor da função objetivo;
- resultado da Fase I;
- indicação de inviabilidade ou continuidade para a Fase II.

Isso permite acompanhar o funcionamento interno do algoritmo, e não apenas obter a solução numérica final.

---

## Arquivos relacionados ao Simplex das Duas Fases

Com a inclusão dessa funcionalidade, o repositório passa a conter os seguintes arquivos principais:

```text
Tutorial-SageMath-CoCalc-Interactive-Simplex-Method/
│
├── LICENSE
├── README.md
├── Tutorial_Interactive-Simplex-Method.ipynb
├── Exemplo_Simplex_Duas_Fases.ipynb
└── simplex_duas_fases.py
```

### `Tutorial_Interactive-Simplex-Method.ipynb`

Contém o tutorial relacionado ao **Método Simplex Interativo**, incluindo a adaptação da renderização LaTeX/MathJax no CoCalc.

### `simplex_duas_fases.py`

Contém a implementação do **Método Simplex das Duas Fases**, integrada às estruturas do `interactive_simplex_method`.

### `Exemplo_Simplex_Duas_Fases.ipynb`

Contém exemplos práticos de utilização da implementação das Duas Fases no SageMath.

---

## Relação com o Simplex Interativo

O projeto passa, portanto, a contemplar duas abordagens complementares:

| Funcionalidade | Descrição |
|---|---|
| **Simplex Interativo** | Utilização das classes nativas do SageMath e visualização dos dicionários |
| **Simplex das Duas Fases** | Construção automática de uma base viável utilizando variáveis artificiais |
| **Renderização LaTeX/MathJax** | Adaptação da apresentação matemática para CoCalc/Jupyter |
| **Visualização gráfica** | Representação geométrica de problemas de Programação Linear |
| **Acompanhamento das iterações** | Exibição dos dicionários e operações realizadas pelo Simplex |

A implementação das Duas Fases complementa o tutorial original ao permitir trabalhar com problemas em que a base inicial não pode ser obtida diretamente apenas pela introdução de variáveis de folga.

---

## Observação sobre a implementação

A implementação atual foi desenvolvida para integração com o **SageMath 10.9** e utiliza internamente as classes do módulo:

```python
sage.numerical.interactive_simplex_method
```

Ela possui finalidade principalmente **didática e educacional**, permitindo visualizar as etapas envolvidas na construção e resolução de um problema pelo Método Simplex das Duas Fases.

Para aplicações de otimização em produção, recomenda-se utilizar os solucionadores de Programação Linear disponibilizados pelo próprio SageMath.

---

## Resumo do fluxo completo

O projeto agora apresenta o seguinte fluxo conceitual:

```text
                 PROGRAMAÇÃO LINEAR
                         │
             ┌───────────┴───────────┐
             │                       │
             ▼                       ▼
      SIMPLEX INTERATIVO      SIMPLEX DUAS FASES
             │                       │
             │                       ▼
             │                    FASE I
             │                       │
             │               ┌───────┴───────┐
             │               │               │
             │               ▼               ▼
             │            W ≠ 0           W = 0
             │               │               │
             │               ▼               ▼
             │           INVIÁVEL         FASE II
             │                               │
             │                               ▼
             │                          SOLUÇÃO ÓTIMA
             │
             ▼
      DICIONÁRIOS SIMPLEX
             │
             ▼
       SOLUÇÃO ÓTIMA
```

Dessa forma, o repositório reúne tanto a utilização didática do **Simplex Interativo do SageMath** quanto uma implementação própria do **Simplex das Duas Fases**, mantendo o foco na visualização das etapas matemáticas e computacionais do algoritmo.

---

# Limitações

Esta implementação deve ser entendida como uma **adaptação para o ambiente CoCalc/Jupyter**, e não necessariamente como uma correção definitiva incorporada ao SageMath.

As principais finalidades são:

- recuperar a visualização matemática;
- evitar comandos LaTeX incompatíveis com o renderizador;
- preservar o funcionamento do algoritmo Simplex;
- facilitar o uso didático do SageMath;
- documentar uma possível correção no código-fonte.

O MathJax implementa grande parte da linguagem LaTeX, mas não todo o conjunto de comandos disponíveis em um compilador LaTeX completo. Portanto, determinadas expressões geradas pelo SageMath podem precisar de adaptações quando apresentadas diretamente no navegador.

---

# Referências

- [SageMath — LaTeX e companheiros](https://doc.sagemath.org/html/pt/tutorial/latex.html)
- [SageMath — LaTeX Printing](https://doc.sagemath.org/html/en/reference/misc/sage/misc/latex.html)
- [SageMath — Developer Guide](https://doc.sagemath.org/html/en/developer/)
- [SageMath — Código-fonte](https://github.com/sagemath/sage)
- [CoCalc](https://cocalc.com/)
- [Repositório deste projeto](https://github.com/brenoassis32/Tutorial-SageMath-CoCalc-Interactive-Simplex-Method)

---

# Licença

Este projeto está distribuído sob a licença **MIT**.

Consulte o arquivo [`LICENSE`](LICENSE) para obter os termos completos da licença.
