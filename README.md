# emmu-snes-roms

Repositório e conjunto de scripts de automação em Python com **Playwright** para baixar, extrair e consolidar ROMs de Super Nintendo (SNES) diretamente na pasta raiz do repositório (`emmu-snes-roms/`).

---

## Avisos e Disclaimers Legais

> **Importante — Direitos Autorais e Propriedade Intelectual:**
> * Este repositório contém **exclusivamente scripts de automação e organização de arquivos** — nenhuma ROM ou material protegido por direitos autorais é hospedado ou distribuído intencionalmente por meio deste código.
> * ROMs de jogos de Super Nintendo podem estar protegidas por leis de direitos autorais e marcas registradas de seus respectivos detentores. O uso deste projeto deve se restringir a backups de jogos que você possui legalmente, conteúdos em domínio público, *homebrew* ou cenários permitidos pela legislação vigente no seu país.
> * O autor deste repositório não se responsabiliza pelo uso indevido dos scripts, por violações de direitos autorais cometidas por terceiros ou por eventuais restrições impostas por sites externos.

> **Aviso de Uso de Automação e Responsabilidade Técnica:**
> * Sites de terceiros podem aplicar limites de taxa (*rate limiting*), proteções anti-bot, alterações de layout/seletores ou termos de serviço que restrinjam automação.
> * Utilize o script de forma responsável, respeitando intervalos entre requisições e evitando sobrecarga em servidores externos.
> * Os scripts são fornecidos *"no estado em que se encontram" (as-is)*, sem garantias expressas ou implícitas de funcionamento contínuo ou isenção de erros.

---

## Estrutura do Repositório

Ao executar o fluxo completo, as ROMs descompactadas e demais arquivos não-ZIP ficam na **raiz** de `emmu-snes-roms/`:

```text
emmu-snes-roms/
├── Script.py          # Baixa os arquivos das páginas configuradas usando Playwright
├── Script2.py         # Extrai .zip, copia arquivos não-zip para a raiz e remove pastas pageX
├── README.md          # Documentação do repositório
└── *.sfc / *.smc      # ROMs extraídas ou copiadas diretamente para a raiz (exemplo)
```

## Pré-requisitos

Python 3.10+ instalado e disponível no PATH (verifique com python --version ou python3 --version).
Playwright instalado no ambiente Python:
```pip install playwright```

Navegador Chromium configurado para o Playwright:
```playwright install chromium```

(Opcional, recomendado em Linux) Dependências do sistema para o Chromium:
```playwright install-deps chromium```

## Execução Completa (Passo a Passo)

### Passo 1: Clonar ou acessar o repositório

```git clone <URL-DO-REPOSITORIO> emmu-snes-roms```
```cd emmu-snes-roms```

#### (Opcional) Crie e ative um ambiente virtual antes de instalar as dependências:

```python -m venv .venv```

##### Windows (PowerShell):

```.\.venv\Scripts\Activate.ps1```

##### Linux / macOS:

```source .venv/bin/activate```

### Passo 2: Configurar e executar o download (Script.py)

Abra Script.py e ajuste os parâmetros principais conforme necessário:
START_PAGE e END_PAGE: definem o intervalo de páginas a percorrer (ex.: 29 até 45).
URL_TEMPLATE: URL paginada de origem (https://www.romsgames.net/roms/super-nintendo/?page={page}&sort=popularity).
MAX_CONCURRENT_DOWNLOADS: número máximo de abas/downloads simultâneos (ex.: 8; reduza para 3 ou 4 caso ocorram timeouts ou bloqueios).
CARD_LINK_SELECTOR e DOWNLOAD_BTN_SELECTOR: seletores usados para localizar os links dos jogos e o botão de download.
Execute o download:
```python Script.py```

Durante essa etapa:
O navegador Chromium abre cada página configurada (START_PAGE até END_PAGE).
Os links dos jogos são coletados e abertos em abas concorrentes controladas por asyncio.Semaphore.
Cada arquivo baixado é salvo temporariamente dentro da pasta correspondente (page29/, page30/, ..., page45/).
Passo 3: Pós-processamento — Extrair .zip, copiar demais arquivos para a raiz e limpar pastas (Script2.py)
Abra Script2.py e verifique as configurações:
START_PAGE e END_PAGE: devem corresponder ao intervalo de pastas pageX a processar (ex.: 29 até 45).
DEST_DIR: já aponta para a pasta raiz do script (Path(__file__).resolve().parent), onde as ROMs finais ficarão.
DELETE_ZIP_AFTER_EXTRACT: defina como True se quiser remover os .zip individuais após a extração bem-sucedida.
Execute o pós-processamento:
```python Script2.py```

O que acontece em cada pasta pageX durante o pós-processamento:
Verificação da pasta: checa se pageX existe e não é igual à pasta de destino.
Validação e extração de .zip: testa a integridade de cada arquivo .zip (zf.testzip()) e extrai seu conteúdo diretamente para a raiz (emmu-snes-roms/).
Cópia de arquivos não-ZIP: copia para a raiz qualquer arquivo que não tenha extensão .zip (ex.: .sfc, .smc, etc.) preservando metadados com shutil.copy2.
Limpeza da pasta: ao concluir a pasta pageX sem erros, exclui o diretório pageX com shutil.rmtree(source_dir) antes de avançar para a próxima página. Se ocorrer algum erro naquela pasta, ela é mantida para inspeção.
Solução de Problemas e Boas Práticas
Muitos erros de timeout ou bloqueio temporário: diminua MAX_CONCURRENT_DOWNLOADS (ex.: de 8 para 3 ou 4) e aumente os tempos de espera (asyncio.sleep) em Script.py.
Botão ou card não encontrado: inspecione a página no navegador (F12) para verificar se houve mudança nos seletores HTML ou pop-ups/temporizadores na página do jogo.
Pasta pageX não foi excluída: indica que ocorreu falha na extração de algum .zip ou na cópia de algum arquivo dentro daquela pasta; verifique o log no terminal antes de apagar manualmente.
Versionamento com Git: evite commitar arquivos de ROMs (.sfc, .smc, .zip, etc.) e pastas temporárias page* adicionando-os ao .gitignore.
Contribuição e Licença
Contribuições, sugestões e correções são bem-vindas via issues ou pull requests. Caso adicione uma licença ao repositório (como MIT para os scripts), consulte o arquivo LICENSE para os termos específicos aplicáveis ao código.