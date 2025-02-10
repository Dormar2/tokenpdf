from functools import lru_cache

try:
    import rembg
    import onnxruntime as ort
except ImportError:
    rembg = None
    ort = None

@lru_cache
def onnx_provider_names() -> dict:
    def find_provider(p):
        for provider in ort.get_available_providers():
            if p.lower() in provider.lower():
                return provider
        return None
    res = {p: find_provider(p) for p in ["tensorrt", "cuda", "cpu"]}
    res = {k: v for k, v in res.items() if v is not None}
    return res

@lru_cache
def can_use_rembg(provider=None) -> bool:
    """ Check if the rembg package can be used with the specified provider
        or at all. Provider is shorthand: "cpu", "cuda", "tensorrt" or "gpu"."""
    session = get_session(provider)
    return session is not None

def _init__rembg_sessions():
    global _rembg_sessions
    if "_rembg_sessions" not in globals():
        _rembg_sessions = {}

@lru_cache
def _get_onnx_session(rawname: str):
    """ We cache the sessions to avoid creating a new session for each image.
        The cache is per provider """
    global _rembg_sessions
    _init__rembg_sessions()
    if not rembg:
        return None
    if rawname in _rembg_sessions:
        return _rembg_sessions[rawname]
    try:
        session = rembg.new_session(providers=[rawname])
        _rembg_sessions[rawname] = session
        return session
    except Exception:
        return None
    

@lru_cache
def get_session(provider:str|None = None):
    names = onnx_provider_names()
    providers = []
    if provider is not None:
        if provider == "gpu":
            providers.extend([names["cuda"], names["tensorrt"]])
        elif provider not in names:
            return None
        else:
            providers.append(names[provider])
    else:
        providers.extend(names.values())
    for p in providers:
        session = _get_onnx_session(p)
        if session is not None:
            return session
    return None
        


def rembg_remove(*args, provider:str|None=None, **kw):
    if ort is not None:
        ort.set_default_logger_severity(4)
    if not rembg:
        raise ImportError("The rembg package is not installed")
    if not can_use_rembg(provider):
        raise RuntimeError(f"Could not create a rembg session with provider {provider}")
    return rembg.remove(*args, session=get_session(provider), **kw)

rembg_remove.__doc__ = rembg.remove.__doc__