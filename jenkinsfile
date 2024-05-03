pipeline {
    agent any
    
    stages {
        stage('Build') {
            steps {
                // Add build steps here (e.g., compiling code, running tests)
                sh 'echo "Building..."'
            }
        }
        stage('Test') {
            steps {
                // Add test steps here (e.g., running unit tests, integration tests)
                sh 'echo "Testing..."'
            }
        }
        stage('Deploy') {
            steps {
                // Add deployment steps here (e.g., deploying to a server)
                sh 'echo "Deploying..."'
            }
        }
    }
    
    post {
        success {
            // Actions to perform if the pipeline succeeds
            echo 'Pipeline succeeded!'
        }
        failure {
            // Actions to perform if the pipeline fails
            echo 'Pipeline failed!'
        }
        always {
            // Actions to perform regardless of pipeline outcome
            echo 'Pipeline completed.'
        }
    }
}
