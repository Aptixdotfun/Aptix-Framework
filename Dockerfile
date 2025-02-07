FROM python:3.10-slim
WORKDIR /AptixBot

COPY . /AptixBot/

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    python3-dev \
    libffi-dev \
    libssl-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN python -m pip install -r requirements.txt

EXPOSE 6185 
EXPOSE 6186

CMD [ "python", "main.py" ]
