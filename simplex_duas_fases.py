from sage.numerical.interactive_simplex_method import (
    InteractiveLPProblem,
    InteractiveLPProblemStandardForm,
    LPDictionary,
)


class simplex_duas_fases:
    """
    Método Simplex das Duas Fases para SageMath 10.9.

    Fluxo:

        P
        |
        v
    construir_fase_1()
        |
        v
    construir_forma_padrao_fase_1()
        |
        v
    Fase I
        |
        +---- objetivo != 0 ----> inviável
        |
        v
    expulsar_artificiais_basicas()
        |
        v
    dicionario_fase_2()
        |
        v
    Fase II
        |
        v
    solução ótima
    """

    def __init__(self, P):

        self.P = P

        self.P2 = None
        self.P3 = None

        self.D3 = None
        self.D4 = None

        self.artificiais = ()

        self.valor_fase_I = None
        self.viavel = None

        self.fase = None
        self.resultado = None

    # =========================================================
    # CONSTRUIR FASE I
    # =========================================================

    def construir_fase_1(self):

        P = self.P

        A = P.A()
        b = P.b()
        c = P.c()

        constraint_types = list(
            P.constraint_types()
        )

        variable_types = list(
            P.variable_types()
        )

        variaveis = list(
            P.decision_variables()
        )

        m = P.n_constraints()
        n = P.n_variables()

        nomes = [
            str(v)
            for v in variaveis
        ]

        if len(nomes) != n:

            nomes = [
                f"x_{i+1}"
                for i in range(n)
            ]

        A2 = [
            list(linha)
            for linha in A
        ]

        nomes2 = list(nomes)

        artificiais = []

        contador_R = 1
        contador_artificial = 1

        # =====================================================
        # Processa restrições
        # =====================================================

        for i in range(m):

            tipo = str(
                constraint_types[i]
            )

            # -------------------------------------------------
            # <=
            # -------------------------------------------------

            if tipo == "<=":

                nome_R = (
                    f"R_{contador_R}"
                )

                contador_R += 1

                nomes2.append(
                    nome_R
                )

                for linha in A2:
                    linha.append(0)

                A2[i][-1] = 1

            # -------------------------------------------------
            # >=
            # -------------------------------------------------

            elif tipo == ">=":

                nome_R = (
                    f"R_{contador_R}"
                )

                contador_R += 1

                nomes2.append(
                    nome_R
                )

                for linha in A2:
                    linha.append(0)

                A2[i][-1] = -1

                nome_artificial = (
                    f"a_{contador_artificial}"
                )

                contador_artificial += 1

                nomes2.append(
                    nome_artificial
                )

                artificiais.append(
                    nome_artificial
                )

                for linha in A2:
                    linha.append(0)

                A2[i][-1] = 1

            # -------------------------------------------------
            # =
            # -------------------------------------------------

            elif tipo in ("==", "="):

                nome_artificial = (
                    f"a_{contador_artificial}"
                )

                contador_artificial += 1

                nomes2.append(
                    nome_artificial
                )

                artificiais.append(
                    nome_artificial
                )

                for linha in A2:
                    linha.append(0)

                A2[i][-1] = 1

            else:

                raise ValueError(
                    f"Tipo de restrição inválido na "
                    f"restrição {i+1}: {tipo}"
                )

        # =====================================================
        # Objetivo da Fase I
        # =====================================================

        c2 = []

        for nome in nomes2:

            if nome in artificiais:
                c2.append(1)
            else:
                c2.append(0)

        # =====================================================
        # Todas as restrições são igualdades
        # =====================================================

        constraint_types2 = [
            "=="
            for _ in range(m)
        ]

        # =====================================================
        # Tipos das variáveis
        # =====================================================

        variable_types2 = list(
            variable_types
        )

        while len(variable_types2) < len(nomes2):

            variable_types2.append(
                ">="
            )

        # =====================================================
        # Cria P2
        # =====================================================

        self.P2 = InteractiveLPProblem(
            tuple(
                tuple(linha)
                for linha in A2
            ),
            tuple(b),
            tuple(c2),
            nomes2,
            problem_type="min",
            constraint_type=constraint_types2,
            variable_type=variable_types2
        )

        self.artificiais = tuple(
            artificiais
        )

        return (
            self.P2,
            self.artificiais
        )

    # =========================================================
    # CONSTRUIR FORMA PADRÃO DA FASE I
    # =========================================================

    def construir_forma_padrao_fase_1(self):

        P2 = self.P2
        artificiais = self.artificiais

        A2 = [
            list(linha)
            for linha in P2.A()
        ]

        b2 = tuple(
            P2.b()
        )

        nomes = [
            str(v)
            for v in P2.decision_variables()
        ]

        m = P2.n_constraints()

        variaveis_basicas = []
        indices_basicos = []

        # =====================================================
        # Identificar base inicial
        # =====================================================

        for j, nome in enumerate(nomes):

            coluna = [
                A2[i][j]
                for i in range(m)
            ]

            for linha_pivo in range(m):

                esperado = [
                    1 if i == linha_pivo else 0
                    for i in range(m)
                ]

                if coluna == esperado:

                    if j not in indices_basicos:

                        indices_basicos.append(
                            j
                        )

                        variaveis_basicas.append(
                            nome
                        )

                    break

        if len(indices_basicos) != m:

            raise ValueError(
                "Não foi possível identificar uma base "
                "completa para a Fase I."
            )

        # =====================================================
        # Não-básicas
        # =====================================================

        indices_nao_basicos = [
            j
            for j in range(len(nomes))
            if j not in indices_basicos
        ]

        variaveis_nao_basicas = [
            nomes[j]
            for j in indices_nao_basicos
        ]

        # =====================================================
        # Matriz
        # =====================================================

        A3 = []

        for i in range(m):

            A3.append([
                A2[i][j]
                for j in indices_nao_basicos
            ])

        # =====================================================
        # Objetivo da Fase I
        # =====================================================

        c3 = [
            0
            for _ in variaveis_nao_basicas
        ]

        objective_constant_term = 0

        indices_artificiais = [
            j
            for j in indices_basicos
            if nomes[j] in artificiais
        ]

        for indice_basico in indices_artificiais:

            coluna = [
                A2[i][indice_basico]
                for i in range(m)
            ]

            linha_base = coluna.index(1)

            objective_constant_term -= (
                b2[linha_base]
            )

            for j, indice_nb in enumerate(
                indices_nao_basicos
            ):

                c3[j] += (
                    A2[linha_base][indice_nb]
                )

        # =====================================================
        # P3
        # =====================================================

        self.P3 = InteractiveLPProblemStandardForm(
            tuple(
                tuple(linha)
                for linha in A3
            ),
            tuple(b2),
            tuple(c3),
            variaveis_nao_basicas,
            slack_variables=variaveis_basicas,
            objective_constant_term=(
                objective_constant_term
            )
        )

        return self.P3

    # =========================================================
    # IDENTIFICAR ARTIFICIAIS
    # =========================================================

    def identificar_artificiais(self, N=None):

        if N is None:

            return tuple(
                self.artificiais
            )

        return tuple(
            x
            for x in N
            if str(x).startswith("a_")
        )

    # =========================================================
    # ARTIFICIAIS BÁSICAS
    # =========================================================

    def artificiais_basicas( self, D=None, artificiais=None):

        if D is None:
            D = self.D3

        if artificiais is None:
            artificiais = self.artificiais

        artificiais = tuple(
            str(a)
            for a in artificiais
        )

        B = tuple(
            D.basic_variables()
        )

        return tuple(
            a
            for a in B
            if str(a) in artificiais
        )

    # =========================================================
    # EXPULSAR ARTIFICIAIS BÁSICAS
    # =========================================================

    def expulsar_artificiais_basicas(self, D=None, artificiais=None):
        """
        Expulsa da base as variáveis artificiais.

        Uma variável artificial NUNCA pode ser escolhida
        como variável entrante.

        O dicionário original D não é alterado.
        """

        if D is None:
            D = self.D3

        if artificiais is None:
            artificiais = self.artificiais

        artificiais = tuple(
            str(a)
            for a in artificiais
        )

        # =====================================================
        # Copiar D
        # =====================================================

        A, b, c, v, B, N, z = (
            D._AbcvBNz
        )

        D_atual = LPDictionary(
            A,
            b,
            c,
            v,
            tuple(B),
            tuple(N),
            z
        )

        # =====================================================
        # Expulsar artificiais
        # =====================================================

        while True:

            B_atual = tuple(
                D_atual.basic_variables()
            )

            N_atual = tuple(
                D_atual.nonbasic_variables()
            )

            # =================================================
            # Usar método da própria classe
            # =================================================

            artificiais_na_base = (
                self.artificiais_basicas(
                    D_atual,
                    artificiais
                )
            )

            # -------------------------------------------------
            # Nenhuma artificial na base
            # -------------------------------------------------

            if not artificiais_na_base:
                break

            # -------------------------------------------------
            # Escolher artificial
            # -------------------------------------------------

            a = artificiais_na_base[0]

            i = B_atual.index(a)

            A_atual = (
                D_atual._AbcvBNz[0]
            )

            linha = A_atual.row(i)

            # -------------------------------------------------
            # Procurar variável NÃO-ARTIFICIAL para entrar
            # -------------------------------------------------

            candidatos = [
                x
                for j, x in enumerate(N_atual)
                if str(x) not in artificiais
                and linha[j] != 0
            ]

            # -------------------------------------------------
            # Não existe variável para expulsar artificial
            # -------------------------------------------------

            if not candidatos:

                raise ValueError(
                    f"A variável artificial {a} permanece básica "
                    "com valor zero, mas não existe variável "
                    "não-artificial capaz de entrar na base. "
                    "A restrição correspondente é redundante."
                )

            # -------------------------------------------------
            # Escolher variável entrante
            # -------------------------------------------------

            x_entrante = candidatos[0]

            print(
                f"\nExpulsando {a}: "
                f"entra {x_entrante}, "
                f"sai {a}"
            )

            # -------------------------------------------------
            # Pivot
            # -------------------------------------------------

            D_atual.enter(
                x_entrante
            )

            D_atual.leave(
                a
            )

            D_atual.update()

            # -------------------------------------------------
            # Mostrar dicionário produzido
            # -------------------------------------------------

            show(
                D_atual
            )

        return D_atual

    # =========================================================
    # DICIONÁRIO FASE II
    # =========================================================

    def dicionario_fase_2(self, P, D3, artificiais=None):
        """
        Constrói o dicionário inicial da Fase II a partir do
        dicionário final da Fase I.

        As variáveis artificiais:

            1. são expulsas da base;
            2. nunca podem entrar na base durante essa operação;
            3. são removidas das não-básicas;
            4. não podem aparecer em D4.
        """

        # =====================================================
        # 1. Identificar artificiais
        # =====================================================

        if artificiais is None:

            A0, b0, c10, v10, B0, N0, z0 = (
                D3._AbcvBNz
            )

            B0 = tuple(B0)
            N0 = tuple(N0)

            artificiais = (
                self.identificar_artificiais(
                    B0 + N0
                )
            )

        else:

            artificiais = tuple(
                artificiais
            )

        artificiais = tuple(
            str(a)
            for a in artificiais
        )

        if not artificiais:

            raise ValueError(
                "Nenhuma variável artificial foi encontrada."
            )

        # =====================================================
        # 2. Expulsar artificiais básicas
        #
        # Usa o método já existente na classe.
        # =====================================================

        D_atual = (
            self.expulsar_artificiais_basicas(
                D3,
                artificiais
            )
        )

        # =====================================================
        # 3. Extrair dicionário após expulsão
        # =====================================================

        A, b, c1, v1, B, N, z1 = (
            D_atual._AbcvBNz
        )

        B = tuple(B)
        N = tuple(N)

        # =====================================================
        # 4. Verificação:
        #    nenhuma artificial pode estar na base
        # =====================================================

        artificiais_na_base = tuple(
            x
            for x in B
            if str(x) in artificiais
        )

        if artificiais_na_base:

            raise RuntimeError(
                "Ainda existem variáveis artificiais "
                "na base após a expulsão: "
                + str(artificiais_na_base)
            )

        # =====================================================
        # 5. Remover artificiais das não-básicas
        # =====================================================

        N2 = tuple(
            x
            for x in N
            if str(x) not in artificiais
        )

        # =====================================================
        # 6. Colunas que permanecem
        # =====================================================

        colunas_manter = [
            j
            for j, x in enumerate(N)
            if str(x) not in artificiais
        ]

        A2 = A.matrix_from_columns(
            colunas_manter
        )

        B2 = B

        b2 = vector(
            D_atual.base_ring(),
            b
        )

        # =====================================================
        # 7. Verificação final antes de construir D4
        # =====================================================

        artificiais_restantes = tuple(
            x
            for x in B2 + N2
            if str(x) in artificiais
        )

        if artificiais_restantes:

            raise RuntimeError(
                "ERRO: variáveis artificiais ainda "
                "estão presentes antes da construção "
                "de D4: "
                + str(artificiais_restantes)
            )

        # =====================================================
        # 8. Problema original
        # =====================================================

        A_original, b_original, c_original, x_original = (
            P.Abcx()
        )

        # =====================================================
        # 9. Reconstruir objetivo original
        # =====================================================

        c2 = vector(
            D_atual.base_ring(),
            [0] * len(N2)
        )

        v2 = D_atual.base_ring()(
            P._constant_term
        )

        for cj, xj in zip(
            c_original,
            x_original
        ):

            # -------------------------------------------------
            # Variável original não-básica
            # -------------------------------------------------

            if xj in N2:

                j = N2.index(xj)

                c2[j] += cj

            # -------------------------------------------------
            # Variável original básica
            # -------------------------------------------------

            elif xj in B2:

                i = B2.index(xj)

                v2 += (
                    cj * b2[i]
                )

                c2 -= (
                    cj * A2.row(i)
                )

            # -------------------------------------------------
            # Variável não encontrada
            # -------------------------------------------------

            else:

                raise ValueError(
                    f"A variável original {xj} não pertence "
                    "ao dicionário da Fase I após a eliminação "
                    "das artificiais."
                )

        # =====================================================
        # 10. MIN -> MAX
        # =====================================================

        if P.problem_type() == "min":

            c2 = -c2
            v2 = -v2

        # =====================================================
        # 11. Criar D4
        # =====================================================

        D4 = LPDictionary(
            A2,
            b2,
            c2,
            v2,
            B2,
            N2,
            z1
        )

        # =====================================================
        # 12. Verificação definitiva
        #
        # D4 NÃO PODE conter artificiais.
        # =====================================================

        B4 = tuple(
            D4.basic_variables()
        )

        N4 = tuple(
            D4.nonbasic_variables()
        )

        artificiais_restantes = tuple(
            x
            for x in B4 + N4
            if str(x) in artificiais
        )

        if artificiais_restantes:

            raise RuntimeError(
                "ERRO: artificiais ainda presentes em D4: "
                + str(artificiais_restantes)
            )

        print(
            "\nDicionário inicial da Fase II:"
        )

        # show(D4)

        return D4

    # =========================================================
    # VERIFICAR FASE I
    # =========================================================

    def verifica_fase_I(self):

        resultado = (
            self.P3.run_simplex_method()
        )

        display(
            resultado
        )

        self.D3 = (
            self.P3._final_dictionary
        )

        print(
            "\nDicionário final da Fase I:"
        )

        show(
            self.D3
        )

        self.valor_fase_I = (
            self.D3.objective_value()
        )

        print(
            "\nValor da função objetivo da Fase I:"
        )

        show(
            self.valor_fase_I
        )

        if self.valor_fase_I != 0:

            self.viavel = False

            print(
                "\nProblema original inviável."
            )

            return False

        self.viavel = True

        print(
            "\nProblema original viável. "
            "Siga para a Fase II."
        )

        return True

    # =========================================================
    # RESOLVER
    # =========================================================

    def resolver(self):

        # =====================================================
        # FASE I
        # =====================================================

        self.fase = 1

        print("=" * 60)
        print("FASE I")
        print("=" * 60)

        # -----------------------------------------------------
        # Construir Fase I
        # -----------------------------------------------------

        self.construir_fase_1()

        print(
            "\nProblema da Fase I (P2):"
        )

        display(self.P2)

        # -----------------------------------------------------
        # Construir forma padrão da Fase I
        # -----------------------------------------------------

        self.construir_forma_padrao_fase_1()

        # -----------------------------------------------------
        # Resolver Fase I
        # -----------------------------------------------------

        resultado_fase_I = (
            self.P3.run_simplex_method()
        )

        # -----------------------------------------------------
        # Mostrar dicionários da Fase I
        # -----------------------------------------------------

        display(
            resultado_fase_I
        )

        # -----------------------------------------------------
        # Recuperar D3
        # -----------------------------------------------------

        self.D3 = (
            self.P3._final_dictionary
        )

        self.valor_fase_I = (
            self.D3.objective_value()
        )

        # =====================================================
        # VERIFICAR VIABILIDADE
        # =====================================================

        if self.valor_fase_I != 0:

            self.viavel = False
            self.resultado = None

            print(
                "\nProblema original inviável."
            )

            return None

        # =====================================================
        # PROBLEMA VIÁVEL
        # =====================================================

        self.viavel = True

        print(
            "\nProblema original viável. "
            "Siga para a Fase II."
        )

        # =====================================================
        # FASE II
        # =====================================================

        self.fase = 2

        print()
        print("=" * 60)
        print("FASE II")
        print("=" * 60)

        # -----------------------------------------------------
        # Construir D4
        # -----------------------------------------------------

        self.D4 = (
            self.dicionario_fase_2(
                self.P,
                self.D3,
                self.artificiais
            )
        )

        # -----------------------------------------------------
        # Resolver Fase II
        # -----------------------------------------------------

        resultado_fase_II = (
            self.D4.run_simplex_method()
        )

        # -----------------------------------------------------
        # Mostrar dicionários da Fase II
        # -----------------------------------------------------

        display(
            resultado_fase_II
        )

        # -----------------------------------------------------
        # Recuperar dicionário final
        # -----------------------------------------------------

        if hasattr(
            self.D4,
            "_final_dictionary"
        ):

            self.D4 = (
                self.D4._final_dictionary
            )

        # =====================================================
        # RESULTADO
        # =====================================================

        self.resultado = self.D4

        return self.D4
