import asyncio
from pathlib import Path
from urllib.parse import urljoin
from playwright.async_api import async_playwright

START_PAGE = 29
END_PAGE = 45
URL_TEMPLATE = "https://www.romsgames.net/roms/super-nintendo/?page={page}&sort=popularity"
BASE_DIR = Path(__file__).resolve().parent

# Ajuste conforme sua conexão e tolerância do site (ex.: 3 a 5 abas simultâneas)
MAX_CONCURRENT_DOWNLOADS = 8

CARD_LINK_SELECTOR = "a[href*='/super-nintendo-rom-']"
DOWNLOAD_BTN_SELECTOR = "a[href*='download'], button:has-text('Save Game'), a:has-text('Save Game')"


async def baixar_jogo(context, semaphore: asyncio.Semaphore, download_dir: Path, idx: int, total: int, url: str):
    async with semaphore:
        game_page = await context.new_page()
        try:
            print(f"  [{idx}/{total}] Abrindo: {url}")
            await game_page.goto(url, wait_until="domcontentloaded")

            btn = game_page.locator(DOWNLOAD_BTN_SELECTOR).first
            await btn.wait_for(state="visible", timeout=15000)

            # Aguarda o evento de início do download disparado pelo clique
            async with game_page.expect_download(timeout=60000) as download_info:
                await btn.click()

            download = await download_info.value
            suggested_name = download.suggested_filename or f"rom_{idx}.zip"
            dest_path = download_dir / suggested_name

            # Aguarda o download concluir e salva na pasta da página
            await download.save_as(str(dest_path))
            print(f"    [{idx}/{total}] Salvo em: {dest_path}")

        except Exception as e:
            print(f"    [{idx}/{total}] Erro ao baixar {url}: {e}")
        finally:
            await game_page.close()
            # Pequena pausa para espaçar requisições entre lotes
            await asyncio.sleep(1)


async def processar_pagina(context, list_page, page_num: int):
    page_url = URL_TEMPLATE.format(page=page_num)
    download_dir = BASE_DIR / f"page{page_num}"
    download_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n=== Página {page_num}/{END_PAGE}: {page_url} ===")
    await list_page.goto(page_url, wait_until="domcontentloaded")
    await list_page.wait_for_timeout(2000)

    hrefs = await list_page.locator(CARD_LINK_SELECTOR).evaluate_all(
        "els => els.map(e => e.getAttribute('href')).filter(Boolean)"
    )
    game_urls = list(dict.fromkeys(urljoin(page_url, h) for h in hrefs))
    total = len(game_urls)

    if total == 0:
        print(f"Nenhum jogo encontrado na página {page_num}.")
        return

    print(f"Encontrados {total} links na página {page_num}. Baixando em: {download_dir}")

    semaphore = asyncio.Semaphore(MAX_CONCURRENT_DOWNLOADS)
    tasks = [
        baixar_jogo(context, semaphore, download_dir, idx, total, url)
        for idx, url in enumerate(game_urls, start=1)
    ]

    await asyncio.gather(*tasks)


async def baixar_intervalo_paginas():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(accept_downloads=True)
        list_page = await context.new_page()

        for page_num in range(START_PAGE, END_PAGE + 1):
            await processar_pagina(context, list_page, page_num)

        await browser.close()
        print("\nProcesso concluído para todas as páginas!")


if __name__ == "__main__":
    asyncio.run(baixar_intervalo_paginas())
