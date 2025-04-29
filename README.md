# Berlin BurgerSucher Bot

A bot that checks for available appointments at the Burgeramt in Berlin.
Notifies you via Telegram when an appointment is available.

### Inspiration

This project was inspired (and based on) by [Nicolas Bouliane - Burgeramt Experiment](https://nicolasbouliane.com/blog/berlin-buergeramt-experiment)
E.g.:
![Chances of finding an appointment to the Burgeramt, by time of day](https://nicolasbouliane.com/images/appointment-availability.png)

## Usage

### Running with Docker

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

### Running without Docker

1. Copy the `.env.example` file to `.env` and fill in the required values
2. Run the following command:

```bash
python -m src
```

## Plans and Todos
- Booking link should point to the month of the appointment.
- Make an autonomous telegram bot for this.
- Add support for Burgeramts in different cities.
- Add support for other languages?

### License

MIT License

### Credits

- [Max Grinberg](https://blog.maxcode.me)
- [Nicolas Bouliane](https://nicolasbouliane.com/)
