# Cloud Sync Server

A minimal web server built with FastAPI, providing cloud sync capabilities for the [Female Gender Mod].

>[!important]
> If you are a user, **you do not need to install this!** The mod already ships with its own default cloud sync server,
> which does not require any additional configuration to use.
>
> This server is provided to allow for other developers to contribute to it, as well as a reference for anyone
> that may wish to reimplement the APIs it provides for their own purposes.

## Running your own

This server has the following prerequisite requirements to run:

- A MongoDB server with replication support enabled
  - [MongoDB Atlas](https://www.mongodb.com/atlas) provides free databases with up to 512 MB of storage
- Python 3.10 through 3.13
- [Poetry](https://python-poetry.org/)

```sh
git clone https://github.com/FemaleGenderMod/cloud-sync-server.git
cd wfgm-sync-server
poetry install --only main
poetry run fastapi run
```

Afterward, override the default `cloud_server` in `config/wildfire_gender.json` to point to your server,
such as `https://wfgm.example.com`.

>[!important]
> There are known issues with the mod not properly connecting to cloud sync servers not running over HTTPS;
> this issue is automatically worked around in a development environment where relevant, but production
> deployments are expected to always be running over HTTPS.

[Female Gender Mod]: https://github.com/WildfireRomeo/WildfireFemaleGenderMod
