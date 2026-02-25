pipeline {
  agent any

  options {
    // Always start with a clean workspace
    skipDefaultCheckout()
  }

  stages {

    stage('Checkout') {
      steps {
        echo 'Fetching latest source code...'
        checkout([
          $class: 'GitSCM',
          branches: [[name: 'main']],
          userRemoteConfigs: [[
            url: 'https://github.com/Ender19722072/smokeTime.git',
            credentialsId: 'github'   // <-- Add this credential in Jenkins
          ]]
        ])
      }
    }

    stage('Build') {
      steps {
        echo 'Building Docker image...'
        sh '''
          docker build --pull --no-cache -t smoke-time .
        '''
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
  }
}
