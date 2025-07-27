# Slothtop Assistant
**Project isn't ready yet!!!**

This is the project of AI assistant Slothtop. This assistant can work with your PC: open apps, turn off your PC, reload it, search the web for some information (Tavily API required).
In the future new tools will be added.
If you want, you can take and use this project as a template for your own AI assistants.

## How to run this project localy

Clone the project

```bash
  git clone https://github.com/Lalka00pq/Slothtop-assistant
```

Go to the project directory

```bash
  cd slothtop-assistant
```
Create the `.env` file with the following content
```env
TAVILY_API_KEY=your-api-key
```

Install dependencies (using pip or uv package manager)

```bash
  pip install requirements.txt
```
------
Using uv sync
```bash
uv sync 
```
------
Using uv add pyproject.toml
```bash
uv add pyproject.toml
```
Run the App
```bash
  python app.py
```
or 
```bash
    uv run app.py
```

