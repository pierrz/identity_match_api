# Identity match API

<br>

### Specifications
- Based on [FastAPI](https://fastapi.tiangolo.com/)
- Includes unit tests
- Uses HTTP Basic Auth
- Possibility to use either a default data file or to provide a new one
(see current input scheme with the default data at `data/examples.json`)
- SAP interface using [Bulma.io](https://www.bulma.io)

<br>

### Build, test and start

##### => **Virtualenv**
``sh install.sh``

``source venv/bin/activate``

``uvicorn main:app --reload``

<br>

##### => Docker
``docker-compose up -d``

``docker exec -it api_prod bash``

###### still some issues to access the API urls from the host (wip on networking settings ...)

<br>

### Documentation

Visit [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) for an interactive documentation based on Swagger UI.

<br>

### Access

Default API
- endpoint: [http://127.0.0.1:8000/service_api_default](http://127.0.0.1:8000/service_api_default)
- parameters: ``apikey`` (default = apikey123)

<br>

Specific API
- endpoint: [http://127.0.0.1:8000/service_api](http://127.0.0.1:8000/service_api)
- parameters: ``apikey`` (default = apikey123), ``filepath`` : path to data file

<br>

To access the related UI, simply change the string `_api` into `_ui` within the API urls.
Then log in with the id `service_ui_admin` and password `ponytail`

<br>

API links: 
- [http://127.0.0.1:8000/service_api?apikey=apikey123&filepath=../data/examples.json](http://127.0.0.1:8000/service_api?apikey=apikey123&filepath=../data/examples.json)
- [http://127.0.0.1:8000/service_api_default?apikey=apikey123](http://127.0.0.1:8000/service_api_default?apikey=apikey123)

UI links: 
- [http://127.0.0.1:8000/service_ui?apikey=apikey123&filepath=../data/examples.json](http://127.0.0.1:8000/service_ui?apikey=apikey123&filepath=../data/examples.json)
- [http://127.0.0.1:8000/service_ui_default?apikey=apikey123](http://127.0.0.1:8000/service_ui_default?apikey=apikey123)
