#!/bin/sh
for docker_arch in amd64 arm32v6 arm64v8; do
  cp Dockerfile.cross Dockerfile.${docker_arch}
  sed -i "s|__BASEIMAGE_ARCH__|${docker_arch}|g" Dockerfile.${docker_arch}
done
