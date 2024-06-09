import copy
import math
from typing import Dict, List, Optional, Tuple, Union

from PIL import Image
import numpy as np
import torch
from torchvision import transforms
from einops import rearrange, repeat
from omegaconf import ListConfig, OmegaConf
from sgm.util import append_dims, default, instantiate_from_config
from safetensors.torch import load_file as load_safetensors
from generative_models.scripts.util.detection.nsfw_and_watermark_dectection import DeepFloydDataFiltering

VERSION2SPECS = {
    "SDXL-base-1.0": {
        "H": 1024,
        "W": 1024,
        "C": 4,
        "f": 8,
        "is_legacy": False,
        "config": "configs/inference/sd_xl_base.yaml",
        "ckpt": "checkpoints/sd_xl_base_1.0.safetensors",
    },
    "SDXL-refiner-1.0": {
        "H": 1024,
        "W": 1024,
        "C": 4,
        "f": 8,
        "is_legacy": True,
        "config": "configs/inference/sd_xl_refiner.yaml",
        "ckpt": "checkpoints/sd_xl_refiner_1.0.safetensors",
    },
}

def load_img(img_path):
    """
    Load image from path.

    Args:
        img_path (str): Path to image file.

    Returns:
        torch.Tensor: A processed image tensor ready for model inference.
    """
    img = Image.open(img_path)
    
    w, h = img.size
    width, height = map(
        lambda x: x - x % 64, (w, h)
    )  # resize to integer multiple of 64
    img = img.resize((width, height))
    
    img = np.array(img.convert("RGB"))
    img = img[None].transpose(0, 3, 1, 2)
    img = torch.from_numpy(img).to(dtype=torch.float32) / 127.5 - 1.0
    return img.to("cuda")


def load_img_for_pool(img_path = None, size = None, center_crop = False,
):
    if (img_path is None):
        return None
    image = Image.open(img_path).convert("RGB")

    transform = []
    if size is not None:
        transform.append(transforms.Resize(size))
    if center_crop:
        transform.append(transforms.CenterCrop(size))
    transform.append(transforms.ToTensor())
    transform.append(transforms.Lambda(lambda x: 2.0 * x - 1.0))

    transform = transforms.Compose(transform)
    img = transform(image)[None, ...]
    return img


def load_model_from_config(config, ckpt):
    """
    Load model from config and checkpoint.

    Args:
        config (DictConfig): Configuration object for the model.
        ckpt (str): Path to the checkpoint file, expected to end with 'safetensors'.
        
    Returns:
        torch.nn.Module: The loaded and prepared model
    """
    torch.cuda.empty_cache()
    
    model = instantiate_from_config(config.model)
    if (ckpt.endswith("safetensors")):
        sd = load_safetensors(ckpt)
    else:
        raise ValueError("Checkpoint path is not vaild. Expected a '.safetensors' file.")
    
    if model:
        m, u = model.load_state_dict(sd, strict=False)

        if len(m) > 0:
            print("missing keys:")
            print(m)
        if len(u) > 0:
            print("unexpected keys:")
            print(u)
        
        model.half()
        model.eval()
    else:
        raise RuntimeError("Model can't be loaded.")
    
    return model


def load_model(model):
    """
    Load model to GPU.

    Args:
        model (torch.nn.Module): Model to activate.
    """
    model.cuda()
    
    
def unload_model(model):
    """
    Unload model from GPU.

    Args:
        model (torch.nn.Module): Model to deactivate.
    """
    model.cpu()
    torch.cuda.empty_cache()
    

def init_state(version_dict):
    """
    Create state dictionary with version dictionary.

    Args:
        version_dict(dict): An element of VERSION2SPECS.
        
    Returns:
        dict: Dictionary containing state informations.
    """
    ckpt = version_dict["ckpt"]
    config = OmegaConf.load(version_dict["config"]) # create DictConfig instance
    model = load_model_from_config(config, ckpt)
    
    state = dict()
    state["model"] = model
    state["ckpt"] = ckpt
    state["config"] = config
    state["filter"] = DeepFloydDataFiltering(verbose=False)
    
    return state


def init_embedder_options(keys, init_dict, prompt="", negative_prompt=""):
    value_dict = {}
    for key in keys:
        if key == "txt":
            value_dict["prompt"] = prompt
            value_dict["negative_prompt"] = negative_prompt

        if key == "original_size_as_tuple":
            value_dict["orig_width"] = init_dict["orig_width"]
            value_dict["orig_height"] = init_dict["orig_height"]

        if key == "crop_coords_top_left":
            value_dict["crop_coords_top"] = 0
            value_dict["crop_coords_left"] = 0

        if key == "aesthetic_score":
            value_dict["aesthetic_score"] = 6.0
            value_dict["negative_aesthetic_score"] = 2.5

        if key == "target_size_as_tuple":
            value_dict["target_width"] = init_dict["target_width"]
            value_dict["target_height"] = init_dict["target_height"]

        if key in ["fps_id", "fps"]:
            fps = 6

            value_dict["fps"] = fps
            value_dict["fps_id"] = fps - 1

        if key == "motion_bucket_id":
            value_dict["motion_bucket_id"] = 127

        if key == "pool_image":
            image = load_img_for_pool(size=224,center_crop=True) # to be modified
            if image is None:
                image = torch.zeros(1, 3, 224, 224)
            value_dict["pool_image"] = image

    return value_dict


