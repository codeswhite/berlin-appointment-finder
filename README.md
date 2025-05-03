# Berlin Bürgeramt Telegram Bot (unofficial)

A Telegram bot that notifies you when new appointments are available at the Bürgeramt in Berlin.

You can specify your preferred date (or date range).

Try it out: 👉🏼 https://t.me/BerlinAppointmentFinderBot 👈🏼

### Inspiration

This project is based on the work done by [Nicolas Bouliane](https://nicolasbouliane.com/) - The author of [All About Berlin](https://allaboutberlin.com/).

I recommend checking out his blog post about this:  
[Nicolas Bouliane - Bürgeramt Experiment](https://nicolasbouliane.com/blog/berlin-buergeramt-experiment).

Cool insight from the blog:
![Chances of finding an appointment to the Bürgeramt, by time of day](https://nicolasbouliane.com/images/content2x/appointment-availability.webp)

### How it works?

1. The bot subscribes to the Websocket at `wss://allaboutberlin.com/api/appointments` (source: https://github.com/All-About-Berlin/burgeramt-appointments)
2. When the bot receives a new set of appointments from the ws, it checks if any of them are in the preferred date range for any user.
3. If appointments are found, the bot sends a message to the user.

## Running

### Running with Docker

First copy the `.env.example` file to `.env` and fill in the required values.

#### With Compose

```bash
docker compose up -d
```
#### Without Compose

```bash
docker build -t berlin-appointment-finder .
docker run -d --env-file .env --name berlin-appointment-finder berlin-appointment-finder
```

### Local development

1. Copy the `.env.example` file to `.env` and fill in the required values
2. Run the following commands:

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python -m src
```

## Plans and Todos
- Add support for Burgeramts in different cities.
- Add support for other languages?
- Booking link should point to the month of the appointment.
- Add support for running a local instance of [the scrapper](https://github.com/All-About-Berlin/burgeramt-appointments) instead of using the remote one (maybe create an alternative compose.yml).

### License

MIT License

### Credits

- Max Grinberg - https://maxcode.me
- Nicolas Bouliane - https://nicolasbouliane.com/
