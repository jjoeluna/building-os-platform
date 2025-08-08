# BuildingOS API Testing Script
# Advanced PowerShell testing for all endpoints

param(
    [string]$BaseUrl = "https://pj4vlvxrg7.execute-api.us-east-1.amazonaws.com",
    [switch]$Detailed = $false,
    [switch]$Performance = $false
)

# Color functions
function Write-Success { param($Message) Write-Host $Message -ForegroundColor Green }
function Write-Error { param($Message) Write-Host $Message -ForegroundColor Red }
function Write-Info { param($Message) Write-Host $Message -ForegroundColor Cyan }
function Write-Warning { param($Message) Write-Host $Message -ForegroundColor Yellow }

# Test result tracking
$results = @()

function Test-Endpoint {
    param(
        [string]$Name,
        [string]$Method,
        [string]$Uri,
        [hashtable]$Headers = @{},
        [string]$Body = $null,
        [string]$ExpectedStatus = "Success"
    )
    
    Write-Info "`n=== Testing $Name ==="
    Write-Host "Method: $Method" -ForegroundColor Gray
    Write-Host "URI: $Uri" -ForegroundColor Gray
    
    $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
    $testResult = @{
        Name = $Name
        Method = $Method
        Uri = $Uri
        Status = "Unknown"
        ResponseTime = 0
        Error = $null
        Response = $null
    }
    
    try {
        $splat = @{
            Uri = $Uri
            Method = $Method
            Headers = $Headers
        }
        
        if ($Body) {
            $splat.Body = $Body
        }
        
        $response = Invoke-RestMethod @splat
        $stopwatch.Stop()
        
        $testResult.Status = "Success"
        $testResult.ResponseTime = $stopwatch.ElapsedMilliseconds
        $testResult.Response = $response
        
        Write-Success "✅ SUCCESS ($($stopwatch.ElapsedMilliseconds)ms)"
        
        if ($Detailed) {
            Write-Host "Response:" -ForegroundColor Gray
            $response | ConvertTo-Json -Depth 3 | Write-Host
        } else {
            $response | ConvertTo-Json -Compress | Write-Host
        }
        
    } catch {
        $stopwatch.Stop()
        $testResult.Status = "Failed"
        $testResult.ResponseTime = $stopwatch.ElapsedMilliseconds
        $testResult.Error = $_.Exception.Message
        
        Write-Error "❌ FAILED ($($stopwatch.ElapsedMilliseconds)ms)"
        Write-Error "Error: $($_.Exception.Message)"
    }
    
    $results += $testResult
    return $testResult
}

# Header definitions
$jsonHeaders = @{ 'Content-Type' = 'application/json' }

Write-Info "🚀 BuildingOS API Testing Suite"
Write-Info "Base URL: $BaseUrl"
Write-Info "Time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"

# Test 1: Health Check
Test-Endpoint -Name "Health Check" -Method "GET" -Uri "$BaseUrl/health"

# Test 2: Director (no parameters)
Test-Endpoint -Name "Director (Basic)" -Method "GET" -Uri "$BaseUrl/director"

# Test 3: Director (with parameters)
$directorUri = "$BaseUrl/director?user_request=" + [System.Web.HttpUtility]::UrlEncode("Test from PowerShell")
Test-Endpoint -Name "Director (With Message)" -Method "GET" -Uri $directorUri

# Test 4: Persona
$personaBody = @{
    user_id = "powershell-user-$(Get-Random)"
    message = "Hello from PowerShell testing suite!"
} | ConvertTo-Json

Test-Endpoint -Name "Persona" -Method "POST" -Uri "$BaseUrl/persona" -Headers $jsonHeaders -Body $personaBody

# Test 5: Persona Conversations
Test-Endpoint -Name "Persona Conversations" -Method "GET" -Uri "$BaseUrl/persona/conversations?user_id=test-user"

# Test 6: Elevator
$elevatorBody = @{
    mission_id = "powershell-test-$(Get-Random)"
    action = "check_elevator_status"
    parameters = @{
        floor = 3
    }
} | ConvertTo-Json

Test-Endpoint -Name "Elevator" -Method "POST" -Uri "$BaseUrl/elevator/call" -Headers $jsonHeaders -Body $elevatorBody

# Test 7: PSIM
$psimBody = @{
    action = "search_person"
    query = "powershell-test-user"
    parameters = @{
        department = "IT"
    }
} | ConvertTo-Json

Test-Endpoint -Name "PSIM" -Method "POST" -Uri "$BaseUrl/psim/search" -Headers $jsonHeaders -Body $psimBody

# Test 8: Coordinator
$missionId = "powershell-mission-$(Get-Random)"
Test-Endpoint -Name "Coordinator" -Method "GET" -Uri "$BaseUrl/coordinator/missions/$missionId"

# Summary Report
Write-Info "`n📊 TEST SUMMARY REPORT"
Write-Info "======================="

$successCount = ($results | Where-Object { $_.Status -eq "Success" }).Count
$failCount = ($results | Where-Object { $_.Status -eq "Failed" }).Count
$totalTests = $results.Count

Write-Host "Total Tests: $totalTests" -ForegroundColor White
Write-Success "Successful: $successCount"
Write-Error "Failed: $failCount"

if ($Performance) {
    Write-Info "`n⏱️ PERFORMANCE METRICS"
    Write-Info "====================="
    
    $avgResponseTime = ($results | Measure-Object -Property ResponseTime -Average).Average
    $maxResponseTime = ($results | Measure-Object -Property ResponseTime -Maximum).Maximum
    $minResponseTime = ($results | Where-Object { $_.ResponseTime -gt 0 } | Measure-Object -Property ResponseTime -Minimum).Minimum
    
    Write-Host "Average Response Time: $([math]::Round($avgResponseTime, 2))ms" -ForegroundColor Yellow
    Write-Host "Max Response Time: $maxResponseTime ms" -ForegroundColor Red
    Write-Host "Min Response Time: $minResponseTime ms" -ForegroundColor Green
    
    # Performance table
    Write-Info "`nDetailed Performance:"
    $results | Select-Object Name, Status, ResponseTime | Format-Table -AutoSize
}

# Failed tests details
$failedTests = $results | Where-Object { $_.Status -eq "Failed" }
if ($failedTests.Count -gt 0) {
    Write-Error "`n🚨 FAILED TESTS DETAILS"
    Write-Error "======================"
    
    foreach ($test in $failedTests) {
        Write-Host "$($test.Name): $($test.Error)" -ForegroundColor Red
    }
}

# Export results to JSON
$resultsFile = "api-test-results-$(Get-Date -Format 'yyyyMMdd-HHmmss').json"
$results | ConvertTo-Json -Depth 3 | Out-File -FilePath $resultsFile -Encoding UTF8
Write-Info "`n💾 Results exported to: $resultsFile"

Write-Info "`n🎯 Test completed at $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
