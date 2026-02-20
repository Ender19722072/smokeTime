pipeline {
  agent any
  stages {
    stage('Checkout') {
      steps {
        echo 'Pulling source code...'
        sh 'git pull origin main'
      }
    }

    stage('Build') {
      steps {
        echo 'Building Docker image...'
        sh 'docker build -t smoke-time .'
      }
    }

    stage('Test') {
      steps {
        echo 'Running tests...'
        sh 'python3 -m py_compile smokeTime.py'
      }
    }

    stage('Run') {
      steps {
        echo 'Running container...'
        sh '''
                    docker stop smoke-time || true
                    docker rm smoke-time || true
                    docker run -d --name smoke-time smoke-time
                '''
      }
    }

    stage('Deploy') {
      steps {
        echo 'Deploying application...'
      }
    }

    stage('Commit Changes') {
      when {
        expression {
          return fileExists('smokeTime.log')
        }

      }
      steps {
        echo 'Committing generated files...'
        sh '''
                    git config user.email "jenkins@ci"
                    git config user.name "Jenkins CI"
                    git add .
                    git commit -m "Automated commit from Jenkins" || true
                    git push origin HEAD:main || true
                '''
      }
    }

  }
}
