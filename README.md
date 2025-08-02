# wfgm-sync-server

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
  - [MongoDB Atlas](https://www.mongodb.com/atlas) provides free databases with up to 512 MB of storage; I personally don't recommend
    this for a production deployment due to previous experiences around the stability of it, but this may still be suitable enough for
    local development, or small-scale deployments for a small group of friends/a private server.
- Python 3.10 or newer
- [Poetry](https://python-poetry.org/)

```sh
git clone https://codeberg.org/celestialfault/wfgm-sync-server.git
cd wfgm-sync-server
poetry install --only main
poetry run fastapi run
```

Afterward, override the default `cloud_server` in `config/wildfire_gender.json` to point to your server,
such as `https://wfgm.example.com`.

Note that there is a known issue where the mod will fail to send the player's data to the server if it isn't running over
HTTPS; this issue is automatically worked around if you're in a development environment (to allow for local development),
but this otherwise effectively forces an HTTPS requirement for any kind of production deployment (which you should already
be doing to begin with).

[Female Gender Mod]: https://github.com/WildfireRomeo/WildfireFemaleGenderMod
