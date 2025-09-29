FROM ubuntu:latest
LABEL authors="Nesterenko Anton"

ENTRYPOINT ["top", "-b"]