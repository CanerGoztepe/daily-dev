$ErrorActionPreference = "Stop"

$ProjectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectDir

function Require-Command {
    param(
        [string]$Name,
        [string]$InstallHint
    )

    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        Write-Host ""
        Write-Host "$Name bulunamadi." -ForegroundColor Red
        Write-Host $InstallHint -ForegroundColor Yellow
        exit 1
    }
}

# ------------------------------------------------------------
# GitHub CLI PATH kontrolü
# ------------------------------------------------------------

if (-not (Get-Command "gh" -ErrorAction SilentlyContinue)) {
    $PossibleGhPaths = @(
        "C:\Program Files\GitHub CLI",
        "$env:LOCALAPPDATA\Programs\GitHub CLI"
    )

    foreach ($GhDirectory in $PossibleGhPaths) {
        $GhExecutable = Join-Path $GhDirectory "gh.exe"

        if (Test-Path $GhExecutable) {
            $env:Path = "$GhDirectory;$env:Path"
            break
        }
    }
}

Require-Command "git" "Kurulum: winget install --id Git.Git"
Require-Command "gh" "Kurulum: winget install --id GitHub.cli"
Require-Command "python" "Kurulum: winget install --id Python.Python.3.12"

# ------------------------------------------------------------
# GitHub giriş kontrolü
# ------------------------------------------------------------

Write-Host "GitHub girisi kontrol ediliyor..." -ForegroundColor Cyan

$PreviousErrorActionPreference = $ErrorActionPreference
$ErrorActionPreference = "Continue"

& gh auth status 1>$null 2>$null
$GhAuthStatus = $LASTEXITCODE

$ErrorActionPreference = $PreviousErrorActionPreference

