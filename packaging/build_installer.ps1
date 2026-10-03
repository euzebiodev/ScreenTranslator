# Gera o executavel (PyInstaller) e o instalador Windows (Inno Setup) do
# Screen Translator. Rode a partir de qualquer diretorio:
#
#   powershell -ExecutionPolicy Bypass -File packaging\build_installer.ps1
#
# Pre-requisitos neste computador (ja presentes quando este script foi
# escrito): pacote Python "pyinstaller", Tesseract-OCR instalado em
# "C:\Program Files\Tesseract-OCR" e Inno Setup 6 instalado.

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$Dist = Join-Path $Root "dist"
$Build = Join-Path $Root "build"
$AppDist = Join-Path $Dist "ScreenTranslator"
$TesseractSrc = "C:\Program Files\Tesseract-OCR"
$TesseractDst = Join-Path $AppDist "tesseract"

# Conjunto minimo de arquivos do Tesseract necessarios para OCR em ingles
# (testado manualmente — exclui ferramentas de treinamento, docs e idiomas
# nao usados pelo app, reduzindo de ~239 MB para ~120 MB).
$TesseractDlls = @(
    "libtesseract-5.dll", "libleptonica-6.dll", "libpng16-16.dll", "libjpeg-8.dll",
    "libtiff-6.dll", "libwebp-7.dll", "libwebpmux-3.dll", "libsharpyuv-0.dll",
    "libopenjp2-7.dll", "liblzma-5.dll", "libjbig-0.dll", "libdeflate.dll",
    "libLerc.dll", "libzstd.dll", "libgif-7.dll", "libwinpthread-1.dll",
    "libgcc_s_seh-1.dll", "libstdc++-6.dll", "zlib1.dll", "libbz2-1.dll",
    "libarchive-13.dll", "libb2-1.dll", "liblz4.dll", "libcrypto-3-x64.dll",
    "libiconv-2.dll"
)

Write-Host "== 1/3: limpando build/ e dist/ anteriores ==" -ForegroundColor Cyan
Remove-Item $Dist, $Build -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "== 2/3: empacotando com PyInstaller ==" -ForegroundColor Cyan
Push-Location $Root
try {
    pyinstaller main.py `
        --name ScreenTranslator `
        --onedir `
        --windowed `
        --noconfirm `
        --icon "assets\icon.ico" `
        --add-data "assets;assets" `
        --collect-all deep_translator `
        --collect-all pystray `
        --hidden-import truststore
    if ($LASTEXITCODE -ne 0) { throw "PyInstaller falhou (codigo $LASTEXITCODE)" }
}
finally {
    Pop-Location
}

Write-Host "== 2b/3: copiando Tesseract (apenas o necessario) ==" -ForegroundColor Cyan
if (-not (Test-Path $TesseractSrc)) {
    throw "Tesseract nao encontrado em '$TesseractSrc'. Instale via: winget install UB-Mannheim.TesseractOCR"
}
New-Item -ItemType Directory -Force -Path (Join-Path $TesseractDst "tessdata") | Out-Null
Copy-Item (Join-Path $TesseractSrc "tesseract.exe") $TesseractDst
Copy-Item (Join-Path $TesseractSrc "tessdata\eng.traineddata") (Join-Path $TesseractDst "tessdata")
foreach ($dll in $TesseractDlls) {
    $src = Join-Path $TesseractSrc $dll
    if (-not (Test-Path $src)) {
        Write-Warning "DLL esperada nao encontrada: $dll (pode faltar na versao instalada do Tesseract)"
        continue
    }
    Copy-Item $src $TesseractDst
}

$sizeMb = [math]::Round((Get-ChildItem $AppDist -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB, 1)
Write-Host "Pasta empacotada: $AppDist ($sizeMb MB)" -ForegroundColor Green

Write-Host "== 3/3: compilando instalador com Inno Setup ==" -ForegroundColor Cyan
$IsccCandidates = @(
    "C:\Program Files*\Inno Setup *\ISCC.exe"
    "$env:LOCALAPPDATA\Programs\Inno Setup *\ISCC.exe"
)
$Iscc = $IsccCandidates | ForEach-Object { Get-ChildItem $_ -ErrorAction SilentlyContinue } | Select-Object -First 1
if (-not $Iscc) {
    throw "ISCC.exe (Inno Setup) nao encontrado. Instale via: winget install JRSoftware.InnoSetup"
}
& $Iscc.FullName (Join-Path $Root "packaging\installer.iss")
if ($LASTEXITCODE -ne 0) { throw "Inno Setup falhou (codigo $LASTEXITCODE)" }

Write-Host "`nInstalador gerado em packaging\output\" -ForegroundColor Green