def get_batch(
    keys,
    value_dict: dict,
    N: Union[List, ListConfig],
    device: str = "cuda",
    T: Optional[int] = None,
    additional_batch_uc_fields: List[str] = [],
):

    batch = {}
    batch_uc = {}

    for key in keys:
        if key == "txt":
            batch["txt"] = [value_dict["prompt"]] * math.prod(N)

            batch_uc["txt"] = [value_dict["negative_prompt"]] * math.prod(N)

        elif key == "original_size_as_tuple":
            batch["original_size_as_tuple"] = (
                torch.tensor([value_dict["orig_height"], value_dict["orig_width"]])
                .to(device)
                .repeat(math.prod(N), 1)
            )
        elif key == "crop_coords_top_left":
            batch["crop_coords_top_left"] = (
                torch.tensor(
                    [value_dict["crop_coords_top"], value_dict["crop_coords_left"]]
                )
                .to(device)
                .repeat(math.prod(N), 1)
            )
        elif key == "aesthetic_score":
            batch["aesthetic_score"] = (
                torch.tensor([value_dict["aesthetic_score"]])
                .to(device)
                .repeat(math.prod(N), 1)
            )
            batch_uc["aesthetic_score"] = (
                torch.tensor([value_dict["negative_aesthetic_score"]])
                .to(device)
                .repeat(math.prod(N), 1)
            )

        elif key == "target_size_as_tuple":
            batch["target_size_as_tuple"] = (
                torch.tensor([value_dict["target_height"], value_dict["target_width"]])
                .to(device)
                .repeat(math.prod(N), 1)
            )
        elif key == "fps":
            batch[key] = (
                torch.tensor([value_dict["fps"]]).to(device).repeat(math.prod(N))
            )
        elif key == "fps_id":
            batch[key] = (
                torch.tensor([value_dict["fps_id"]]).to(device).repeat(math.prod(N))
            )
        elif key == "motion_bucket_id":
            batch[key] = (
                torch.tensor([value_dict["motion_bucket_id"]])
                .to(device)
                .repeat(math.prod(N))
            )
        elif key == "pool_image":
            batch[key] = repeat(value_dict[key], "1 ... -> b ...", b=math.prod(N)).to(
                device, dtype=torch.half
            )
        elif key == "cond_aug":
            batch[key] = repeat(
                torch.tensor([value_dict["cond_aug"]]).to("cuda"),
                "1 -> b",
                b=math.prod(N),
            )
        elif key == "cond_frames":
            batch[key] = repeat(value_dict["cond_frames"], "1 ... -> b ...", b=N[0])
        elif key == "cond_frames_without_noise":
            batch[key] = repeat(
                value_dict["cond_frames_without_noise"], "1 ... -> b ...", b=N[0]
            )
        elif key == "polars_rad":
            batch[key] = torch.tensor(value_dict["polars_rad"]).to(device).repeat(N[0])
        elif key == "azimuths_rad":
            batch[key] = (
                torch.tensor(value_dict["azimuths_rad"]).to(device).repeat(N[0])
            )
        else:
            batch[key] = value_dict[key]

    if T is not None:
        batch["num_video_frames"] = T

    for key in batch.keys():
        if key not in batch_uc and isinstance(batch[key], torch.Tensor):
            batch_uc[key] = torch.clone(batch[key])
        elif key in additional_batch_uc_fields and key not in batch_uc:
            batch_uc[key] = copy.copy(batch[key])
    return batch, batch_uc


def get_unique_embedder_keys_from_conditioner(conditioner):
    return list(set([x.input_key for x in conditioner.embedders]))


