import os
import os.path
import re
import gradio as gr
from modules import script_callbacks, shared
from modules.ui import create_refresh_button


def add_tab():
    with gr.Blocks(analytics_enabled=False) as ui:
        with gr.Row().style(equal_height=False):
            with gr.Column(variant='panel'):
                gr.HTML(
                    value="<p>Differentiate prompts according to different types.")

                replace_underscore = gr.Checkbox(
                    value=lambda: True,
                    label="Replace underscores with spaces",
                    elem_id="replace_underscore_checkbox")

                need_split_prompts = gr.Textbox(
                    lines=6,
                    label="Prompts",
                    elem_id="need_split_prompts")

                button_split_prompts = gr.Button(
                    elem_id="button_split_prompts",
                    value="Split",
                    variant='primary')

            with gr.Column(variant='panel'):
                submit_result = gr.Textbox(
                    label="Result",
                    elem_id="split_result",
                    interactive=False,
                    show_copy_button=True)

            button_split_prompts.click(
                fn=do_split,
                inputs=[
                    need_split_prompts,
                    replace_underscore,
                ],
                outputs=[submit_result]
            )

    return [(ui, "Split prompts", "split_prompts")]


def load_classification_files():
    base_path = os.path.join(os.path.dirname(
        os.path.dirname(os.path.realpath(__file__))), "分類")

    # A dictionary to hold the contents of the txt files classified by the main folders
    file_contents = {}

    # Iterate through the main folders in the "分類" directory
    for main_folder in os.listdir(base_path):
        main_folder_path = os.path.join(base_path, main_folder)

        # Only process directories (main folders)
        if os.path.isdir(main_folder_path):
            file_contents[main_folder] = []

            # Iterate through all subdirectories and txt files inside the main folder
            for dirpath, dirnames, filenames in os.walk(main_folder_path):
                for file in filenames:
                    if file.endswith(".txt"):
                        with open(os.path.join(dirpath, file), "r", encoding="utf-8") as f:
                            # Add the contents of the txt file to the main folder's list
                            file_contents[main_folder].extend(
                                [word.lower() for word in f.read().splitlines()])

    return file_contents


def simplify_word(word):
    # 使用正则表达式提取词部分
    match = re.match(r'^\(([\w\s]+):\d+\.\d+\)$|^\(([\w\s]+)\)$', word)
    if match:
        processed_word = match.group(1) or match.group(2)
        return processed_word
    else:
        return word

# Modify do_split function to use the classification files


def do_split(need_split_prompts, replace_underscore):
    classifications = load_classification_files()
    results = {key: [] for key in classifications.keys()}

    if "其他" not in results:
        results["其他"] = []

    if "lora" not in results:
        results["lora"] = []

    prompts = re.split(r'[,|\n]', need_split_prompts)
    for prompt in prompts:
        prompt = prompt.strip().lower()

        if not prompt:
            continue

        if replace_underscore:
            prompt = prompt.replace("_", " ")

        check_prompt = prompt
        if prompt.startswith("("):
            check_prompt = simplify_word(prompt)

        classified = False
        for file_name, keywords in classifications.items():
            if any(keyword == check_prompt for keyword in keywords):
                results[file_name].append(prompt)
                classified = True
                break

        if not classified:
            if prompt.startswith("<lora:"):
                results["lora"].append(prompt)
            else:
                results["其他"].append(prompt)

    # Format the results for output

    seg_word = ", "
    splited_result = ""
    for file_name, prompts in results.items():
        if len(prompts) == 0:
            continue

        if file_name.startswith("lora"):
            seg_word = "\n"
        else:
            splited_result += f"[:{os.path.splitext(file_name)[0]}:99] "

        splited_result += seg_word.join(prompts) + "\n\n"

    return splited_result.rstrip("\n")


script_callbacks.on_ui_tabs(add_tab)
