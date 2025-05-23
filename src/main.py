from fastapi import FastAPI

app = FastAPI()

@app.get("/process_data")
def process_geo_data(geo_data: list[int]):
    return
