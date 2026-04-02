pipeline {
    agent any

    parameters {
        password(name: 'MONGO_URI', defaultValue: '', description: 'MongoDB connection URI for container runtime')
    }

    environment {
        IMAGE_NAME = 'products-api'
        CONTAINER_NAME = 'products-api-container'
        PORT = '8000'
        MONGO_URI = "${params.MONGO_URI}"
    }

    stages {
        stage('Checkout from GitHub') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                bat 'docker build -t %IMAGE_NAME% .'
            }
        }

        stage('Run Container in Background') {
            steps {
                powershell '''
                if ([string]::IsNullOrWhiteSpace($env:MONGO_URI)) {
                    throw "MONGO_URI parameter is empty. Provide your full MongoDB Atlas URI in Build with Parameters."
                }

                docker rm -f $env:CONTAINER_NAME 2>$null | Out-Null
                docker run -d --name $env:CONTAINER_NAME -p "$env:PORT`:$env:PORT" -e "MONGO_URI=$env:MONGO_URI" $env:IMAGE_NAME
                '''
            }
        }

        stage('Wait for API to Start') {
            steps {
                powershell '''
                $retries = 15
                $ready = $false
                for ($i = 1; $i -le $retries; $i++) {
                    Start-Sleep -Seconds 2
                    try {
                        $r = Invoke-WebRequest -Uri http://localhost:8000/health -UseBasicParsing -TimeoutSec 3
                        if ($r.StatusCode -eq 200) { $ready = $true; break }
                    } catch {}
                    Write-Host "Waiting for API... attempt $i/$retries"
                }
                if (-not $ready) {
                    docker logs $env:CONTAINER_NAME
                    throw "API did not start in time"
                }
                Write-Host "API is ready"
                '''
            }
        }

        stage('Run Python Unit Tests') {
            steps {
                bat '''
                docker exec %CONTAINER_NAME% python3 -m unittest discover -s tests -p "test_*.py"
                '''
            }
        }

        stage('Run Postman Tests (Newman)') {
            steps {
                bat '''
                newman run postman\\ProductsAPI.postman_collection.json               
                --reporters cli
                '''
            }
        }

        stage('Generate README.txt') {
            steps {
                bat '''
                echo Products API Endpoints > README.txt
                echo ====================== >> README.txt
                echo GET /getSingleProduct/{product_id} >> README.txt
                echo GET /getAll >> README.txt
                echo POST /addNew >> README.txt
                echo DELETE /deleteOne/{product_id} >> README.txt
                echo GET /startsWith/{letter} >> README.txt
                echo GET /paginate?start_id=...^&end_id=...^&page=... >> README.txt
                echo GET /convert/{product_id} >> README.txt
                echo GET /health >> README.txt
                echo GET /metrics >> README.txt
                echo GET / >> README.txt
                echo. >> README.txt
                echo FastAPI Docs: http://localhost:8000/docs >> README.txt
                '''
            }
        }

        stage('Create ZIP File') {
            steps {
                bat '''
                for /f %%i in ('powershell -Command "Get-Date -Format yyyy-MM-dd-HHmmss"') do set dt=%%i
                powershell -Command "Compress-Archive -Path * -DestinationPath complete-%dt%.zip"
                '''
            }
        }
    }

    post {
        always {
            bat 'docker rm -f %CONTAINER_NAME% 2>nul || exit /b 0'
        }
    }
}