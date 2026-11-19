from pathlib import Path
import shutil
import zipfile

START_PAGE = 29
END_PAGE = 45

# Pasta raiz onde este script está salvo
DEST_DIR = Path(__file__).resolve().parent

# Opcional: mude para True se quiser apagar os .zip após extrair com sucesso
DELETE_ZIP_AFTER_EXTRACT = False


def processar_pasta(source_dir: Path, page_num: int):
    print(f"\n=== Página {page_num}/{END_PAGE}: {source_dir} ===")

    if not source_dir.exists():
        print(f"Pasta não encontrada, pulando: {source_dir}")
        return

    if source_dir.resolve() == DEST_DIR.resolve():
        print("Pasta de origem é igual à pasta de destino; pulando para evitar conflito.")
        return

    all_files = sorted(p for p in source_dir.iterdir() if p.is_file())
    if not all_files:
        print(f"Nenhum arquivo encontrado em: {source_dir}")
        shutil.rmtree(source_dir)
        print(f"  -> Pasta vazia removida: {source_dir.name}")
        return

    zip_files = [p for p in all_files if p.suffix.lower() == ".zip"]
    non_zip_files = [p for p in all_files if p.suffix.lower() != ".zip"]
    had_errors = False

    print(f"Encontrados {len(zip_files)} arquivos .zip e {len(non_zip_files)} arquivos não-zip.")

    # 1. Descompacta arquivos .zip na raiz do script
    for idx, zip_path in enumerate(zip_files, start=1):
        try:
            with zipfile.ZipFile(zip_path, "r") as zf:
                bad_file = zf.testzip()
                if bad_file is not None:
                    print(f"  [ZIP {idx}/{len(zip_files)}] Arquivo corrompido em {zip_path.name}: {bad_file}")
                    had_errors = True
                    continue

                zf.extractall(DEST_DIR)
                print(f"  [ZIP {idx}/{len(zip_files)}] Extraído: {zip_path.name}")

            if DELETE_ZIP_AFTER_EXTRACT:
                zip_path.unlink()
                print(f"    -> Removido: {zip_path.name}")

        except zipfile.BadZipFile:
            print(f"  [ZIP {idx}/{len(zip_files)}] Erro: '{zip_path.name}' não é um ZIP válido ou está incompleto.")
            had_errors = True
        except Exception as e:
            print(f"  [ZIP {idx}/{len(zip_files)}] Erro ao extrair '{zip_path.name}': {e}")
            had_errors = True

    # 2. Copia arquivos que não são .zip para a raiz do script
    for idx, file_path in enumerate(non_zip_files, start=1):
        try:
            dest_file = DEST_DIR / file_path.name
            shutil.copy2(file_path, dest_file)
            print(f"  [COPIA {idx}/{len(non_zip_files)}] Copiado para raiz: {file_path.name}")
        except Exception as e:
            print(f"  [COPIA {idx}/{len(non_zip_files)}] Erro ao copiar '{file_path.name}': {e}")
            had_errors = True

    # 3. Exclui a pasta ao final se tudo ocorreu sem erros
    if not had_errors:
        try:
            shutil.rmtree(source_dir)
            print(f"  -> Pasta excluída: {source_dir.name}")
        except Exception as e:
            print(f"  -> Erro ao excluir a pasta '{source_dir.name}': {e}")
    else:
        print(f"  -> Pasta mantida por precaução devido a erros em algum arquivo: {source_dir.name}")


def processar_intervalo_paginas():
    print(f"Destino final (raiz): {DEST_DIR}")
    for page_num in range(START_PAGE, END_PAGE + 1):
        source_dir = DEST_DIR / f"page{page_num}"
        processar_pasta(source_dir, page_num)
    print("\nProcessamento de todas as páginas concluído!")


if __name__ == "__main__":
    processar_intervalo_paginas()
