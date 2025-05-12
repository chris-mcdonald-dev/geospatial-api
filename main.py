from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from app.routes import router

speed_file = "datasets/duval_jan1_2024.parquet.gz"
links_file = "datasets/link_info.parquet.gz"
# df = pd.read_parquet(links_file)
# pd.set_option('display.max_rows', 1000)
# pd.set_option('display.max_columns', 1000)
# pd.set_option('display.width', 1000)
# pd.set_option('display.max_colwidth', None)
# print(df.columns)

app = FastAPI()
origins = [
    "*",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/")
async def root():
    return {"message": "App is working!"}

