$aws = "C:\Users\Jay Patel\AppData\Local\Programs\Amazon\AWSCLIV2\aws.exe"
$region = "ap-south-1"
$profile = "agent-toolkit"
$stackName = "MT5-AlgoTrading-Stack"
$keyName = "mt5-cloud-keypair"
$keyFile = "f:\multi agent\cloud\mt5-cloud-keypair.pem"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  Deploying MetaTrader 5 Cloud VPS to AWS (Free Tier)     " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Create EC2 KeyPair if it doesn't already exist
Write-Host "`n[1/3] Checking / Creating EC2 KeyPair ($keyName)..." -ForegroundColor Green
$keyCheck = & $aws ec2 describe-key-pairs --key-names $keyName --region $region --profile $profile 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "  -> Generating new keypair..." -ForegroundColor Yellow
    $keyMaterial = & $aws ec2 create-key-pair --key-name $keyName --query "KeyMaterial" --output text --region $region --profile $profile
    $keyMaterial | Out-File -FilePath $keyFile -Encoding ASCII
    Write-Host "  -> Saved private key to: $keyFile" -ForegroundColor White
} else {
    Write-Host "  -> KeyPair already exists in AWS." -ForegroundColor White
}

# 2. Deploy CloudFormation Stack
Write-Host "`n[2/3] Deploying CloudFormation Stack ($stackName)..." -ForegroundColor Green
$templateFile = "f:\multi agent\cloud\mt5_windows_cloud.yaml"
& $aws cloudformation deploy `
    --template-file $templateFile `
    --stack-name $stackName `
    --parameter-overrides KeyPairName=$keyName `
    --capabilities CAPABILITY_IAM `
    --region $region `
    --profile $profile

# 3. Retrieve Instance Details
Write-Host "`n[3/3] Retrieving Instance Connection Details..." -ForegroundColor Green
$outputs = & $aws cloudformation describe-stacks --stack-name $stackName --region $region --profile $profile --query "Stacks[0].Outputs" --output json | ConvertFrom-Json

$publicIp = ($outputs | Where-Object { $_.OutputKey -eq "PublicIP" }).OutputValue
$instanceId = ($outputs | Where-Object { $_.OutputKey -eq "InstanceId" }).OutputValue

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  Deployment Successful!                                  " -ForegroundColor Cyan
Write-Host "  Instance ID : $instanceId" -ForegroundColor White
Write-Host "  Public IP   : $publicIp" -ForegroundColor Yellow
Write-Host "  RDP Address : $publicIp:3389" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "`nTo connect via Windows Remote Desktop:"
Write-Host "1. Press Win+R, type 'mstsc', and press Enter."
Write-Host "2. Computer: $publicIp"
Write-Host "3. Username: Administrator"
Write-Host "4. For Password, run: aws ec2 get-password-data --instance-id $instanceId --priv-launch-key $keyFile --region $region --profile $profile"
