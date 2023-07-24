# OpenSearch set-up

- Doc: https://opensearch.org/docs/latest/install-and-configure/install-opensearch/rpm/

## Install OpenSearch and OpenSearch Dashboard

Create a local repository file for OpenSearch at `/etc/yum.repos.d/opensearch-2.x.repo`.

```shell
$ sudo curl -SL https://artifacts.opensearch.org/releases/bundle/opensearch/2.x/opensearch-2.x.repo -o /etc/yum.repos.d/opensearch-2.x.repo
```

Clean the YUM cache to ensure a smooth installation.

```shell
$ sudo yum clean all
```

Verify that the repository was created successfully.

```shell
$ sudo yum repolist
```

With the repository file downloaded, list all available versions of OpenSearch using the command `yum list`.

```shell
$ sudo yum list opensearch --showduplicates
```

Install the latest version of OpenSearch by default.

```shell
$ sudo yum install opensearch
```

During installation, the installer will present the GPG key fingerprint. Verify that the information matches the following:

```shell
Fingerprint: c5b7 4989 65ef d1c2 924b a9d5 39d3 1987 9310 d3fc
```

Once complete, run OpenSearch and verify that the service launched correctly.

```shell
$ sudo systemctl start opensearch
$ sudo systemctl status opensearch
```

## Test OpenSearch installation

With the OpenSearch service running, send a request to port 9200.

```shell
$ curl -X GET https://localhost:9200 -u 'admin:admin' --insecure
```

The response should look like this:

```json
{
    "name" : "hostname",
    "cluster_name" : "opensearch",
    "cluster_uuid" : "6XNc9m2gTUSIoKDqJit0PA",
    "version" : {
       "distribution" : "opensearch",
       "number" : <version>,
       "build_type" : <build-type>,
       "build_hash" : <build-hash>,
       "build_date" : <build-date>,
       "build_snapshot" : false,
       "lucene_version" : <lucene-version>,
       "minimum_wire_compatibility_version" : "7.10.0",
       "minimum_index_compatibility_version" : "7.0.0"
    },
    "tagline" : "The OpenSearch Project: https://opensearch.org/"
 }
```

Query the plugins endpoint.

```shell
$ curl -X GET https://localhost:9200/_cat/plugins?v -u 'admin:admin' --insecure
```

The response should look like this:

```
 name     component                            version
 hostname opensearch-alerting                  2.8.0
 hostname opensearch-anomaly-detection         2.8.0
 hostname opensearch-asynchronous-search       2.8.0
 hostname opensearch-cross-cluster-replication 2.8.0
 hostname opensearch-index-management          2.8.0
 hostname opensearch-job-scheduler             2.8.0
 hostname opensearch-knn                       2.8.0
 hostname opensearch-ml                        2.8.0
 hostname opensearch-notifications             2.8.0
 hostname opensearch-notifications-core        2.8.0
 hostname opensearch-observability             2.8.0
 hostname opensearch-performance-analyzer      2.8.0
 hostname opensearch-reports-scheduler         2.8.0
 hostname opensearch-security                  2.8.0
 hostname opensearch-sql                       2.8.0
```

## Install OpenSearch Dashboard

Create a local repository file for OpenSearch Dashboard at `/etc/yum.repos.d/opensearch-dashboards-2.x.repo`.

```shell
$ sudo curl -SL https://artifacts.opensearch.org/releases/bundle/opensearch-dashboards/2.x/opensearch-dashboards-2.x.repo -o /etc/yum.repos.d/opensearch-dashboards-2.x.repo
```

Verify that the repository was created successfully.

```shell
$ sudo yum repolist
```

Clean the YUM cache to ensure a smooth installation.

```shell
$ sudo yum clean all
```

With the repository file downloaded, list all available versions of OpenSearch using the command `yum list`.

```shell
$ sudo yum list opensearch-dashboards --showduplicates
```

Install the latest version of OpenSearch by default.

```shell
$ sudo yum install opensearch-dashboards
```

During installation, the installer will present the GPG key fingerprint. Verify that the information matches the following:

```shell
Fingerprint: c5b7 4989 65ef d1c2 924b a9d5 39d3 1987 9310 d3fc
```

Once complete, run OpenSearch Dashboards.

```shell
$  sudo systemctl start opensearch-dashboards
```

## Configure OpenSearch

https://opensearch.org/docs/latest/install-and-configure/install-opensearch/rpm/#step-3-set-up-opensearch-in-your-environment


## Configure OpenSearch Dashboard

https://opensearch.org/docs/latest/install-and-configure/install-dashboards/rpm/

Test connection to OpenSearch dashboards at [`http://localhost:5601`](http://localhost:5601).

## Test connection

Update the configuration hard-coded in the `test.py` script.

```python
host = "localhost"
port = 9200
auth = ("admin", "admin")  # For testing only. Don't store credentials in code.
```

With the `chatgpt-db` environment activated and the OpenSearch service running, call the test script.

```shell
$ python test.py
```

The test script should (1) connect to the database, (2) create an index 'test', (3) insert 20 documents in the index, (4) export the contents of the index to a file `./export.json`.
