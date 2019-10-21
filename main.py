import os
from snaky.bot import client
from dotenv import load_dotenv

if __name__ == "__main__":
    load_dotenv()
    client.run(os.getenv("TOKEN"))
