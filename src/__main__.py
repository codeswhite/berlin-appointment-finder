from src.telegram import TelegramModule

if __name__ == "__main__":
    try:
        TelegramModule().run()
    except KeyboardInterrupt:
        print("Stopped.")
