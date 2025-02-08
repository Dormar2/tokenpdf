from __future__ import annotations
from pathlib import Path
import PIL.ImageFilter
from PIL import Image
import csv
import tempfile
from typing import Sequence, Tuple, Dict, Callable
from uuid import uuid4
import imagesize
import numpy as np
import PIL
import PIL.Image
import logging
import base64
from platformdirs import user_cache_dir
from wrapt import synchronized
from tokenpdf.utils.io import download_file
from tokenpdf.utils.image import join_mask_channel, find_background, mask_to_roi, force_roi_aspect_ratio
from tokenpdf.filters import apply_imagefilters


logger = logging.getLogger(__name__)
PossibleSource = str | Path | PIL.Image.Image | np.ndarray

IMAGE_CACHE = user_cache_dir("tokenpdf", "imaged2")
ENABLE_MAIN_IMAGE_CACHE = True
RESIZE_ALG = PIL.Image.Resampling.LANCZOS

class ImagePersistentCache:
    def __init__(self, folder: Path = IMAGE_CACHE, enabled:bool=False):
        self.folder = Path(folder)
        self.folder.mkdir(parents=True, exist_ok=True)
        self.index = {}
        self.enabled = False
        if enabled:
            self.enable()


    def enable(self):
        self.enabled = True
        self.load_index()
    def disable(self):
        self.enabled = False

    def get(self, key: str) -> FloatingImage:
        if not self.enabled:
            raise KeyError("Cache is disabled.")
        if key not in self.index:
            raise KeyError(f"Key {key} not found in cache.")
        return FloatingImage(self.folder / self.index[key])
    
    def has(self, key: str) -> bool:
        if not (self.enabled) or (key not in self.index):
            return False
        exists = (self.folder / self.index[key]).exists()
        if not exists:
            # Shouldn't get here normally
            # unless manually deleted
            self._remove(key)
        return exists
        
        
    @synchronized
    def _remove(self, key: str):
        if not self.enabled:
            return
        if key in self.index:
            path = self.folder / self.index[key]
            if path.exists():
                path.unlink()
            del self.index[key]
            self.save_index()
    
    @synchronized
    def new(self, key: str, default_suffix=".png") -> Path:
        if not self.enabled:
            raise KeyError("Cache is disabled.")
        if key in self.index and (self.folder / self.index[key]).exists():
            return self.folder / self.index[key]
        file_path = self.folder / f"{uuid4().hex[:8]}{default_suffix}"
        self.index[key] = file_path.name
        return file_path
    
    @synchronized
    def update_suffix(self, key: str, new_suffix: str):
        if not self.enabled or key not in self.index:
            return
        path = Path(self.index[key])
        new_path = path.with_suffix(new_suffix)
        if path.exists():
            path.rename(new_path)
        self.index[key] = new_path.name
        self.save_index()

    @synchronized
    def clear(self, key: str = None, update_index=True):
        if not self.enabled:
            return
        if key and key in self.index:
            path = Path(self.index[key])
            if path.exists():
                path.unlink()
            del self.index[key]
        elif not key:
            for k in list(self.index.keys()):
                self.clear(k, update_index=False)
        if update_index:
            self.save_index()

    @synchronized
    def _get_index(self)->Dict[str, str]:
        return self.index.copy()
    
    def save_index(self):
        index = self._get_index()
        index_path = self.folder / "index.csv"
        with open(index_path, "w") as f:
            writer = csv.writer(f)
            for key, value in index.items():
                writer.writerow([key, value])

    def __getitem__(self, key: str) -> FloatingImage:
        return self.get(key)


    @synchronized
    def load_index(self):
        logger.info(f"Loading image cache index from {self.folder}")
        index_path = self.folder / "index.csv"
        if index_path.exists():
            with open(index_path, "r") as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) >= 2:
                        self.index[row[0]] = row[1]
        self.resolve_references()

    @synchronized
    def resolve_references(self):
        while self._resolve_references_step():
            pass

    def _resolve_references_step(self):
        changed = False
        for key, value in self.index.items():
            if (('/' in value or '\\' in value or value.startswith("*"))
                and value in self.index):
                # This is a reference to another temporary file
                self.index[key] = self.index[value]
                changed = True
        return changed
                
main_image_cache = ImagePersistentCache(folder=IMAGE_CACHE, enabled=ENABLE_MAIN_IMAGE_CACHE)
    

