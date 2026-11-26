/* =====================================================================
   Script 02: exploração dos dados ANTES do machine learning.
   Rode no Azure Data Studio, banco AcademiaML. Tire print dos resultados.
   ===================================================================== */
USE AcademiaML;
GO

-- 1) Visão geral: quantos alunos e quantos cancelaram
SELECT COUNT(*)                               AS total_alunos,
       SUM(Cancelou)                          AS cancelaram,
       CAST(AVG(Cancelou * 100.0) AS DECIMAL(5,1)) AS taxa_cancelamento_pct
FROM dbo.Alunos;

-- 2) Cancelamento por tipo de plano
SELECT Plano,
       COUNT(*)                               AS alunos,
       CAST(AVG(Cancelou * 100.0) AS DECIMAL(5,1)) AS taxa_cancelamento_pct
FROM dbo.Alunos
GROUP BY Plano
ORDER BY taxa_cancelamento_pct DESC;

-- 3) Cancelamento por frequência semanal (faixas)
SELECT CASE WHEN FrequenciaSemanal < 1.5 THEN '1) Menos de 1,5x'
            WHEN FrequenciaSemanal < 3   THEN '2) 1,5x a 3x'
            WHEN FrequenciaSemanal < 4.5 THEN '3) 3x a 4,5x'
            ELSE '4) 4,5x ou mais' END       AS faixa_frequencia,
       COUNT(*)                               AS alunos,
       CAST(AVG(Cancelou * 100.0) AS DECIMAL(5,1)) AS taxa_cancelamento_pct
FROM dbo.Alunos
GROUP BY CASE WHEN FrequenciaSemanal < 1.5 THEN '1) Menos de 1,5x'
              WHEN FrequenciaSemanal < 3   THEN '2) 1,5x a 3x'
              WHEN FrequenciaSemanal < 4.5 THEN '3) 3x a 4,5x'
              ELSE '4) 4,5x ou mais' END
ORDER BY faixa_frequencia;

-- 4) Cancelamento por atrasos de pagamento
SELECT AtrasosPagamento,
       COUNT(*)                               AS alunos,
       CAST(AVG(Cancelou * 100.0) AS DECIMAL(5,1)) AS taxa_cancelamento_pct
FROM dbo.Alunos
GROUP BY AtrasosPagamento
ORDER BY AtrasosPagamento;

-- 5) Cancelamento por avaliação (nota de 1 a 5 dada pelo aluno)
SELECT Avaliacao,
       COUNT(*)                               AS alunos,
       CAST(AVG(Cancelou * 100.0) AS DECIMAL(5,1)) AS taxa_cancelamento_pct
FROM dbo.Alunos
GROUP BY Avaliacao
ORDER BY Avaliacao;

-- 6) Personal trainer faz diferença?
SELECT PersonalTrainer,
       COUNT(*)                               AS alunos,
       CAST(AVG(Cancelou * 100.0) AS DECIMAL(5,1)) AS taxa_cancelamento_pct
FROM dbo.Alunos
GROUP BY PersonalTrainer;
