# Build on Windows: pyinstaller packaging/heiba.spec
from PyInstaller.utils.hooks import collect_submodules
hiddenimports = collect_submodules('heiba_ai')
a = Analysis(['heiba_ai/main.py'], pathex=['.'], hiddenimports=hiddenimports, datas=[('packaging/models','models')], binaries=[], excludes=[])
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, a.binaries, a.datas, [], name='HeibaAI', debug=False, console=False)
cli_a = Analysis(['heiba_ai/cli.py'], pathex=['.'], hiddenimports=hiddenimports, datas=[('packaging/models','models')], binaries=[], excludes=[])
cli_pyz = PYZ(cli_a.pure)
cli_exe = EXE(cli_pyz, cli_a.scripts, cli_a.binaries, cli_a.datas, [], name='heiba-cli', debug=False, console=True)