class FloatingImage:
    """
    Represnts an image that can be in multiple places 
    (URL, path, memory) or formats, depending on need.
    """

    def __init__(self, *sources: Sequence[PossibleSource], default_suffix=".png", **kw):
        self._sources = {}
        self._default_suffix = default_suffix
        self._save_kw = kw
        self._temp_sources = []
        for source in sources:
            self.add_source(source)
    

    def add_source(self, source: PossibleSource):
        """
        Add a source to the floating image.
        """
        if isinstance(source, (str, Path)):
            if str(source).startswith("http"):
                self._sources["url"] = source
            else:
                self._sources["perm_path"] = source
        elif isinstance(source, PIL.Image.Image):
            self._sources["image"] = source
        elif isinstance(source, np.ndarray):
            self._sources["array"] = source
        else:
            raise ValueError(f"Invalid source type: {type(source)}")
    
    def as_pil(self) -> PIL.Image.Image:
        """
        Get the image as a PIL image.
        """
        if "image" in self._sources:
            return self._sources["image"]
        elif "array" in self._sources:
            return PIL.Image.fromarray(self._sources["array"])
        else:
            self._sources["image"] = (image := PIL.Image.open(self.as_path()))
            if image.mode not in ("RGB", "RGBA", "L"):
                self._sources["image"] = (image := image.convert("RGBA"))

            return image
            
    
    def as_path(self) -> Path:
        """
        Get the image as a path, downloading or writing to disk if necessary.
        """
        if "perm_path" in self._sources:
            return self._sources["perm_path"]
        elif "temp_path" in self._sources:
            return self._sources["temp_path"]
        elif "image" in self._sources or "array" in self._sources:
            self._save("temp_path")
            return self._sources["temp_path"]
        elif "url" in self._sources:
            self._sources["temp_path"] = self._download_to_temporary(self._sources["url"])
            return self._sources["temp_path"]
        else:
            raise ValueError("No valid source found.")
    
    def _download_to_temporary(self, url: str):
        temp_path = self._get_temp_path(url)
        actual_path = download_file(url, temp_path, allow_rename=True)
        if actual_path.suffix != temp_path.suffix and main_image_cache.enabled:
            main_image_cache.update_suffix(url, actual_path.suffix)
        return actual_path
            
    def flip(self, horz: bool = False, vert: bool = False) -> FloatingImage:
        if not horz and not vert:
            return self
        img = self.as_pil()
        if horz:
            img = img.transpose(PIL.Image.FLIP_LEFT_RIGHT)
        if vert:
            img = img.transpose(PIL.Image.FLIP_TOP_BOTTOM)
        return FloatingImage(img, default_suffix=self._default_suffix, **self._save_kw)

    def rotate(self, angle: float) -> FloatingImage:
        if angle == 0:
            return self
        return FloatingImage(self.as_pil().rotate(angle*np.pi/180, 
                                                  resample=RESIZE_ALG, expand=True),
                                                  default_suffix=self._default_suffix, 
                                                  **self._save_kw)

    def as_array(self) -> np.ndarray:
        """
        Get the image as a numpy array.
        """
        return np.asanyarray(self.as_pil())
    
    def as_floating_image(self) -> "FloatingImage":
        """
        Get the image as a FloatingImage.
        """
        return self
    
    def cleanup(self):
        """
        Clean up any temporary files.
        Object can still be used after this.
        """
        for source in self._temp_sources:
            self._sources[source].unlink()
            del self._sources[source]
        self._temp_sources = []

    def crop(self, roi: Tuple[int, int, int, int], zoom:bool=False) -> "FloatingImageWithROI" | "FloatingImage":
        """
        Return a FloatingImage representing the cropped area
        """
        if not zoom:
            return FloatingImageWithROI(self, roi)
        else:
            roif = force_roi_aspect_ratio(roi, self.dims)
            return FloatingImageWithROI(self, roif).resize(self.dims)
    
    @property
    def dims(self) -> Tuple[int, int]:
        if "image" in self._sources:
            return self._sources["image"].size
        elif "array" in self._sources:
            return self._sources["array"].shape[:2]
        else:
            return imagesize.get(self.as_path())

    def _get_temp_path(self, url: str|Path|None = None, suffix = None) -> Path:
        if suffix is None:
            suffix = self._default_suffix
        if url and main_image_cache.enabled:
            return main_image_cache.new(url, suffix)
        
        folder = Path(tempfile.gettempdir())
        path = folder / f"fi_{uuid4().hex[:8]}{suffix}"
        return path
    
    def resize(self, size: Tuple[int, int] = None, scale_x: float = None, scale_y : float = None) -> "FloatingImage":
        if size is None:
            if scale_y is None:
                scale_y = scale_x
            if scale_y==1 and scale_x==1:
                return self
            size = np.round(np.array(self.dims()) * np.array([scale_x, scale_y])).astype(int)

        return FloatingImage(self.as_pil().resize(size, resample=RESIZE_ALG), default_suffix=self._default_suffix, **self._save_kw) 
    
    
    def _has_path(self) -> bool:
        return "perm_path" in self._sources or "temp_path" in self._sources

    
    def as_specific_image_format(self, format:str = ".png") -> Path:
        if self._has_path() and self.as_path().suffix == format:
            return self.as_path()
        
        #TODO: Make this more efficient by specific source names
        source_to_create = f"temp_path_{format[1:]}"
        if source_to_create in self._sources:
            return self._sources[source_to_create]
        self._save(source_to_create, format=format)
        return self._sources[source_to_create]
    
    def as_png(self) -> Path:
        return self.as_specific_image_format(".png")
        
    def _save(self, source, url:str = None, format:str = None):
        if format is None:
            format = self._default_suffix
        path = self._get_temp_path(url=url, suffix=format)
        self._temp_sources.append(source)
        self.as_pil().save(path, **self._save_kw)
        self._sources[source] = path



        
        
