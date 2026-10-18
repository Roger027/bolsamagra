# Publicação privada do Bolsa Magra

O dashboard continua em Streamlit. A hospedagem Render mantém o endereço do
site disponível sem depender deste computador; o Supabase guarda os dados
compartilhados. No celular, o site pode ser adicionado à tela inicial como
atalho. Esse atalho abre o site no navegador e não funciona offline como um
aplicativo nativo.

Os planos gratuitos podem pausar o serviço Render após inatividade e suspender
projetos Supabase sem atividade prolongada. Como os dados ficam no banco
Supabase, a pausa do site não apaga os registros. Confira os limites e as
regras atuais dos provedores antes de guardar dados importantes.

## 1. Criar o banco compartilhado

1. Crie um projeto Supabase e guarde a URL do projeto e a chave `service_role`
   em um gerenciador seguro. Nunca publique essa chave nem a envie pelo chat.
2. No SQL Editor do Supabase, execute
   [`migrations/finance_state.sql`](./migrations/finance_state.sql).
3. No painel do Supabase, confirme que a tabela `finance_state` foi criada.

A tabela bloqueia leitura e gravação direta de usuários `anon` e
`authenticated`; só o backend do dashboard usa a chave privada do servidor.

## 2. Preparar o login Google

1. Crie um cliente OAuth do tipo aplicação Web no Google Cloud.
2. Depois de criar o serviço no Render, copie o endereço HTTPS dele.
3. Registre como URI de redirecionamento autorizada:
   `https://SEU-SERVICO.onrender.com/oauth2callback`
4. Guarde o Client ID e o Client Secret para configurar o Render.

O acesso ao dashboard é limitado aos endereços listados em
`AUTHORIZED_EMAILS`. Informe os e-mails Google autorizados separados por
vírgulas. Pessoas fora dessa lista não conseguem consultar os dados, mesmo
que tenham o endereço do site.

## 3. Publicar pelo Render

1. Crie um repositório **privado** no GitHub e envie o código, sem incluir
   `.env`, arquivos CSV ou `.streamlit/secrets.toml`. Essas exclusões já estão
   em `.gitignore`; confira `git status` antes de publicar.
2. No Render, crie um Blueprint a partir desse repositório. O arquivo
   [`render.yaml`](./render.yaml) configura o serviço gratuito.
3. Configure no Render os valores pedidos pelo Blueprint:
   - `SUPABASE_URL`: URL do projeto Supabase.
   - `SUPABASE_SERVICE_ROLE_KEY`: chave privada do backend Supabase.
   - `STREAMLIT_COOKIE_SECRET`: segredo aleatório longo, único e permanente.
   - `AUTHORIZED_EMAILS`: e-mails autorizados, separados por vírgulas.
   - `GEMINI_API_KEY`: chave do Gemini; necessária somente para os recursos
     de IA.
4. Depois que o Render atribuir um endereço HTTPS ao serviço, crie o cliente
   OAuth Google usando esse endereço e URI de retorno terminada em
   `/oauth2callback`.
5. No painel do Render, adicione `GOOGLE_OIDC_CLIENT_ID` e
   `GOOGLE_OIDC_CLIENT_SECRET` como variáveis privadas e faça novo deploy.
   O inicializador monta o arquivo de configuração privado do Streamlit; os
   segredos não entram no repositório.

O site continua público na internet, mas o conteúdo financeiro exige login
Google e validação da lista de convidados. O dashboard compartilha os mesmos
dados entre todas as contas autorizadas.

## 4. Migrar os dados atuais uma vez

1. Acrescente `SUPABASE_URL` e `SUPABASE_SERVICE_ROLE_KEY` ao `.env` já
   existente no computador que contém os CSVs. Não sobrescreva esse arquivo;
   `.env.example` serve apenas como referência de nomes.
3. Confirme que `obrigacoes.csv` e `dividas_reais.csv` são os arquivos atuais.
4. No PowerShell, execute:

   ```powershell
   & ".\.venv\Scripts\python.exe" ".\migrar_para_supabase.py"
   ```

O importador inclui obrigações, dívidas, faturas, receitas, saídas e pagamentos.
Ele cancela a operação se o banco já contiver dados, para não sobrescrever
registros existentes. Mantenha os CSVs originais como cópia de segurança até
confirmar os dados no site.

Depois da migração, o dashboard hospedado lê e grava no Supabase; CSVs no
disco do serviço não são usados como armazenamento. A execução dos scripts
locais que recriam CSVs não altera automaticamente os dados na nuvem.

## 5. Adicionar à tela inicial do celular

- **Android:** abra o endereço do Render no Chrome, abra o menu e escolha
  **Adicionar à tela inicial** ou **Instalar app** (o nome varia conforme o
  navegador).
- **iPhone:** abra o endereço no Safari, toque em **Compartilhar** e escolha
  **Adicionar à Tela de Início**.

É necessário ter internet para consultar ou editar os dados. Para compartilhar,
envie o endereço do Render apenas às pessoas convidadas; cada uma deve entrar
com o e-mail que foi incluído em `AUTHORIZED_EMAILS`.
