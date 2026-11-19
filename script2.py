from pathlib import Path
import zipfile

# Pasta onde estão os arquivos .zip baixados
SOURCE_DIR = Path("./page23").resolve()

# Pasta raiz onde este script está salvo
DEST_DIR = Path(__file__).resolve().parent

# Opcional: mude para True se quiser apagar os .zip após extrair com sucesso
DELETE_ZIP_AFTER_EXTRACT = False


def extrair_zips():
    if not SOURCE_DIR.exists():
        print(f"Pasta de origem não encontrada: {SOURCE_DIR}")
        return

    zip_files = sorted(SOURCE_DIR.glob("*.zip"))
    if not zip_files:
        print(f"Nenhum arquivo .zip encontrado em: {SOURCE_DIR}")
        return

    print(f"Encontrados {len(zip_files)} arquivos .zip. Extraindo para: {DEST_DIR}")

    for idx, zip_path in enumerate(zip_files, start=1):
        try:
            with zipfile.ZipFile(zip_path, "r") as zf:
                # Verifica se há arquivos corrompidos antes de extrair
                bad_file = zf.testzip()
                if bad_file is not None:
                    print(f"[{idx}/{len(zip_files)}] Arquivo corrompido em {zip_path.name}: {bad_file}")
                    continue

                zf.extractall(DEST_DIR)
                print(f"[{idx}/{len(zip_files)}] Extraído: {zip_path.name}")

            if DELETE_ZIP_AFTER_EXTRACT:
                zip_path.unlink()
                print(f"  -> Removido: {zip_path.name}")

        except zipfile.BadZipFile:
            print(f"[{idx}/{len(zip_files)}] Erro: '{zip_path.name}' não é um ZIP válido ou está incompleto.")
        except Exception as e:
            print(f"[{idx}/{len(zip_files)}] Erro ao extrair '{zip_path.name}': {e}")


if __name__ == "__main__":
    extrair_zips()
