"""
Gera a base de dados fictícia da academia FitPlus.

- alunos.csv        -> 2000 alunos com a resposta (Cancelou = 0/1), usados no treino
- alunos_novos.csv  -> 500 alunos sem a resposta, usados na previsão
- gabarito_novos.csv-> a resposta verdadeira dos 500 novos (para conferir o acerto)
- ../sql/01_criar_banco.sql -> script que cria o banco AcademiaML com tudo dentro

Os dados são aleatórios, mas seguem regras simples (ex.: quem vai pouco à
academia e tem plano mensal cancela mais), para o modelo ter o que aprender.

Uso: python gerar_dados.py
"""
import csv
import math
import random
import unicodedata
from pathlib import Path

random.seed(2025)

AQUI = Path(__file__).resolve().parent
SQL = AQUI.parent / "sql" / "01_criar_banco.sql"

NOMES_M = ["Lucas", "Gabriel", "Pedro", "Rafael", "Mateus", "Gustavo", "Felipe", "Bruno",
           "Thiago", "Diego", "Rodrigo", "André", "João", "Vitor", "Leonardo", "Eduardo",
           "Marcelo", "Carlos", "Daniel", "Fernando"]
NOMES_F = ["Ana", "Beatriz", "Camila", "Juliana", "Larissa", "Mariana", "Fernanda", "Amanda",
           "Bruna", "Carolina", "Letícia", "Patrícia", "Gabriela", "Isabela", "Natália",
           "Renata", "Aline", "Vanessa", "Débora", "Priscila"]
SOBRENOMES = ["Silva", "Santos", "Oliveira", "Souza", "Rodrigues", "Ferreira", "Alves",
              "Pereira", "Lima", "Gomes", "Costa", "Ribeiro", "Martins", "Carvalho",
              "Almeida", "Lopes", "Soares", "Fernandes", "Vieira", "Barbosa"]
CIDADES = ["Porto Alegre", "Canoas", "Gravataí", "Novo Hamburgo", "Viamão"]
PLANOS = {"Mensal": 129.90, "Trimestral": 109.90, "Anual": 89.90}

CAMPOS = ["AlunoID", "Nome", "Email", "Sexo", "Idade", "Cidade", "Plano", "ValorMensal",
          "MesesMatriculado", "FrequenciaSemanal", "DistanciaKm", "PersonalTrainer",
          "AulasColetivas", "AtrasosPagamento", "Avaliacao", "Cancelou"]


def sem_acento(txt):
    return "".join(c for c in unicodedata.normalize("NFD", txt) if unicodedata.category(c) != "Mn")


def novo_aluno(aluno_id):
    sexo = random.choice(["M", "F"])
    nome = random.choice(NOMES_M if sexo == "M" else NOMES_F)
    sobrenome = random.choice(SOBRENOMES)
    email = f"{sem_acento(nome).lower()}.{sem_acento(sobrenome).lower()}{aluno_id}@exemplo.com"

    idade = max(16, min(70, int(random.gauss(32, 10))))
    plano = random.choices(list(PLANOS), weights=[50, 25, 25])[0]
    meses = random.randint(1, 36)
    freq = round(max(0.0, min(6.0, random.gauss(2.8, 1.3))), 1)
    dist = round(random.uniform(0.5, 15.0), 1)
    personal = random.choices(["Sim", "Não"], weights=[20, 80])[0]
    coletivas = random.choices(["Sim", "Não"], weights=[40, 60])[0]
    atrasos = random.choices([0, 1, 2, 3, 4], weights=[55, 20, 12, 8, 5])[0]
    avaliacao = random.choices([1, 2, 3, 4, 5], weights=[6, 12, 27, 35, 20])[0]

    # Regra "escondida" que define a chance de cancelar
    z = 1.6 * (-1.15
               + (1.1 if plano == "Mensal" else 0.0)
               - (0.9 if plano == "Anual" else 0.0)
               - 0.8 * (freq - 2.8)
               + 0.09 * (dist - 7.5)
               + 0.55 * atrasos
               - 0.55 * (avaliacao - 3.5)
               - (0.8 if personal == "Sim" else 0.0)
               - (0.4 if coletivas == "Sim" else 0.0)
               - 0.03 * (meses - 18))
    cancelou = 1 if random.random() < 1 / (1 + math.exp(-z)) else 0

    return {
        "AlunoID": aluno_id, "Nome": f"{nome} {sobrenome}", "Email": email, "Sexo": sexo,
        "Idade": idade, "Cidade": random.choice(CIDADES), "Plano": plano,
        "ValorMensal": f"{PLANOS[plano]:.2f}", "MesesMatriculado": meses,
        "FrequenciaSemanal": freq, "DistanciaKm": dist, "PersonalTrainer": personal,
        "AulasColetivas": coletivas, "AtrasosPagamento": atrasos, "Avaliacao": avaliacao,
        "Cancelou": cancelou,
    }


def salvar_csv(nome, linhas, campos):
    with open(AQUI / nome, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=campos, delimiter=";")
        w.writeheader()
        for l in linhas:
            w.writerow({c: l[c] for c in campos})


def valor_sql(campo, v):
    if campo in ("Nome", "Email", "Sexo", "Cidade", "Plano", "PersonalTrainer", "AulasColetivas"):
        return "N'" + str(v).replace("'", "''") + "'"
    return str(v)


