#!/bin/bash -v
function download_redis {
  DOWNLOAD_PATH=$HOME/redis/redis-$2
  curl "$1" --output "$DOWNLOAD_PATH.tar.gz"
  if [ ! -f "$DOWNLOAD_PATH" ]; then
    mkdir "$DOWNLOAD_PATH"
  fi
  tar xzvf "$DOWNLOAD_PATH.tar.gz" --strip-components 1 -C "$DOWNLOAD_PATH"
  rm "$DOWNLOAD_PATH.tar.gz"
  (cd "$DOWNLOAD_PATH"; make)

}

if [ ! -f "$HOME/redis" ]; then
  mkdir $HOME/redis
fi

download_redis https://download.redis.io/releases/redis-8.10.1.tar.gz 8.10
download_redis https://download.redis.io/releases/redis-8.8.2.tar.gz 8.8
download_redis https://download.redis.io/releases/redis-8.6.6.tar.gz 8.6
download_redis https://download.redis.io/releases/redis-8.4.6.tar.gz 8.4
download_redis https://download.redis.io/releases/redis-8.2.9.tar.gz 8.2
download_redis https://download.redis.io/releases/redis-7.4.11.tar.gz 7.4
download_redis https://download.redis.io/releases/redis-7.2.16.tar.gz 7.2
download_redis https://download.redis.io/releases/redis-6.2.24.tar.gz 6.2
