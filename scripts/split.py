import os
import os.path
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
                    value=lambda:True,
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


# Modify do_split function to use the classification files


def do_split(need_split_prompts, replace_underscore):
    classifications = load_classification_files()
    results = {key: [] for key in classifications.keys()}

    if "其他" not in results:
        results["其他"] = []

    prompts = need_split_prompts.split(",")
    for prompt in prompts:
        prompt = prompt.strip().lower()

        if not prompt:
            continue

        if replace_underscore:
            prompt = prompt.replace("_", " ")

        classified = False
        for file_name, keywords in classifications.items():
            if any(keyword == prompt for keyword in keywords):
                results[file_name].append(prompt)
                classified = True
                break
        if not classified:
            results["其他"].append(prompt)

    # Format the results for output
    splited_result = ""
    for file_name, prompts in results.items():
        if len(prompts) == 0:
            continue
        splited_result += f"[:{os.path.splitext(file_name)[0]}:99] "
        splited_result += ", ".join(prompts) + "\n\n"

    return splited_result


script_callbacks.on_ui_tabs(add_tab)