def inserts(tabela, linhas, campos):
    blocos = []
    for i in range(0, len(linhas), 500):
        parte = linhas[i:i + 500]
        valores = ",\n".join("(" + ", ".join(valor_sql(c, l[c]) for c in campos) + ")" for l in parte)
        blocos.append(f"INSERT INTO dbo.{tabela} ({', '.join(campos)}) VALUES\n{valores};\nGO\n")
    return "\n".join(blocos)


def main():
    alunos = [novo_aluno(i) for i in range(1, 2001)]
    novos = [novo_aluno(i) for i in range(5001, 5501)]
    campos_novos = [c for c in CAMPOS if c != "Cancelou"]

    salvar_csv("alunos.csv", alunos, CAMPOS)
    salvar_csv("alunos_novos.csv", novos, campos_novos)
    salvar_csv("gabarito_novos.csv", novos, ["AlunoID", "Cancelou"])

    colunas = """    AlunoID           INT           NOT NULL PRIMARY KEY,
    Nome              NVARCHAR(60)  NOT NULL,
    Email             NVARCHAR(80)  NOT NULL,
    Sexo              NCHAR(1)      NOT NULL,
    Idade             INT           NOT NULL,
    Cidade            NVARCHAR(40)  NOT NULL,
    Plano             NVARCHAR(20)  NOT NULL,
    ValorMensal       DECIMAL(6,2)  NOT NULL,
    MesesMatriculado  INT           NOT NULL,
    FrequenciaSemanal DECIMAL(3,1)  NOT NULL,
    DistanciaKm       DECIMAL(4,1)  NOT NULL,
    PersonalTrainer   NVARCHAR(3)   NOT NULL,
    AulasColetivas    NVARCHAR(3)   NOT NULL,
    AtrasosPagamento  INT           NOT NULL,
    Avaliacao         INT           NOT NULL"""

    sql = f"""/* =====================================================================
   Trabalho de Machine Learning - Academia FitPlus
   Script 01: cria o banco AcademiaML e carrega os dados fictícios.
   Rode inteiro no Azure Data Studio (ou SSMS) conectado em localhost.
   Gerado por dados/gerar_dados.py
   ===================================================================== */

IF DB_ID('AcademiaML') IS NOT NULL
BEGIN
    ALTER DATABASE AcademiaML SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE AcademiaML;
END
GO

CREATE DATABASE AcademiaML;
GO

USE AcademiaML;
GO

-- Alunos com a resposta conhecida (base de TREINO, como a vTargetMail da aula)
CREATE TABLE dbo.Alunos (
{colunas},
    Cancelou          INT           NOT NULL   -- 1 = cancelou, 0 = continua
);
GO

-- Alunos novos, sem a resposta (base de PREVISÃO, como a ProspectiveBuyer da aula)
CREATE TABLE dbo.AlunosNovos (
{colunas}
);
GO

-- Resposta verdadeira dos alunos novos, usada só para conferir o acerto do modelo
CREATE TABLE dbo.GabaritoNovos (
    AlunoID  INT NOT NULL PRIMARY KEY,
    Cancelou INT NOT NULL
);
GO

{inserts("Alunos", alunos, CAMPOS)}
{inserts("AlunosNovos", novos, campos_novos)}
{inserts("GabaritoNovos", novos, ["AlunoID", "Cancelou"])}
-- Permissão para o Analysis Services ler e gravar neste banco.
-- Assim, no Visual Studio, a opção "Usar a conta de serviço" funciona.
-- Se o Analysis Services ainda não estiver instalado, aparece só um aviso.
BEGIN TRY
    IF NOT EXISTS (SELECT 1 FROM sys.server_principals WHERE name = N'NT Service\\MSSQLServerOLAPService')
        EXEC (N'CREATE LOGIN [NT Service\\MSSQLServerOLAPService] FROM WINDOWS;');
    IF NOT EXISTS (SELECT 1 FROM sys.database_principals WHERE name = N'NT Service\\MSSQLServerOLAPService')
        EXEC (N'CREATE USER [NT Service\\MSSQLServerOLAPService] FOR LOGIN [NT Service\\MSSQLServerOLAPService];');
    EXEC (N'ALTER ROLE db_owner ADD MEMBER [NT Service\\MSSQLServerOLAPService];');
    PRINT 'Permissão do Analysis Services concedida.';
END TRY
BEGIN CATCH
    PRINT 'AVISO: não foi possível dar permissão ao Analysis Services: ' + ERROR_MESSAGE();
END CATCH
GO

-- Conferência: deve mostrar 2000, 500 e 500
SELECT 'Alunos' AS tabela, COUNT(*) AS linhas FROM dbo.Alunos
UNION ALL SELECT 'AlunosNovos', COUNT(*) FROM dbo.AlunosNovos
UNION ALL SELECT 'GabaritoNovos', COUNT(*) FROM dbo.GabaritoNovos;
GO
"""
    SQL.parent.mkdir(parents=True, exist_ok=True)
    SQL.write_text(sql, encoding="utf-8-sig")

    taxa = sum(a["Cancelou"] for a in alunos) / len(alunos)
    print(f"alunos: {len(alunos)}  novos: {len(novos)}  taxa de cancelamento no treino: {taxa:.1%}")


if __name__ == "__main__":
    main()
