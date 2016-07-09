# The Point Church Website #

This is a Django project designed to be deployed to an Amazon EC2 instance running Debian (wheezy or jessie), although this is not a requirement.

## Installation ##

### EC2 Instance ###

Generate `user-data` for the EC2 instance by running:

    HOST=<hostname> MAILHUB=<mailrelay> AUTHUSER=<mailuser> AUTHPASS=<mailpass> debian_release=[wheezy|jessie] make user-data

where you define:

* **hostname**: The name of the EC2 instance you are creating
* **mailrelay**: The hostname of the SMTP relay to use for host emails
* **mailuser** and **mailpass**: The credentials to access the SMTP relay

Note, Amazon SES servers are supported.

The `user-data` file will be gzipped, but not base64 encoded.

### Installing Project Instances ###

Separate instances of the project can be installed for different environments (production, testing, etc.). Each instance runs under a separate user account. A new account can be created by running on the EC2 host:

    sudo create_user.sh <username> <description> [environment]

You must provide a "username" and "description". If not specified, the environment will be "production".

This will set up an empty git repository that can be accessed using the same SSH key used to access the EC2 instance. This repository will manage the project instance.

Push the desired branch of the codebase to the project repository:

    git remote add <environment> <username>@<hostname>:git
    git push <environment> <branch>

This will then initialise the project and run it. You will need to manually reload the nginx configuration to complete the deployment.
