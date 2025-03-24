# 🧾 Sistema de Gerenciamento de Clientes com Flask

Este é um sistema web desenvolvido com **Flask** e **MySQL** que permite o gerenciamento de clientes de forma segura e individual para cada administrador. Cada usuário tem acesso apenas aos seus próprios registros, garantindo privacidade e organização.

---

## 🚀 Funcionalidades

- ✅ Cadastro e login de administradores
- ✅ Hash de senha com segurança (Werkzeug)
- ✅ Tela principal com total de clientes
- ✅ Adição, edição e exclusão de clientes
- ✅ Visualização detalhada por modal
- ✅ Exportação de dados para CSV
- ✅ Filtros dinâmicos e busca em tempo real
- ✅ Acesso restrito por `usuario_id`

---

## 💻 Tecnologias Utilizadas

- **Python** (Flask, Flask-Login, SQLAlchemy)
- **MySQL** (com PyMySQL)
- **HTML5 + CSS3 (Bootstrap 5)**
- **JavaScript Vanilla**
- **Pandas** (para exportação de CSV)

---

## 🔐 Multiusuário com Acesso Individual

Cada administrador tem um painel exclusivo. Isso é feito através do campo `usuario_id` nos registros de clientes, vinculado ao `current_user.id` de cada usuário logado.

---

## 🏗️ Estrutura do Projeto

