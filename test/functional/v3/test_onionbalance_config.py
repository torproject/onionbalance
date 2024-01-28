# -*- coding: utf-8 -*-
"""
Functional tests which run the onionbalance-config tool and check
the created output files.
"""
import sys

import pexpect


def onionbalance_config_interact(cli, cli_input):
    """
    Send each input line to the onionbalance-config CLI interface
    """
    cli.expect("store generated config")
    cli.send("{}\n".format(cli_input.get("config_dir", "")))

    cli.expect("Number of services")
    cli.send("1\n")

    cli.expect("path to master service private key")
    cli.send("{}\n".format(cli_input.get("private_key_path", "")))

    cli.expect("Number of instance services")
    cli.send("{}\n".format(cli_input.get("num_instances", "")))

    cli.expect("Provide a tag name")
    cli.send("{}\n".format(cli_input.get("tag_name", "")))


def check_basic_config_output(config_dir):
    """
    Run basic tests on the generated config files and keys to check
    that they look reasonable.
    """

    assert len(config_dir.listdir()) == 2

    # Find generated instance addresses
    instance_addresses = []
    for fn in config_dir.listdir():
        if not fn.isfile():
            continue
        if not fn.basename.endswith(".key"):
            continue
        instance_addresses.append(fn.basename[:-4])

    # Correct number of directories created
    assert len(config_dir.listdir()) == 2

    cfp = config_dir.join("config.yaml")
    assert cfp.check()
    conf = cfp.read_text("utf-8")
    assert all(address in conf for address in instance_addresses)


def test_onionbalance_config_interactive(tmpdir):
    """
    Functional test to run onion-balance config in interactive mode.
    """
    # Start onionbalance-config in interactive mode (no command line arguments)
    cli = pexpect.spawnu("onionbalance-config", logfile=sys.stdout)
    cli.expect("entering interactive mode")

    # Interact with the running onionbalance-config process
    onionbalance_config_interact(
        cli, cli_input={"config_dir": str(tmpdir.join("configdir"))}
    )
    cli.expect("Done! Successfully generated")

    check_basic_config_output(tmpdir.join("configdir"))


def test_onionbalance_config_automatic(tmpdir):
    """
    Functional test to run onion-balance config in automatic mode.
    """
    # Start onionbalance-config in automatic mode
    cli = pexpect.spawnu(
        "onionbalance-config",
        logfile=sys.stdout,
        args=[
            "--output",
            str(tmpdir.join("configdir")),
        ],
    )
    cli.expect("Done! Successfully generated")

    check_basic_config_output(tmpdir.join("configdir"))
