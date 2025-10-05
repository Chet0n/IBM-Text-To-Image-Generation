from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
import os, time, base64
from diffusers import StableDiffusionPipeline
import torch

app = FastAPI()

# GPU setup
device = "cuda" if torch.cuda.is_available() else "cpu"
pipe = StableDiffusionPipeline.from_pretrained(uu
    "runwayml/stable-diffusion-v1-5",
    torch_dtype=torch.float16
).to(device)
pipe.enable_attention_slicing()

os.makedirs("outputs", exist_ok=True)

# Templates
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/generate")
async def generate(prompt: str = Form(...)):
    start_time = time.time()
    image = pipe(prompt, height=512, width=512, num_inference_steps=50, guidance_scale=7.5).images[0]
    filename = f"outputs/generated_{int(time.time())}.png"
    image.save(filename)
    with open(filename, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")
    return {"image_base64": encoded, "time_taken": round(time.time()-start_time, 2)}
