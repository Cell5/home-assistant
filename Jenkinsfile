pipeline {
  agent any

  environment {
    TERRAFORM_DIR = 'terraform'
    PYTHON_SCRIPT = 'deploy_stack.py'
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }
    stage('Terraform Init') {
      steps {
        dir(env.TERRAFORM_DIR) {
          sh 'terraform init -input=false'
        }
      }
    }
    stage('Terraform Plan') {
      steps {
        dir(env.TERRAFORM_DIR) {
          sh 'terraform plan -out=tfplan -input=false'
        }
      }
    }
    stage('Terraform Apply') {
      steps {
        dir(env.TERRAFORM_DIR) {
          sh 'terraform apply -input=false tfplan'
        }
      }
    }
    stage('Deploy Home Assistant Stack') {
      steps {
        sh "python ${env.PYTHON_SCRIPT} --stack-name home-assistant --zigbee-device /dev/ttyUSB0 --up"
      }
    }
  }

  post {
    always {
      archiveArtifacts artifacts: 'docker-compose.yaml', allowEmptyArchive: true
    }
  }
}
