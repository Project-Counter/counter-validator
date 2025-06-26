# How to build a docker image which the GitLab CI/CD pipeline uses

In the root of the project run:

    docker buildx build -t beda42/validator-ci:01 -f .gitlab/Dockerfile .

This will build the docker image and tag it with `beda42/validator-ci:01`.
You can then push the image to the GitLab registry:

    docker push beda42/validator-ci:01

(You need to be logged in to the GitLab registry to push the image. To log in, run `docker login`.)
