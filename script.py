import asyncio
import os
from pathlib import Path
from urllib.parse import urljoin
from playwright.async_api import async_playwright

START_URL = "https://www.romsgames.net/roms/super-nintendo/?page=23&sort=popularity"
DOWNLOAD_DIR = Path("/").resolve()

# Ajuste estes seletores conforme o HTML atual da página (inspecione com F12)
CARD_LINK_SELECTOR = "a[href*='/super-nintendo-rom-']"
DOWNLOAD_BTN_SELECTOR = "a[href*='download'], button:has-text('Save Game'), a:has-text('Save Game')"


async def baixar_todos():
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as p:
        # accept_downloads=True é essencial para o Playwright salvar os arquivos
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(accept_downloads=True)
        page = await context.new_page()

        await page.goto(START_URL, wait_until="domcontentloaded")
        await page.wait_for_timeout(2000)

        # Coleta URLs únicas dos jogos listados na página
        hrefs = await page.locator(CARD_LINK_SELECTOR).evaluate_all(
            "els => els.map(e => e.getAttribute('href')).filter(Boolean)"
        )
        game_urls = list(dict.fromkeys(urljoin(START_URL, h) for h in hrefs))

        print(f"Encontrados {len(game_urls)} links de jogos.")

        for idx, url in enumerate(game_urls, start=1):
            game_page = await context.new_page()
            try:
                print(f"[{idx}/{len(game_urls)}] Abrindo: {url}")
                await game_page.goto(url, wait_until="domcontentloaded")

                btn = game_page.locator(DOWNLOAD_BTN_SELECTOR).first
                await btn.wait_for(state="visible", timeout=15000)

                # Aguarda o evento de início do download disparado pelo clique
                async with game_page.expect_download(timeout=60000) as download_info:
                    await btn.click()

                download = await download_info.value
                suggested_name = download.suggested_filename or f"rom_{idx}.zip"
                dest_path = DOWNLOAD_DIR / suggested_name

                # save_as aguarda o download ser concluído no disco
                await download.save_as(str(dest_path))
                print(f"  -> Salvo em: {dest_path}")

            except Exception as e:
                print(f"  -> Erro ao baixar {url}: {e}")
            finally:
                # Fecha a aba do jogo, mantendo a página principal aberta
                await game_page.close()
                # Pausa entre requisições para reduzir chances de bloqueio
                await asyncio.sleep(2)

        await browser.close()


if __name__ == "__main__":
    asyncio.run(baixar_todos())
