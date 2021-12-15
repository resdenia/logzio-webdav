# logzio-webdav

A Docker image purpose-built to monitor Salesforce Commerce Cloud (fka Demandware) logs using Logzio Python shipper.

Python Application that includes modules:

pygrok \
webdavclient3 \
logzio-python-handler\
python-decouple\
[python-json-logger](https://docs.logz.io/shipping/log-sources/python.html)\
codecs

## Usage

1. Use `git` to clone this repository into a suitable folder:

```sh
git clone https://github.com/resdenia/logzio-webdav.git logzio-webdav
```

2. Define parameters

| Parameter            | Description                                                                                                                                                                                                                                                                                                                       | Required/Defaulr |
| -------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------: |
| LOGZIO_LISTENER_URL  | Determines protocol, listener host, and port. For example, https://<<LISTENER-HOST>>:8071.Replace <<LISTENER-HOST>> with your region's listener host (for example, listener.logz.io). For more information on finding your account's region, see [Account region](https://docs.logz.io/user-guide/accounts/account-region.html) . |         Required |
| LOGZIO_SHIPPING_KEY  | The [token](https://app.logz.io/#/dashboard/settings/general) of the account you want to ship to.                                                                                                                                                                                                                                 |         Required |
| WEBDAV_USERNAME      | Username for you webDav server                                                                                                                                                                                                                                                                                                    |         Required |
| WEBDAV_PASSWORD      | Password for you webDav server                                                                                                                                                                                                                                                                                                    |         Required |
| SEND_HISTORICAL_LOGS | If you need to send previous period of the time                                                                                                                                                                                                                                                                                   |            False |
| SEND_UNPARSE_LOGS    | Send logs that can't be parsed and don't exist time                                                                                                                                                                                                                                                                               |            False |
| WEBDAV_DIR_LINK      | logz listener                                                                                                                                                                                                                                                                                                                     |         Required |
| WEBDAV_DIR           | Directory where is your host your log files                                                                                                                                                                                                                                                                                       |              YES |
| GROK_PATTERNS        | Array where you can store Grok patterns based on this fetcher will parse your logs                                                                                                                                                                                                                                                |               [] |

## Usage

## Check Logz.io for your logs

Give your logs some time to get from your system to ours, and then open Kibana.

If you still don’t see your logs, see log shipping troubleshooting.

## License

logz.io for WebDav is licensed under the [MIT](https://github.com/logzio/webdav-fetcher/blob/master/LICENSE) License.
