ChatterChum
===========

ChatterChum is an end to end AI-powered photo management tool similar to Google Photos from scratch which is capable of automatically tagging photos based on objects, recognize familiar faces, and also generate an album based on a user requirement.

## Features
- [ ] **Entity Detection**: Automatically tag photos based on people, objects, and places.
- [ ] **Cluster Photos**: Group photos based on the similarity of objects, people, and places.
- [ ] **Search Photos**: Search photos based on tags, people, and places using natural language.

## Setup
1. Clone the repository
```bash
git clone https://github.com/vsaravind01/ChatterChum.git
```
2. Install the dependencies
```bash
pip install -r requirements.txt
```

## Usage
1. Run the application
```bash
python app.py
```
or
```bash
uvicorn app:app --reload --port 8000 --host 0.0.0.0
```