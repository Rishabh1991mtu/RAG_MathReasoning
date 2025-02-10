try {
    # Define headers
    $headers = @{
        "accept" = "application/json"
        "Content-Type" = "application/json"
    }

    # Define request body
    $body = @{
        "prompt" = "Find the general solution of y'' + 4y = 0."
        "top_k_param" = 3
    } | ConvertTo-Json -Depth 10

    # Send POST request
    $response = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/math-query" -Method Post -Headers $headers -Body $body

    # Print response
    Write-Output "Response from server:"
    Write-Output $response
}
catch {
    # Catch and display errors
    Write-Output "Error occurred while making the API request:"
    Write-Output $_.Exception.Message
}
