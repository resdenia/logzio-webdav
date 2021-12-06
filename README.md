# logzio-webdav

A Docker image purpose-built to monitor Salesforce Commerce Cloud (fka Demandware) logs using Logzio Python shipper.

Python Application that includes modules:

pygrok
webdavclient3
logzio-python-handler
python-decouple
python-json-logger
codecs

## Installation

1. Use `git` to clone this repository into a suitable folder:

```sh
git clone https://github.com/resdenia/logzio-webdav.git logzio-webdav
```

2. Define parameters

| Parameter            |  Description  | Require |
| -------------------- | :-----------: | ------: |
| LOGZIO_LISTENER_URL  | logz listener |     YES |
| LOGZIO_SHIPPING_KEY  | logz listener |     YES |
| WEBDAV_USERNAME      | logz listener |     YES |
| WEBDAV_PASSWORD      | logz listener |     YES |
| SEND_HISTORICAL_LOGS | logz listener |     YES |
| SEND_UNPARSE_LOGS    | logz listener |     YES |
| WEBDAV_DIR_LINK      | logz listener |     YES |
| WEBDAV_DIR           | logz listener |     YES |
| GROK_PATTERNS        | logz listener |     YES |

3. Use `docker` to build a container from this image:

## Usage

## License

logz.io for WebDav is licensed under the [Apache 2.0](http://apache.org/licenses/LICENSE-2.0.txt) License.
