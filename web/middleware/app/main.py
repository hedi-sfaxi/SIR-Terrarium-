import uvicorn
from fastapi import FastAPI, HTTPException
from influxdb import InfluxDBClient
from analysis import correlation, ruptures
from sensor_node import irrigate


app = FastAPI()
influxDbClient = InfluxDBClient(host='influxdb', port=8086)
AUTHORIZED_COLUMNS = ['temperature', 'humidity', 'light', 'moisture', 'pH']

@app.get("/")
def get_root():
    return {"message": "Welcome to the middleware server! got to /docs to see the API documentation"}

@app.get("/columns")	
def get_authorized_columns():
    return {"columns": AUTHORIZED_COLUMNS}

@app.get("/irrigate")
def get_irrigate():
    # send irrigation control to the mqtt broker via Node-Red
    irrigate()
    return {"message": "The plants are being irrigated!"}

@app.get("/ruptures")
def get_rupture():
    # launch rupture analysis
    ruptures(influxDbClient, AUTHORIZED_COLUMNS)

    return {"message": "Rupture analysis completed"}

@app.get("/correlation")
def get_correlation(param1 : str, param2 : str):
    # raise and error if the param is not authorized
    for param in [param1, param2]:
        if param not in AUTHORIZED_COLUMNS:
            raise HTTPException(status_code=401, detail="Unauthorized column")
    
    # launch correlation analysis
    correlation(influxDbClient, param1, param2)

    return {"message": "Correlation analysis completed"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8082, reload=True)