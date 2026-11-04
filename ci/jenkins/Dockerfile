FROM jenkins/jenkins:2.580.2-lts-jdk21

# Pipeline'ların image build edebilmesi için Docker CLI ve buildx
COPY --from=docker:29.9-cli /usr/local/bin/docker /usr/local/bin/docker
COPY --from=docker:29.9-cli /usr/local/libexec/docker/cli-plugins/docker-buildx /usr/local/libexec/docker/cli-plugins/docker-buildx

# Plugin'ler kurulum sihirbazından değil, koddan gelir
COPY plugins.txt /usr/share/jenkins/ref/plugins.txt
RUN jenkins-plugin-cli --plugin-file /usr/share/jenkins/ref/plugins.txt
