$new = Read-Host "Enter password for new DB user 'thyroid' (input will be hidden)" -AsSecureString
$ptr = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($new)
$plain = [System.Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr)
[System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr)

$sql = @"
CREATE DATABASE IF NOT EXISTS thyroid_db;
CREATE USER IF NOT EXISTS 'thyroid'@'localhost' IDENTIFIED BY '$plain';
ALTER USER 'thyroid'@'localhost' IDENTIFIED BY '$plain';
GRANT ALL PRIVILEGES ON thyroid_db.* TO 'thyroid'@'localhost';
FLUSH PRIVILEGES;
"@

$temp = Join-Path $env:TEMP "create_thyroid.sql"
Set-Content -Path $temp -Value $sql -Encoding ASCII

$mysql = 'C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe'
if (-Not (Test-Path $mysql)) {
    Write-Error "mysql client not found at $mysql"
    exit 1
}

Write-Host "You will be prompted for the MySQL root password next."
Get-Content $temp -Raw | & $mysql -u root -p

if ($LASTEXITCODE -eq 0) {
    Write-Host "Creating application tables from data.sql..."
    & $mysql -u thyroid -p$plain thyroid_db -e "source data.sql"
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Could not connect as 'thyroid'. Check the password and MySQL user setup above."
        Remove-Item $temp -ErrorAction SilentlyContinue
        exit 1
    }
} else {
    Write-Error "Could not create the database user. Check the MySQL root password and errors above."
    Remove-Item $temp -ErrorAction SilentlyContinue
    exit 1
}

Remove-Item $temp -ErrorAction SilentlyContinue
Write-Host "Done. The database, user, and tables were created."
