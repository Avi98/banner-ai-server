# Banner ai Server


## Setup gcloud crenditals
- gcloud crenditals are required for llm to work

install gcloud cli based on OS from [here](https://cloud.google.com/sdk/docs/install) 

Run following cmd for Application Default Credendtials(ADC) 

```gcloud auth application-default login```

## Setup server 

- Clone repo
- Create virtual env using following cmd

```
uv venv
```

- Activate Virtual env

```
source .venv/bin/activate
```

- install chromium 

```
playwright install chromium --with-deps

```

### Run server

```
uv main:app --reload

```
-- 