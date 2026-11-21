API Raízes do Nordeste
Protótipo acadêmico de uma API REST para apoiar operações da rede Raízes do Nordeste. Desenvolvido em Python com FastAPI, permite cadastrar e consultar unidades, produtos e estoque, além de criar pedidos autenticados e simular pagamentos.

Funcionalidades
Cadastro e consulta de unidades e produtos.
Cadastro e consulta de estoque por unidade e produto.
Cadastro e login de usuários com autenticação por token Bearer.
Criação e consulta dos pedidos do usuário autenticado.
Validação de estoque e redução da quantidade após a criação do pedido.
Simulação de pagamento aprovado, sem processamento real de cartões.
Tecnologias
Python, FastAPI, Pydantic, SQLAlchemy, Uvicorn e Swagger UI. O banco e sua configuração devem ser confirmados em app/infrastructure/database.py.

Como executar
Abra um terminal na pasta raiz do projeto.
Crie e ative um ambiente virtual. No PowerShell do Windows, use python -m venv .venv e depois .\.venv\Scripts\Activate.ps1.
Instale as dependências registradas em requirements.txt com pip install -r requirements.txt.
Inicie a API com uvicorn app.main:app --reload.
Acesse a documentação interativa em http://127.0.0.1:8000/docs.
Principais endpoints



Método	Endpoint	Finalidade
GET / POST	/unidades/	Consultar ou cadastrar unidades
GET / POST	/produtos/	Consultar ou cadastrar produtos
GET / POST	/estoques/	Consultar ou cadastrar estoque
POST	/auth/cadastro	Cadastrar usuário
POST	/auth/login	Fazer login e obter token
GET	/auth/me	Consultar o usuário autenticado
GET / POST	/pedidos/	Consultar ou criar pedidos autenticados
POST	/pagamentos/{pedido_id}	Simular o pagamento de um pedido
Os caminhos devem ser conferidos no Swagger, que apresenta as rotas disponibilizadas pela versão atual do projeto.

Escopo e limitações
Este projeto é um protótipo acadêmico. O pagamento é simulado; não há processamento real de cartões. Recursos como relatórios gerenciais, auditoria completa e integração com um provedor externo de pagamento podem ser considerados como evolução futura.

Autoria
Projeto acadêmico — Desenvolvimento Back End
Aluno: Matheu Alves Oliveira da Silva
RU: 4579323
