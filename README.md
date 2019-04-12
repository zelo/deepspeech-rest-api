deepspeech rest api
===================

Simple api over mozilla deepspeech voice recognition engine.

## Endpoints
```
POST /api/v1/stt - Just look at curl command below

$  curl -X POST -F "speech=@./speech.mp3" http://127.0.0.1:9000/api/v1/stt 
➜ {"text":"but over all revenue and"}
```

## Setup

### 0. Checkout repository
`git clone git@github.com:zelo/deepspeech-rest-api.git`

### 1. Download deepspeech data model
1. Look at `requirements.pip` file and find what is the current 
deepspeech library version used by this api
2. Go to `https://github.com/mozilla/DeepSpeech/releases` and find release doc for this version.
It should contain link to download data model. For version 0.4.1 it's `https://github.com/mozilla/DeepSpeech/releases/download/v0.4.1/deepspeech-0.4.1-models.tar.gz`
3. Download and extract above package content to `<repository_root>/model`

### 2.1 Using docker
1. Enter `<repository_root>`
#### 2.1.1 Using `docker-compose`
1. Run `docker-compose up`
#### 2.1.2 Using `docker run`
1. Build image
`docker build . --tag zelo/deepspeech-rest-api:0.4.1`
2. Run
`docker run --rm --publish=127.0.0.1:9000:8000 --volume=$(pwd)/model:/app/model:ro zelo/deepspeech-rest-api:0.4.1`
### 2.2 Running outside of docker
Just look at the content of `Dockerfile` it contains complete instruction to setup app under `debian`
