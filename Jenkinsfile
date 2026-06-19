pipeline {
  agent any

  environment {
    TERRAFORM_DIR = 'terraform'
    PYTHON_SCRIPT = 'deploy_stack.py'
    STACK_NAME = 'hass'
    ZIGBEE_DEVICE = '/dev/ttyUSB0'
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
        sh "python ${env.PYTHON_SCRIPT} --stack-name ${env.STACK_NAME} --zigbee-device ${env.ZIGBEE_DEVICE} --up"
      }
    }
  }

  post {
    always {
      archiveArtifacts artifacts: 'docker-compose.yaml', allowEmptyArchive: true
    }
  }
}
