token=`cat .env | grep "SONARQUBE_SCANER=" | sed 's/SONARQUBE_SCANER=//'`

sonar-scanner \
  -Dsonar.projectKey=test-1 \
  -Dsonar.sources=. \
  -Dsonar.host.url=http://localhost:9000 \
  -Dsonar.login=$token