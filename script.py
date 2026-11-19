import asyncio
from pathlib import Path
from urllib.parse import urljoin
from playwright.async_api import async_playwright

START_URL = "https://www.romsgames.net/roms/super-nintendo/?page=23&sort=popularity"
DOWNLOAD_DIR = Path("./page23").resolve()

# Ajuste conforme sua conexão e tolerância do site (ex.: 3 a 5 abas simultâneas)
MAX_CONCURRENT_DOWNLOADS = 8

CARD_LINK_SELECTOR = "a[href*='/super-nintendo-rom-']"
DOWNLOAD_BTN_SELECTOR = "a[href*='download'], button:has-text('Save Game'), a:has-text('Save Game')"


async def baixar_jogo(context, semaphore: asyncio.Semaphore, idx: int, total: int, url: str):
    async with semaphore:
        game_page = await context.new_page()
        try:
            print(f"[{idx}/{total}] Abrindo: {url}")
            await game_page.goto(url, wait_until="domcontentloaded")

            btn = game_page.locator(DOWNLOAD_BTN_SELECTOR).first
            await btn.wait_for(state="visible", timeout=15000)

            # Aguarda o evento de início do download disparado pelo clique
            async with game_page.expect_download(timeout=60000) as download_info:
                await btn.click()

            download = await download_info.value
            suggested_name = download.suggested_filename or f"rom_{idx}.zip"
            dest_path = DOWNLOAD_DIR / suggested_name

            # Aguarda o download concluir e salva na pasta de destino
            await download.save_as(str(dest_path))
            print(f"  [{idx}/{total}] Salvo em: {dest_path}")

        except Exception as e:
            print(f"  [{idx}/{total}] Erro ao baixar {url}: {e}")
        finally:
            await game_page.close()
            # Pequena pausa para espaçar requisições entre lotes
            await asyncio.sleep(1)


async def baixar_todos():
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(accept_downloads=True)
        page = await context.new_page()

        await page.goto(START_URL, wait_until="domcontentloaded")
        await page.wait_for_timeout(2000)

        hrefs = await page.locator(CARD_LINK_SELECTOR).evaluate_all(
            "els => els.map(e => e.getAttribute('href')).filter(Boolean)"
        )
        game_urls = list(dict.fromkeys(urljoin(START_URL, h) for h in hrefs))
        total = len(game_urls)

        print(f"Encontrados {total} links de jogos. Iniciando com até {MAX_CONCURRENT_DOWNLOADS} abas simultâneas...")

        semaphore = asyncio.Semaphore(MAX_CONCURRENT_DOWNLOADS)
        tasks = [
            baixar_jogo(context, semaphore, idx, total, url)
            for idx, url in enumerate(game_urls, start=1)
        ]

        await asyncio.gather(*tasks)
        await browser.close()


if __name__ == "__main__":
    asyncio.run(baixar_todos())
