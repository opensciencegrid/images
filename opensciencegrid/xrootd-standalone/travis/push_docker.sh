if [[ "${TRAVIS_PULL_REQUEST}" != "false" ]]; then
    echo "DockerHub deployment not performed for pull requests"
    exit 0
fi

docker_repos='xrootd-standalone'
# Credentials for docker push                                                                                                                                                 
echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin

for repo in $docker_repos; do
    for tag in $timestamp fresh; do
        docker push $org/$repo:$tag
    done
done
