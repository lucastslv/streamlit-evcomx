# Deploy do app

Este diretório contém o necessário para rodar o Streamlit em container. O `Dockerfile` da raiz
empacota o app, as dependências e os dados/artefatos que ele lê em runtime.

## 1. Docker local

Na raiz do projeto:

```bash
docker build -t evcomx-carga-alta .
docker run --rm -p 8501:8501 --name evcomx-app evcomx-carga-alta
```

Abra `http://localhost:8501`.

O container roda como usuário sem privilégios, tem `HEALTHCHECK` em `/_stcore/health` e não
depende de banco de dados. Reiniciar o container não perde nada: o estado é só a sessão do
Streamlit.

### Docker Compose

```bash
docker compose up --build -d
docker compose logs -f
docker compose down
```

## 2. VM com HTTPS (Caddy)

Para uma URL privada e com TLS, use uma VM Linux (Ubuntu 22.04/24.04, por exemplo).

1. Aponte um domínio para o IP da VM (registro A).
2. Instale Docker na VM.
3. Copie o projeto para a VM.
4. Em `deploy/`:

```bash
cp .env.example .env
# edite DOMAIN=app.seudominio.com
docker compose -f docker-compose.prod.yml up -d --build
```

5. Libere as portas **80** e **443** no firewall/security group. O Caddy obtém o certificado
   automaticamente e faz proxy para o app na porta interna 8501. A porta 8501 não fica exposta
   publicamente.

```bash
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs -f
```

Para atualizar:

```bash
git pull
docker compose -f docker-compose.prod.yml up -d --build
```

## 3. Streamlit Community Cloud

O app também roda no Streamlit Community Cloud, desde que o repositório esteja no GitHub.

1. Suba o repositório (sem `.venv`, com `data/` e `models/`).
2. Em <https://share.streamlit.io>, crie um app apontando para o repositório.
3. Main file path: `app.py`.
4. O Streamlit Cloud usa `requirements.txt` e `runtime.txt` (Python 3.12).
5. Confirme que os dados podem ficar em um app público. Se houver restrição da EVCOMX,
   prefira a VM privada ou um ambiente com SSO/VPN.

O app é somente leitura em relação aos dados; não há upload nem banco.

## 4. Render, Railway e Fly.io

O `Dockerfile` é compatível com plataformas que fazem build de container:

- **Render**: New → Web Service → Docker; health check `/_stcore/health`; porta 8501.
- **Railway**: New Project → Deploy from repo; a plataforma detecta o `Dockerfile`; porta 8501.
- **Fly.io**: `fly launch --dockerfile Dockerfile` e `fly deploy`; configure
  `internal_port = 8501` no `fly.toml`.

Em qualquer uma, configure o health check para `/_stcore/health` e não exponha a porta sem TLS
se os dados forem sensíveis.

## 5. Pipeline do modelo

Este Dockerfile é o **entregável Streamlit**. O guia da apresentação também pede o **pipeline do
modelo com Docker**, que é um artefato separado. O `projeto-bootcamp/` tem os notebooks e o
`joblib`, mas ainda não tem um `Dockerfile`/entrypoint que rode do dado ao resultado.

O modelo didático do simulador pode ser regenerado dentro da imagem:

```bash
docker run --rm \
  --user "$(id -u):$(id -g)" \
  -v "$PWD/data:/app/data" \
  -v "$PWD/models:/app/models" \
  evcomx-carga-alta \
  python scripts/train_simulator.py
```

Isso atualiza `data/app/` e `models/app_simulator.joblib` no host. O ensemble oficial continua
sendo o reportado em `projeto-bootcamp/relatorios_complementares/`.

## Checklist rápido

- [ ] `docker build` conclui sem erro.
- [ ] `docker run` responde em `http://localhost:8501`.
- [ ] `/_stcore/health` retorna 200.
- [ ] Dados e artefatos estão na imagem (ou em volume, se preferir).
- [ ] TLS e autenticação definidos antes de expor dados da empresa.
- [ ] Política de dados confirmada com a EVCOMX/professor.