if ($GhAuthStatus -ne 0) {
    Write-Host "Tarayicida GitHub girisi acilacak." -ForegroundColor Yellow

    & gh auth login `
        --hostname github.com `
        --git-protocol https `
        --web

    if ($LASTEXITCODE -ne 0) {
        throw "GitHub girisi tamamlanamadi."
    }
}
else {
    Write-Host "GitHub girisi zaten mevcut." -ForegroundColor Green
}

# ------------------------------------------------------------
# Git kimlik bilgilerini GitHub CLI ile bağla
# ------------------------------------------------------------

& gh auth setup-git

if ($LASTEXITCODE -ne 0) {
    throw "Git kimlik bilgileri GitHub CLI ile ayarlanamadi."
}

# ------------------------------------------------------------
# Git repo kontrolü
# ------------------------------------------------------------

if (-not (Test-Path ".git")) {
    Write-Host ""
    Write-Host "Bu klasor bir Git deposu degil:" -ForegroundColor Red
    Write-Host $ProjectDir
    Write-Host ""
    Write-Host "Bu iki dosyayi mevcut GitHub repo klasorune koymalisin." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Ornek klasor:" -ForegroundColor Yellow
    Write-Host "C:\github\daily-dev"
    exit 1
}

# ------------------------------------------------------------
# Remote kontrolü
# ------------------------------------------------------------

$PreviousErrorActionPreference = $ErrorActionPreference
$ErrorActionPreference = "Continue"

$Remote = & git remote get-url origin 2>$null
$RemoteExitCode = $LASTEXITCODE

$ErrorActionPreference = $PreviousErrorActionPreference

if ($RemoteExitCode -ne 0 -or [string]::IsNullOrWhiteSpace($Remote)) {
    Write-Host ""
    Write-Host "origin remote bulunamadi." -ForegroundColor Red
    Write-Host ""
    Write-Host "Ornek:" -ForegroundColor Yellow
    Write-Host "git remote add origin https://github.com/KULLANICI/REPO.git"
    exit 1
}

Write-Host "GitHub reposu bulundu:" -ForegroundColor Green
Write-Host $Remote

# ------------------------------------------------------------
# Git kullanıcı adı
# ------------------------------------------------------------

$GitName = & git config user.name

if ([string]::IsNullOrWhiteSpace($GitName)) {
    $Login = & gh api user --jq ".login"

    if ([string]::IsNullOrWhiteSpace($Login)) {
        throw "GitHub kullanici adi alinamadi."
    }

    & git config user.name $Login

    if ($LASTEXITCODE -ne 0) {
        throw "Git kullanici adi ayarlanamadi."
    }

    Write-Host "Git kullanici adi ayarlandi: $Login" -ForegroundColor Green
}
else {
    Write-Host "Git kullanici adi: $GitName" -ForegroundColor Green
}

# ------------------------------------------------------------
# Git e-posta
# ------------------------------------------------------------

$GitEmail = & git config user.email

if ([string]::IsNullOrWhiteSpace($GitEmail)) {
    Write-Host ""
    Write-Host "Commitlerin profilinde gorunmesi icin GitHub hesabina bagli e-posta gerekir." -ForegroundColor Yellow
    Write-Host "GitHub noreply adresini de kullanabilirsin." -ForegroundColor Yellow

    $Email = Read-Host "GitHub hesabina bagli e-posta veya noreply adresi"

    if ([string]::IsNullOrWhiteSpace($Email)) {
        throw "Git e-posta adresi bos birakilamaz."
    }

    & git config user.email $Email

    if ($LASTEXITCODE -ne 0) {
        throw "Git e-posta adresi ayarlanamadi."
    }

    Write-Host "Git e-posta adresi ayarlandi." -ForegroundColor Green
}
else {
    Write-Host "Git e-posta adresi: $GitEmail" -ForegroundColor Green
}

# ------------------------------------------------------------
# OpenAI API anahtarı
# ------------------------------------------------------------

if (-not (Test-Path ".env")) {
    Write-Host ""
    Write-Host "OpenAI API anahtari .env dosyasina kaydedilecek." -ForegroundColor Cyan

    $SecureKey = Read-Host "OpenAI API anahtarini gir" -AsSecureString
    $Ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($SecureKey)

    try {
        $ApiKey = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($Ptr)
    }
    finally {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($Ptr)
    }

    if ([string]::IsNullOrWhiteSpace($ApiKey)) {
        throw "API anahtari bos birakilamaz."
    }

    "OPENAI_API_KEY=$ApiKey" | Set-Content -Encoding UTF8 ".env"

    Write-Host ".env dosyasi olusturuldu." -ForegroundColor Green
}
else {
    Write-Host ".env dosyasi zaten mevcut." -ForegroundColor Green
}

# ------------------------------------------------------------
# .gitignore
# ------------------------------------------------------------

if (-not (Test-Path ".gitignore")) {
    New-Item ".gitignore" -ItemType File | Out-Null
}

$IgnoreContent = @(Get-Content ".gitignore" -ErrorAction SilentlyContinue)

$RequiredIgnores = @(
    ".env",
    ".venv/",
    "__pycache__/",
    "daily-ai.log"
)

foreach ($Item in $RequiredIgnores) {
    if ($IgnoreContent -notcontains $Item) {
        Add-Content ".gitignore" $Item
    }
}

# ------------------------------------------------------------
# Python sanal ortamı
# ------------------------------------------------------------

if (-not (Test-Path ".venv")) {
    Write-Host "Python sanal ortami kuruluyor..." -ForegroundColor Cyan

    & python -m venv .venv

    if ($LASTEXITCODE -ne 0) {
        throw "Python sanal ortami olusturulamadi."
    }
}
else {
    Write-Host "Python sanal ortami zaten mevcut." -ForegroundColor Green
}

$PythonExe = Join-Path $ProjectDir ".venv\Scripts\python.exe"

if (-not (Test-Path $PythonExe)) {
    throw "Python sanal ortam calistiricisi bulunamadi: $PythonExe"
}

# ------------------------------------------------------------
# Python paketleri
# ------------------------------------------------------------

Write-Host "Gerekli Python paketleri kuruluyor..." -ForegroundColor Cyan

& $PythonExe -m pip install --quiet --upgrade pip

if ($LASTEXITCODE -ne 0) {
    throw "pip guncellenemedi."
}

& $PythonExe -m pip uninstall --quiet --yes openai

& $PythonExe -m pip install `
    --quiet `
    --upgrade `
    "google-genai>=1.0.0" `
    "python-dotenv>=1.0.0"

if ($LASTEXITCODE -ne 0) {
    throw "Python paketleri kurulamadi."
}

# ------------------------------------------------------------
# Commit scripti kontrolü
# ------------------------------------------------------------

$DailyCommitScript = Join-Path $ProjectDir "daily_commit.py"

if (-not (Test-Path $DailyCommitScript)) {
    throw "daily_commit.py bulunamadi: $DailyCommitScript"
}

# ------------------------------------------------------------
# Günlük commit scriptini çalıştır
# ------------------------------------------------------------

Write-Host ""
Write-Host "Gunluk commit scripti calistiriliyor..." -ForegroundColor Green

& $PythonExe $DailyCommitScript

if ($LASTEXITCODE -ne 0) {
    throw "daily_commit.py hata ile sonlandi."
}

Write-Host ""
Write-Host "Tamamlandi." -ForegroundColor Green