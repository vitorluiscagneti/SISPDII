/* =====================================================================
   Script 04: análise do resultado do machine learning + views do Power BI.
   Rode DEPOIS de salvar a previsão do Visual Studio na tabela
   dbo.PrevisaoCancelamento (colunas: AlunoID, Nome, Email, Plano,
   Previsao, Probabilidade).
   ===================================================================== */
USE AcademiaML;
GO

-- 1) Alunos com maior risco de cancelar (na aula o corte foi > 0.75; aqui a maior
--    probabilidade da árvore é 0,748, então o corte usado é >= 0.70 = faixa "Alto")
SELECT AlunoID, Nome, Email, Plano, Probabilidade
FROM dbo.PrevisaoCancelamento
WHERE Probabilidade >= 0.70
ORDER BY Probabilidade DESC;

-- 2) Acerto do modelo: compara a previsão com a resposta verdadeira (GabaritoNovos)
SELECT COUNT(*)                                                         AS alunos_avaliados,
       SUM(CASE WHEN p.Previsao = g.Cancelou THEN 1 ELSE 0 END)         AS acertos,
       CAST(AVG(CASE WHEN p.Previsao = g.Cancelou THEN 100.0 ELSE 0 END)
            AS DECIMAL(5,1))                                            AS acuracia_pct
FROM dbo.PrevisaoCancelamento p
JOIN dbo.GabaritoNovos g ON g.AlunoID = p.AlunoID;

-- 3) Matriz de confusão (onde o modelo acerta e onde erra)
SELECT g.Cancelou AS real_cancelou,
       p.Previsao AS previsto_cancelou,
       COUNT(*)   AS alunos
FROM dbo.PrevisaoCancelamento p
JOIN dbo.GabaritoNovos g ON g.AlunoID = p.AlunoID
GROUP BY g.Cancelou, p.Previsao
ORDER BY g.Cancelou, p.Previsao;
GO

-- 4) View para o Power BI: alunos novos + probabilidade + faixa de risco
CREATE OR ALTER VIEW dbo.vw_PowerBI_Previsao AS
SELECT n.AlunoID, n.Nome, n.Email, n.Sexo, n.Idade, n.Cidade, n.Plano,
       n.MesesMatriculado, n.FrequenciaSemanal, n.DistanciaKm,
       n.PersonalTrainer, n.AulasColetivas, n.AtrasosPagamento, n.Avaliacao,
       p.Previsao,
       p.Probabilidade,
       CASE WHEN p.Probabilidade >= 0.70 THEN 'Alto'
            WHEN p.Probabilidade >= 0.40 THEN 'Médio'
            ELSE 'Baixo' END AS FaixaRisco,
       g.Cancelou AS CancelouReal,
       CASE WHEN n.FrequenciaSemanal < 1.5 THEN '1) Menos de 1,5x'
            WHEN n.FrequenciaSemanal < 3   THEN '2) 1,5x a 3x'
            WHEN n.FrequenciaSemanal < 4.5 THEN '3) 3x a 4,5x'
            ELSE '4) 4,5x ou mais' END AS FaixaFrequencia
FROM dbo.AlunosNovos n
JOIN dbo.PrevisaoCancelamento p ON p.AlunoID = n.AlunoID
LEFT JOIN dbo.GabaritoNovos g   ON g.AlunoID = n.AlunoID;
GO

-- 5) View para o Power BI: base histórica (treino)
CREATE OR ALTER VIEW dbo.vw_PowerBI_Historico AS
SELECT AlunoID, Sexo, Idade, Cidade, Plano, MesesMatriculado, FrequenciaSemanal,
       DistanciaKm, PersonalTrainer, AulasColetivas, AtrasosPagamento, Avaliacao,
       Cancelou,
       CASE WHEN Cancelou = 1 THEN 'Cancelou' ELSE 'Continua' END AS Situacao,
       CASE WHEN FrequenciaSemanal < 1.5 THEN '1) Menos de 1,5x'
            WHEN FrequenciaSemanal < 3   THEN '2) 1,5x a 3x'
            WHEN FrequenciaSemanal < 4.5 THEN '3) 3x a 4,5x'
            ELSE '4) 4,5x ou mais' END AS FaixaFrequencia,
       CASE WHEN Idade < 25 THEN '16 a 24'
            WHEN Idade < 35 THEN '25 a 34'
            WHEN Idade < 45 THEN '35 a 44'
            ELSE '45 ou mais' END AS FaixaIdade
FROM dbo.Alunos;
GO

-- Conferência das views
SELECT FaixaRisco, COUNT(*) AS alunos FROM dbo.vw_PowerBI_Previsao GROUP BY FaixaRisco;
