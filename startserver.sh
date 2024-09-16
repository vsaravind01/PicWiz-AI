export SECRET_KEY='secret'
export ALGORITHM='HS256'
export COHERE_API_KEY=uK9Jk6MRaFj7Fy7fPFGr41NZHRnUFm1xIvawkt8N

uvicorn main:app --reload --host 0.0.0.0 --port 8080 --log-level debug