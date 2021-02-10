#!groovy
pipeline {
  agent any

  tools {nodejs "node"}
  
  stages {
    stage('Upload to CDN') {
      when {
        anyOf {
          branch 'master';
        }
      }
      environment {
        AWS_ACCESS_KEY_ID = credentials('aws_access_key_id')
        AWS_SECRET_ACCESS_KEY = credentials('aws_secret_access_key')
      }
      steps {
        sh 'npm i'
        sh 'bash -n hotpatch'
        sh 'node cdn_upload.js ff_locust.py redwolfsecurity.com-public-cdn-production ff/python/import/ff_locust.py E3I5LA88VUO8LT'
      }
    }
  }
  post {
    cleanup {
      echo 'One way or another, I have finished'
      deleteDir()
    }
  }
}
