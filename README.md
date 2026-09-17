# ai-full-stack-weather-tool

```bash
pip install -r requirements.txt
python -c 'from weather import get_weather; print(get_weather("Shanghai", "tomorrow"))'
python test_weather.py
```

`get_weather(city, day="today")` supports `today`, `tomorrow`, and
`day_after_tomorrow`. It returns max/min temperature (°C), precipitation (mm),
weather condition, and umbrella advice, or `{"error": "..."}` on failure.

## Chat agent

Copy `.env.example` to `.env`, add your Anthropic API key, then run:

```bash
python agent.py
```
