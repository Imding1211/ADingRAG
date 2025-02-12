
from marker.output import markdown_exists, save_markdown
from marker.pdf.extract_text import get_length_of_text
from marker.convert import convert_single_pdf
from marker.logger import configure_logging
from marker.pdf.utils import find_filetype
from marker.models import load_all_models
from marker.settings import settings

from tqdm import tqdm

import torch.multiprocessing as mp
import pypdfium2
import traceback
import math
import json
import sys
import os

#=============================================================================#

os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1" # For some reason, transformers decided to use .isin for a simple op, which is not supported on MPS
os.environ["IN_STREAMLIT"] = "true" # Avoid multiprocessing inside surya
os.environ["PDFTEXT_CPU_WORKERS"] = "1" # Avoid multiprocessing inside pdftext

#=============================================================================#

configure_logging()

#=============================================================================#

def remove_temp_PDF(folder_path):
    
    if not os.path.exists(folder_path):
        print(f"資料夾 {folder_path} 不存在。")
        return
    
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path) and filename.lower().endswith('.pdf'):
                os.remove(file_path)
                print(f"已刪除檔案: {file_path}")
        except Exception as e:
            print(f"無法刪除檔案 {file_path}，錯誤: {e}")

#-----------------------------------------------------------------------------#

def worker_init(shared_model):

    if shared_model is None:
        shared_model = load_all_models()

    global model_refs
    model_refs = shared_model

#-----------------------------------------------------------------------------#

def worker_exit():

    global model_refs
    del model_refs

#-----------------------------------------------------------------------------#

def process_single_pdf(args):

    filepath, out_folder, metadata, min_length = args

    fname = os.path.basename(filepath)
    if markdown_exists(out_folder, fname):
        return

    try:
        # Skip trying to convert files that don't have a lot of embedded text
        # This can indicate that they were scanned, and not OCRed properly
        # Usually these files are not recent/high-quality
        if min_length:
            filetype = find_filetype(filepath)
            if filetype == "other":
                return 0

            length = get_length_of_text(filepath)
            if length < min_length:
                return

        full_text, images, out_metadata = convert_single_pdf(filepath, model_refs, metadata=metadata)
        if len(full_text.strip()) > 0:
            save_markdown(out_folder, fname, full_text, images, out_metadata)
        else:
            print(f"Empty file: {filepath}.  Could not convert.")
    except Exception as e:
        print(f"Error converting {filepath}: {e}")
        print(traceback.format_exc())

#-----------------------------------------------------------------------------#

def PDF_to_MD(in_folder, out_folder, chunk_idx=0, num_chunks=1, max_num=None, workers=5, metadata_file=None, min_length=None):

    in_folder  = os.path.abspath(in_folder)
    out_folder = os.path.abspath(out_folder)

    files = [os.path.join(in_folder, f) for f in os.listdir(in_folder)]
    files = [f for f in files if os.path.isfile(f)]

    os.makedirs(out_folder, exist_ok=True)

    # Handle chunks if we're processing in parallel
    # Ensure we get all files into a chunk
    chunk_size       = math.ceil(len(files) / num_chunks)
    start_idx        = chunk_idx * chunk_size
    end_idx          = start_idx + chunk_size
    files_to_convert = files[start_idx:end_idx]

    # Limit files converted if needed
    if max_num:
        files_to_convert = files_to_convert[:max_num]

    metadata = {}
    if metadata_file:
        metadata_file = os.path.abspath(metadata_file)
        with open(metadata_file, "r") as f:
            metadata = json.load(f)

    total_processes = min(len(files_to_convert), workers)

    try:
        mp.set_start_method('spawn') # Required for CUDA, forkserver doesn't work
    except RuntimeError:
        raise RuntimeError("Set start method to spawn twice. This may be a temporary issue with the script. Please try running it again.")

    if settings.TORCH_DEVICE == "mps" or settings.TORCH_DEVICE_MODEL == "mps":
        print("Cannot use MPS with torch multiprocessing share_memory. This will make things less memory efficient. If you want to share memory, you have to use CUDA or CPU.  Set the TORCH_DEVICE environment variable to change the device.")

        model_lst = None
    else:
        model_lst = load_all_models()

        for model in model_lst:
            if model is None:
                continue
            model.share_memory()

    print(f"Converting {len(files_to_convert)} pdfs in chunk {chunk_idx + 1}/{num_chunks} with {total_processes} processes, and storing in {out_folder}")
    
    task_args = [(f, out_folder, metadata.get(os.path.basename(f)), min_length) for f in files_to_convert]

    with mp.Pool(processes=total_processes, initializer=worker_init, initargs=(model_lst,)) as pool:
        list(tqdm(pool.imap(process_single_pdf, task_args), total=len(task_args), desc="Processing PDFs", unit="pdf"))

        pool._worker_handler.terminate = worker_exit

    # Delete all CUDA tensors
    del model_lst

#=============================================================================#

if __name__ == "__main__":

    in_folder  = f"storage/{sys.argv[1]}/save_PDF/"
    out_folder = f"storage/{sys.argv[1]}/output_MD/"

    PDF_to_MD(in_folder, out_folder, chunk_idx=0, num_chunks=1, max_num=None, workers=2, metadata_file=None, min_length=None)
    
    #remove_temp_PDF("temp_PDF")