def init_sampling(
    key=1,
    img2img_strength: Optional[float] = None,
    specify_num_samples: bool = True,
    stage2strength: Optional[float] = None,
    options: Optional[Dict[str, int]] = None,
):
    options = {} if options is None else options

    num_rows, num_cols = 1, 1
    if specify_num_samples:
        num_cols = st.number_input(
            f"num cols #{key}", value=num_cols, min_value=1, max_value=10
        )

    steps = st.number_input(
        f"steps #{key}", value=options.get("num_steps", 50), min_value=1, max_value=1000
    )
    sampler = st.sidebar.selectbox(
        f"Sampler #{key}",
        [
            "EulerEDMSampler",
            "HeunEDMSampler",
            "EulerAncestralSampler",
            "DPMPP2SAncestralSampler",
            "DPMPP2MSampler",
            "LinearMultistepSampler",
        ],
        options.get("sampler", 0),
    )
    discretization = st.sidebar.selectbox(
        f"Discretization #{key}",
        [
            "LegacyDDPMDiscretization",
            "EDMDiscretization",
        ],
        options.get("discretization", 0),
    )

    discretization_config = get_discretization(discretization, options=options, key=key)

    guider_config = get_guider(options=options, key=key)

    sampler = get_sampler(sampler, steps, discretization_config, guider_config, key=key)
    if img2img_strength is not None:
        st.warning(
            f"Wrapping {sampler.__class__.__name__} with Img2ImgDiscretizationWrapper"
        )
        sampler.discretization = Img2ImgDiscretizationWrapper(
            sampler.discretization, strength=img2img_strength
        )
    if stage2strength is not None:
        sampler.discretization = Txt2NoisyDiscretizationWrapper(
            sampler.discretization, strength=stage2strength, original_steps=steps
        )
    return sampler, num_rows, num_cols


@torch.no_grad()
def do_img2img(
    img,
    model,
    sampler,
    value_dict,
    num_samples,
    force_uc_zero_embeddings: Optional[List] = None,
    force_cond_zero_embeddings: Optional[List] = None,
    additional_kwargs={},
    offset_noise_level: float = 0.0,
    return_latents=False,
    skip_encode=False,
    filter=None,
    add_noise=True,
):
    with torch.no_grad():
        with torch.autocast("cuda"):
            with model.ema_scope():
                load_model(model.conditioner)
                batch, batch_uc = get_batch(
                    get_unique_embedder_keys_from_conditioner(model.conditioner),
                    value_dict,
                    [num_samples],
                )
                c, uc = model.conditioner.get_unconditional_conditioning(
                    batch,
                    batch_uc=batch_uc,
                    force_uc_zero_embeddings=force_uc_zero_embeddings,
                    force_cond_zero_embeddings=force_cond_zero_embeddings,
                )
                unload_model(model.conditioner)
                for k in c:
                    c[k], uc[k] = map(lambda y: y[k][:num_samples].to("cuda"), (c, uc))

                for k in additional_kwargs:
                    c[k] = uc[k] = additional_kwargs[k]
                    
                if skip_encode:
                    z = img
                else:
                    load_model(model.first_stage_model)
                    z = model.encode_first_stage(img)
                    unload_model(model.first_stage_model)

                noise = torch.randn_like(z)

                sigmas = sampler.discretization(sampler.num_steps).cuda()
                sigma = sigmas[0]

                if offset_noise_level > 0.0:
                    noise = noise + offset_noise_level * append_dims(
                        torch.randn(z.shape[0], device=z.device), z.ndim
                    )
                if add_noise:
                    noised_z = z + noise * append_dims(sigma, z.ndim).cuda()
                    noised_z = noised_z / torch.sqrt(
                        1.0 + sigmas[0] ** 2.0
                    )  # Note: hardcoded to DDPM-like scaling. need to generalize later.
                else:
                    noised_z = z / torch.sqrt(1.0 + sigmas[0] ** 2.0)

                def denoiser(x, sigma, c):
                    return model.denoiser(model.model, x, sigma, c)

                load_model(model.denoiser)
                load_model(model.model)
                samples_z = sampler(denoiser, noised_z, cond=c, uc=uc)
                unload_model(model.model)
                unload_model(model.denoiser)

                load_model(model.first_stage_model)
                samples_x = model.decode_first_stage(samples_z)
                unload_model(model.first_stage_model)
                samples = torch.clamp((samples_x + 1.0) / 2.0, min=0.0, max=1.0)

                if filter is not None:
                    samples = filter(samples)

                if return_latents:
                    return samples, samples_z
                return samples


def run_img2img(
    state,
    version_dict,
    is_legacy=False,
    return_latents=False,
    filter=None,
    stage2strength=None,
):
    img = load_img('sample_image.png')
    
    H, W = img.shape[2], img.shape[3]

    init_dict = {
        "orig_width": W,
        "orig_height": H,
        "target_width": W,
        "target_height": H,
    }
    value_dict = init_embedder_options(
        get_unique_embedder_keys_from_conditioner(state["model"].conditioner),
        init_dict,
        prompt="", # to be modified
        negative_prompt="",
    )
    strength = 0.75
    sampler, num_rows, num_cols = init_sampling(
        img2img_strength=strength,
        stage2strength=stage2strength,
    )
    num_samples = num_rows * num_cols

    out = do_img2img(
        repeat(img, "1 ... -> n ...", n=num_samples),
        state["model"],
        sampler,
        value_dict,
        num_samples,
        force_uc_zero_embeddings=["txt"] if not is_legacy else [],
        return_latents=return_latents,
        filter=filter,
    )
    return out
    

if __name__ == "__main__":
    pass
