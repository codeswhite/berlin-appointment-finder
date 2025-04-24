# Berlin BurgerSucher Bot

A bot that checks for available appointments at the Burgeramt in Berlin.
Notifies you via Telegram when an appointment is available.

## Running with Docker

1. Copy the `.env.example` file to `.env` and fill in the required values
2. Run the following command:

```bash
docker compose up -d
```
or manually:

```bash
docker build -t berlin-burgersucher .
docker run -d --env-file .env --name berlin-burgersucher berlin-burgersucher
```

## Running without Docker

1. Copy the `.env.example` file to `.env` and fill in the required values
2. Run the following command:

```bash
python src/berlin_burgersucher.py
```

### License

MIT License

### Author

Max Grinberg
