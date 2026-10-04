import sys, json, time, torch
from diffusers import AutoPipelineForText2Image
torch.set_num_threads(8)
jobs = json.load(open(sys.argv[1]))
pipe = AutoPipelineForText2Image.from_pretrained("stabilityai/sd-turbo", torch_dtype=torch.float32)
pipe.set_progress_bar_config(disable=True)
for j in jobs:
    for k in range(j.get('n', 1)):
        t = time.time(); g = torch.Generator().manual_seed(j.get('seed', 1) + k)
        im = pipe(prompt=j['prompt'], negative_prompt=None, num_inference_steps=j.get('steps', 3), guidance_scale=0.0, width=j.get('w', 512), height=j.get('h', 512), generator=g).images[0]
        out = f"out/{j['name']}_{k}.png"; im.save(out); print(out, round(time.time() - t, 1), flush=True)
