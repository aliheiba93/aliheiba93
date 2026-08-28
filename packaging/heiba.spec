# Build on Windows: pyinstaller packaging/heiba.spec
from PyInstaller.building.build_main import Analysis, PYZ, EXE, COLLECT
from PyInstaller.utils.hooks import collect_submodules

hiddenimports = collect_submodules('heiba_ai')
datas = [('packaging/models', 'models')]

gui_a = Analysis(['heiba_ai/main.py'], pathex=['.'], hiddenimports=hiddenimports, datas=datas, binaries=[], excludes=[], noarchive=False)
gui_pyz = PYZ(gui_a.pure)
gui_exe = EXE(gui_pyz, gui_a.scripts, [], exclude_binaries=True, name='HeibaAI', debug=False, console=False)
gui_dist = COLLECT(gui_exe, gui_a.binaries, gui_a.datas, strip=False, upx=False, name='HeibaAI')

cli_a = Analysis(['heiba_ai/cli.py'], pathex=['.'], hiddenimports=hiddenimports, datas=datas, binaries=[], excludes=[], noarchive=False)
cli_pyz = PYZ(cli_a.pure)
cli_exe = EXE(cli_pyz, cli_a.scripts, [], exclude_binaries=True, name='heiba-cli', debug=False, console=True)
cli_dist = COLLECT(cli_exe, cli_a.binaries, cli_a.datas, strip=False, upx=False, name='heiba-cli')
