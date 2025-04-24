🧑‍💼 Sistema Informatizado de Gestão de Passivo Fiscal

Este é um sistema web robusto desenvolvido com Flask e MySQL, voltado para o gerenciamento de passivos fiscais de múltiplas empresas. O objetivo é oferecer uma plataforma integrada e segura para controle de dívidas (federais, estaduais e municipais), cobrança judicial e administrativa, auditorias e negociações, com visualizações consolidadas por empresa ou portfólio.

🔐 Cada administrador acessa somente seus clientes e painéis autorizados.

✨ Funcionalidades Principais

✅ Autenticação com Flask-Login e hash de senhas
    
✅ Painéis modulares por empresa e visão geral do portfólio

✅ Cadastro, edição e exclusão de clientes

✅ Filtros dinâmicos por empresa, tributo, status e período

✅ Monitoramento detalhado de dívidas e cobrança judicial

✅ Alertas de prazos, vencimentos e riscos fiscais

✅ Exportação de dados e gráficos interativos

✅ Controle de acesso com usuario_id e perfis diferenciados

🧩 Estrutura dos Painéis do Sistema

1. Painel Gerencial (Visão Geral do Portfólio)

Exibe indicadores macro para o escritório como um todo: número de empresas gerenciadas, valor total da dívida consolidada, ranking de maiores devedores, distribuição por esfera (federal, estadual, municipal) e alertas globais. Inclui filtros por tags, responsáveis internos e status das dívidas.

2. Painel de Dados da Empresa

Permite selecionar uma empresa específica e visualizar seus dados básicos, como razão social, CNPJ, contatos, regime tributário, status de CNDs, risco fiscal e resumo rápido da dívida. Oferece links diretos para os demais painéis já filtrados pela empresa.

3. Painel de Débitos Federais

Mostra a dívida federal da empresa selecionada com gráficos de composição por tributo e origem, lista detalhada de débitos (nº do processo, tributo, valor, multa, juros, status), e detalhes de parcelamentos ativos. Possui filtros secundários por tributo, status e período.

4. Painel de Débitos Estaduais

Semelhante ao painel federal, mas foca nos débitos estaduais, permitindo análise por estado de atuação da empresa. Traz valor total, tributos, parcelamentos e filtros como PA e status.

5. Painel de Débitos Municipais

Detalha os débitos municipais da empresa, com composição por tributo/origem, lista de dívidas, parcelamentos e status. Pode ser usado para consolidar valores de ISS e outras taxas municipais.

6. Painel da Cobrança Judicial

Permite visualizar execuções fiscais e processos judiciais, tanto por empresa quanto por todo o portfólio. Mostra status processual, prazos, garantias e permite alertas por proximidade de vencimento. Pode ser filtrado por esfera, status, vara e responsável.

7. Painel de Auditoria da Dívida

Acompanha os débitos em contestação. Mostra valores auditados, potencial de economia, fundamentos jurídicos e status da auditoria. Permite visão por empresa ou consolidação da carteira inteira.

8. Painel de Negociação da Dívida

Focado em parcelamentos e programas de transação. Exibe valor negociado, economia gerada, condições dos acordos e status das negociações. Inclui alertas de vencimento de parcelas e análise agregada de programas mais eficazes.

9. Painel de Monitoramento da Cobrança Administrativa e Judicial

Traz a evolução dos débitos desde a notificação administrativa até a execução judicial, detalhando cada estágio: CDA emitida, protestada, ajuizada, penhora, redirecionamento, leilão, entre outros. Classifica os riscos (baixo a crítico) e organiza ações pendentes e datas relevantes.

📌 Considerações Adicionais

O seletor de empresas estará presente em quase todos os painéis, como um filtro global.

A performance foi projetada para grandes volumes de dados, com foco em responsividade e agilidade.

A padronização visual dos painéis facilita a navegação e reduz a curva de aprendizado dos usuários.

Permissões avançadas garantem que apenas perfis autorizados vejam determinados dados.

🛠️ Tecnologias Utilizadas

Python – Flask, Flask-Login, SQLAlchemy

MySQL – com PyMySQL

HTML5 + CSS3 – usando Bootstrap 5

JavaScript Vanilla + jQuery para funcionalidades dinâmicas

Pandas – para exportação e análise de dados

🔐 Acesso Multiusuário Restrito

Cada administrador é vinculado a um usuario_id, e todas as consultas no sistema são filtradas por esse identificador. A aplicação garante que nenhum administrador veja dados de outro.

Perfis com permissões diferenciadas garantem acesso seletivo a empresas, painéis e dados.

📂 Organização do Projeto

app.py – Inicialização da aplicação Flask

routes/ – Blueprints por módulo (painéis, autenticação, notificações, etc.)

models/ – Modelos de dados com SQLAlchemy

templates/ – HTML com Bootstrap e Jinja

static/ – CSS, JS, imagens

requirements.txt – Lista de dependências do projeto