class FloatingImageWithROI:
    def __init__(self, img:FloatingImage, 
                 roi: Tuple[int, int, int, int]):
        self._img = img
        self._roi = roi 
        self._sources = {}
    
    def as_pil(self) -> PIL.Image.Image:
        if "cropped_image" in self._sources:
            return self._sources["cropped_image"]
        elif "cropped_path" in self._sources:
            self._sources["cropped_image"] = (cimage := PIL.Image.open(self._sources["cropped_path"]))
            return cimage
            
        else:
            image = self._img.as_pil()
            x,y,w,h = self._roi
            pilrect = (x,y,x+w,y+h)
            cropped = image.crop(pilrect)
            self._sources["cropped_image"] = cropped
            return cropped
        
    def as_path(self) -> Path:
        if "cropped_path" in self._sources:
            return self._sources["cropped_path"]
        elif "cropped_image" in self._sources:
            self._sources["cropped_path"] = self._img._get_temp_path()
            
            self._sources["cropped_image"].save(self._sources["cropped_path"])
            return self._sources["cropped_path"]
        else:
            cropped = self.as_pil()
            self._sources["cropped_path"] = self._img._get_temp_path()
            
            cropped.save(self._sources["cropped_path"], **self._img._save_kw)
            return self._sources["cropped_path"]
        
    def as_floating_image(self) -> FloatingImage:
        return FloatingImage(self.as_pil(), default_suffix=self._img._default_suffix, **self._img._save_kw)
       
    def cleanup(self):
        self._img.cleanup()
        if "cropped_path" in self._sources:
            self._sources["cropped_path"].unlink()
            del self._sources["cropped_path"]

    @property
    def dims(self) -> Tuple[int, int]:
        return self._roi[2:]
    
    def crop(self, roi: Tuple[int, int, int, int]) -> "FloatingImageWithROI":
        x,y = np.clip([self._roi[0] + roi[0], self._roi[1] + roi[1]], 0, self._img.dims())
        ox2,oy2 = x+self._roi[2], y+self._roi[3]
        w,h = roi[2:]
        x2,y2 = np.clip([x+w, y+h], 0, np.minimum(self._img.dims(), [ox2, oy2]))
        return FloatingImageWithROI(self.img, x, y, x2-x, y2-y)
    
    def resize(self, size: Tuple[int, int] = None, scale_x: float = None, scale_y : float = None) -> FloatingImage:
        if scale_x != None and (scale_x == 1 and scale_y == 1):
            return self
        return self.as_floating_image().resize(size, scale_x, scale_y)
    
    def flip(self, horz: bool = False, vert: bool = False) -> FloatingImage:
        return self.as_floating_image().flip(horz, vert)
    
    def cleanup(self):
        self._img.cleanup()
        if "cropped_path" in self._sources:
            self._sources["cropped_path"].unlink()
            del self._sources["cropped_path"]


    def as_png(self) -> Path:
        return self.as_floating_image().as_png()

def to_floating_image(source: PossibleSource | None, default_suffix=None, **save_kw)->FloatingImage|None:
    if isinstance(source, (FloatingImage, FloatingImageWithROI)):
        return source
    elif source is None:
        return None
    else:
        kw = save_kw.copy()
        if default_suffix:
            kw["default_suffix"] = default_suffix
        return FloatingImage(source, **kw)

