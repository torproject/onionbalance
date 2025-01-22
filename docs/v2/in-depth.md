# Onionbalance In-depth Tutorial (v2)

!!! warning

    This section refers to the old v2 codebase, which was removed from recent
    releases.
    Although outdated, this documentation is still available for historic
    purposes.

This is a step-by-step tutorial to help you configure Onionbalance for
v2 onions.

Onionbalance implements `round-robin` like load balancing on
top of Tor onion services. A typical Onionbalance deployment will
incorporate one management servers and multiple backend application
servers.

## Assumptions

You want to run:

* one or more Onionbalance processes, to perform load balancing, on hosts named
  `obhost1`, `obhost2`.
* two or more Tor processes, to run the Onion Services, on hosts named
  `torhost1`, `torhost2`.
* two or more servers (e.g. web servers) or traditional load balancers on hosts
  named `webserver1`, `webserver2`.

Scaling up:

* the number of `obhostX` can be increased but this will not help handling more
  traffic.
* the number of `torhostX` can be increased up to 60 instances to handle more
  traffic.
* the number of `webserverX` can be increased to handle more traffic until the
  Tor daemons in front of them become the bottleneck.

Scaling down:

* the three type of services can be run on the same hosts. The number of hosts
  can scale down to one.

Reliability:

Contrarily to traditional load balancers, the Onionbalance daemon does
not receive and forward traffic. As such, `obhostX` does not need to be
in proximity to `torhostX` and can be run from any location on the
Internet. Failure of `obhostX` will not affect the service as long as
either one `obhost` is still up or or the failure is shorter than 30
minutes.

Other assumptions:

* the hosts run Debian or Ubuntu
* there is no previous configuration

### Configuring the Onionbalance host

On `obhost1`:

```bash
sudo apt-get install onionbalance tor
mkdir -p /var/run/onionbalance
chown onionbalance:onionbalance /var/run/onionbalance
/usr/sbin/onionbalance-config -n <number_of_torhostX> --service-virtual-port <port> \
    --service-target <ipaddr:port>  --output ~/onionbalance_master_conf
sudo cp ~/onionbalance_master_conf/master/*.key /etc/onionbalance/
sudo cp ~/onionbalance_master_conf/master/config.yaml /etc/onionbalance/
sudo chown onionbalance:onionbalance /etc/onionbalance/*.key
sudo service onionbalance restart
sudo tail -f /var/log/onionbalance/log
```

Back up the files in `~/onionbalance_master_conf`.

If you have other `obhostX`:

```bash
sudo apt-get install onionbalance
mkdir -p /var/run/onionbalance
chown onionbalance:onionbalance /var/run/onionbalance
```

Copy `/etc/onionbalance/\*.key` and `/etc/onionbalance/config.yml` from
`obhost1` to all hosts in `obhostX`.

Check the logs. The following warnings are expected:

    Error generating descriptor: No introduction points for service

### Configuring the Tor services

Copy the `instance_torrc` and `private_key` files from each of the
directories named `./config/srv1`, `./config/srv2`,.. on `obhost1` to
`torhostX` - the contents of one directory for each `torhostX`.

Configure and start the services - the onion service on Onionbalance
should be ready within 10 minutes.

### Monitoring

On each `obhostX`, run:

```bash
sudo watch 'socat - unix-connect:/var/run/onionbalance/control'
```
