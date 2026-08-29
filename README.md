# Tutorial SageMath + CoCalc — Método Simplex Interativo e Renderização LaTeX

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