class TokenImage:
    """
    Represents a token image that can be drawn on a canvas.
    
    """
    def __init__(self, image: FloatingImage|PossibleSource,
                 mask: FloatingImage|PossibleSource|None = None,
                 default_suffix=".png", **kw):
        self._default_suffix = default_suffix
        self._save_kw = kw
        self._img = to_floating_image(image, default_suffix, **kw)
        self._mask = to_floating_image(mask, default_suffix, **kw)
        self._gray = None
        self._foreground = None
        

    def crop(self, roi: Tuple[int, int, int, int], zoom:bool=False) -> "TokenImage":
        """
        Crop the image and possibly the mask
        """
        return TokenImage(self._img.crop(roi,zoom), self._mask.crop(roi,zoom) if self._mask else None, self._default_suffix, **self._save_kw)

    @property
    def dims(self) -> Tuple[int, int]:
        return self._img.dims
    
    def cleanup(self):
        self._img.cleanup()
        if self._mask:
            self._mask.cleanup()
    
    def add_mask(self, mask: FloatingImage|PossibleSource) -> TokenImage:
        image = self
        if image.masked:
            image = image.join_mask()
        return TokenImage(image._img, mask, image._default_suffix, **image._save_kw)

    @property
    def image(self) -> PIL.Image.Image:
        return self._img.as_pil()
    
    @property
    def path(self) -> Path:
        return self._img.as_path()
    
    @property
    def array(self) -> np.ndarray:
        return self._img.as_array()
    
    @property
    def mask(self) -> PIL.Image.Image:
        return self._mask.as_pil() if self._mask else None
    
    @property 
    def masked(self) -> bool:
        return self._mask is not None

    @property
    def mask_path(self) -> Path:
        return self._mask.as_path() if self._mask else None
    
    @property
    def mask_array(self) -> np.ndarray:
        return self._mask.as_array() if self._mask else None
    

    @property
    def bytes(self) -> bytes:
        return self.path.read_bytes()
    
    @property
    def png_path(self) -> Path:
        return self._img.as_png()
    
    @property
    def png_bytes(self) -> bytes:
        return self.png_path.read_bytes()
    
    @property
    def mask_bytes(self) -> bytes:
        return self.mask_path.read_bytes() if self._mask else None
    
    @property
    def mime_with_data(self) -> str:
        suffix = self.path.suffix[1:]
        return f"data:image/{suffix};base64,{base64.b64encode(self.bytes).decode()}"
    
    @property
    def mime_with_data_png(self) -> str:
        return f"data:image/png;base64,{base64.b64encode(self.png_bytes).decode()}"
    
    @property
    def gray(self) -> FloatingImage | FloatingImageWithROI:
        if self._gray is None:
            pil_image = self.image.convert("L")
            self._gray = FloatingImage(pil_image, default_suffix=self._default_suffix, **self._save_kw)
        return self._gray
    
    @property
    def foreground(self) -> FloatingImage | FloatingImageWithROI:
        if self._foreground is None:
            arr = find_background(self.join_mask().array)
            foreground = FloatingImage(np.logical_not(arr), default_suffix=self._default_suffix, **self._save_kw)
            foreground = foreground.as_pil().filter(PIL.ImageFilter.ModeFilter(13))
            self._foreground = FloatingImage(foreground, default_suffix=self._default_suffix, **self._save_kw)
        return self._foreground
    
    @property
    def foreground_roi(self) -> Tuple[int, int, int, int]:
        return mask_to_roi(self.foreground.as_array())
    
    def crop_foreground_roi(self, zoom:bool=False) -> "TokenImage":
        return self.crop(self.foreground_roi, zoom)

    def filters(self, filters: Sequence[str]|Dict[str, Dict], loader) -> "TokenImage":
        image = self
        if not filters:
            return image
        image = apply_imagefilters(image, filters, loader)
        return image
        

    def resize(self, size: Tuple[int, int] = None, scale_x: float = None, scale_y : float = None) -> "TokenImage":
        if size is None:
            if scale_y is None:
                scale_y = scale_x
            size = np.round(np.array(self.dims) * np.array([scale_x, scale_y])).astype(int)

        return TokenImage(self._img.resize(size=size), 
                          self._mask.resize(size=size) if self._mask else None,
                          default_suffix=self._default_suffix, **self._save_kw)
    
    def join_mask(self, blend:bool=True, allow_resize:bool=True) -> TokenImage:
        if not self.masked:
            return self
        image = join_mask_channel(self.image, self.mask_array, blend, allow_resize)
        return TokenImage(image, default_suffix=self._default_suffix, **self._save_kw)

    def flip(self, horz: bool = False, vert: bool = False) -> TokenImage:
        return TokenImage(self._img.flip(horz, vert), 
                          self._mask.flip(horz, vert) if self._mask else None,
                          default_suffix=self._default_suffix, **self._save_kw)
    
    def rotate(self, angle: float) -> TokenImage:
        return TokenImage(self._img.rotate(angle), 
                          self._mask.rotate(angle) if self._mask else None,
                          default_suffix=self._default_suffix, **self._save_kw)
    

    def op(self, op: Callable[[Image.Image], Image.Image] |
                     Callable[[Image.Image, Image.Image], Tuple[Image.Image, Image.Image]]
           ) -> TokenImage:
        mask_res = None
        if self.masked:
            op_res, mask_res = op(self.image, self.mask)
        else:
            op_res = op(self.image)
        return TokenImage(image=op_res, mask=mask_res, default_suffix=self._default_suffix, **self._save_kw)

    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.cleanup()

