# Identity match API

#### Specifications
- Based on [FastAPI](fastapi.tiangolo.com/)
- Includes unit tests
- Uses HTTP Basic Auth
- Possibility to use either a default data file or to provide a new one
(see current input scheme with the default data at `data/examples.json`)
- SAP interface using [Bulma.io](https://www.bulma.io)

#### Build & start
``sh build.sh``

#### Test & manually (re)start
``docker exec -it id_match_api_container bash`` (enter the container)

``pytest``

``uvicorn src.main:app --reload``

#### Check

Default API
- endpoint: [http://127.0.0.1:8000/service_api_default](http://127.0.0.1:8000/service_api_default)
- parameters: ``apikey`` (default = apikey123)

Specific API
- endpoint: [http://127.0.0.1:8000/service_api](http://127.0.0.1:8000/service_api)
- parameters: ``apikey`` (default = apikey123), ``filepath`` : path to data file

To access the related UI, simply change the string `_api` into `_ui` within the API urls.
Then log in with the id `service_ui_admin` and password `ponytail`

API links: 
- [http://127.0.0.1:8000/service_api?apikey=apikey123&filepath=../data/examples.json](http://127.0.0.1:8000/service_api?apikey=apikey123&filepath=../data/examples.json)
- [http://127.0.0.1:8000/service_api_default?apikey=apikey123](http://127.0.0.1:8000/service_api_default?apikey=apikey123)

UI links: 
- [http://127.0.0.1:8000/service_ui?apikey=apikey123&filepath=../data/examples.json](http://127.0.0.1:8000/service_ui?apikey=apikey123&filepath=../data/examples.json)
- [http://127.0.0.1:8000/service_ui_default?apikey=apikey123](http://127.0.0.1:8000/service_ui_default?apikey=apikey123)
