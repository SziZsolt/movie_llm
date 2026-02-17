from fastapi import FastAPI
from pydantic import BaseModel
from MovieModel import MovieModel
from Retrieval import Retrieval
from MovieDatabase import MovieDatabase

app = FastAPI(title="Movie LLM API")

class QueryRequest(BaseModel):
    query: str

@app.post("/chat")
def chat(request: QueryRequest):
    movie_database = MovieDatabase()
    retrieval = Retrieval(movie_database)
    movie_model = MovieModel(retrieval, "meta-llama/Llama-2-7b-hf")
    generated_answer = movie_model.generate_answer(request.query)
    return {"response": generated_answer}