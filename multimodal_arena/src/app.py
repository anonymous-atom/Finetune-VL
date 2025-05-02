import gradio as gr
import json
import random
import os
from typing import Dict, List, Tuple
import pandas as pd
from pathlib import Path
import time
from datetime import datetime

class MultimodalArena:
    def __init__(self, data_path: str = "data/samples.json", results_path: str = "data/results.csv"):
        self.data_path = data_path
        self.results_path = results_path
        self.samples = self._load_samples()
        self.results = self._load_results()
        self.current_sample = None
        self.current_models = None
        self.session_id = str(int(time.time()))

    def _load_samples(self) -> List[Dict]:
        """Load the sample data from JSON file."""
        with open(self.data_path, 'r') as f:
            return json.load(f)

    def _load_results(self) -> pd.DataFrame:
        """Load or create the results DataFrame."""
        if os.path.exists(self.results_path):
            return pd.read_csv(self.results_path)
        return pd.DataFrame(columns=[
            'session_id', 'timestamp', 'sample_id', 
            'Response 1', 'Response 2', 'Response 3',
            'winner', 'tie',
            'qwen2.5-vl', 'geminivision', 'gpt4v', 'target',
            'clarity', 'relevance', 'depth', 'originality',
            'usefulness', 'discussion_potential', 'understanding_check'
        ])

    def _save_results(self):
        """Save the results DataFrame to CSV."""
        self.results.to_csv(self.results_path, index=False)

    def get_random_sample(self) -> Tuple[Dict, List[str]]:
        """Get a random sample and three random models."""
        if not self.samples:
            raise ValueError("No samples available")
        sample = random.choice(self.samples)
        models = list(sample['model_outputs'].keys())
        selected_models = random.sample(models, 3)
        return sample, selected_models

    def get_outputs(self, sample_id: str, models: List[str]) -> Tuple[List, List, List, List[str]]:
        """Get the outputs for a specific sample and models in chat format."""
        sample = next(s for s in self.samples if s['id'] == sample_id)
        responses = []
        for model in models:
            responses.append([["assistant", sample['model_outputs'][model]['text']]])
        return tuple(responses)

    def record_vote(self, sample_id: str, models: List[str], winner: str, tie: bool,
                   clarity: int, relevance: int, depth: int, originality: int,
                   usefulness: int, discussion_potential: int, understanding_check: int):
        """Record a vote in the results DataFrame."""
        # Initialize all model votes to 0
        model_votes = {model: 0 for model in ['qwen2.5-vl', 'geminivision', 'gpt4v', 'target']}
        
        # If there's a tie, all models get 0.5 votes
        if tie:
            for model in models:
                model_votes[model] = 0.5
        # Otherwise, the winner gets 1 vote
        elif winner != "All are equally good":
            # Map UI response number to actual model
            winner_idx = int(winner.split()[-1]) - 1  # Convert "Response 1" to 0, etc.
            winner_model = models[winner_idx]
            model_votes[winner_model] = 1

        new_row = {
            'session_id': self.session_id,
            'timestamp': datetime.now().isoformat(),
            'sample_id': sample_id,
            'Response 1': models[0],
            'Response 2': models[1],
            'Response 3': models[2],
            'winner': winner,
            'tie': tie,
            'clarity': clarity,
            'relevance': relevance,
            'depth': depth,
            'originality': originality,
            'usefulness': usefulness,
            'discussion_potential': discussion_potential,
            'understanding_check': understanding_check,
            **model_votes  # Add all model votes to the row
        }
        self.results = pd.concat([self.results, pd.DataFrame([new_row])], ignore_index=True)
        self._save_results()

def create_interface():
    arena = MultimodalArena()
    arena.start_time = time.time()

    def get_new_sample():
        sample, models = arena.get_random_sample()
        arena.current_sample = sample
        arena.current_models = models
        outputs = arena.get_outputs(sample['id'], models)
        return (
            sample['prompt'],
            sample['image_paths'],
            outputs[0],
            outputs[1],
            outputs[2]
        )

    def record_vote(winner: str, tie: bool, clarity: int, relevance: int, 
                   depth: int, originality: int, usefulness: int, discussion_potential: int,
                   understanding_check: int):
        if arena.current_sample and arena.current_models:
            arena.record_vote(
                arena.current_sample['id'],
                arena.current_models,
                winner,
                tie,
                clarity,
                relevance,
                depth,
                originality,
                usefulness,
                discussion_potential,
                understanding_check
            )
        return get_new_sample()

    with gr.Blocks(title="Multimodal Model Arena", theme=gr.themes.Soft()) as demo:
        gr.Markdown("""
        # Research Question Evaluation
        ### Compare and rate AI-generated questions for research papers
        """)

        with gr.Row():
            with gr.Column(scale=2):
                # Image Gallery
                gr.Markdown("### Paper Pages")
                image_gallery = gr.Gallery(
                    label="Research Paper",
                    show_label=False,
                    elem_id="gallery",
                    columns=2,
                    height="auto"
                )
                
                # Prompt Display
                gr.Markdown("### Prompt")
                prompt = gr.Textbox(
                    label="",
                    lines=3,
                    interactive=False,
                    show_label=False
                )

            with gr.Column(scale=3):
                # All responses visible simultaneously
                gr.Markdown("### Generated Questions")
                with gr.Row():
                    with gr.Column():
                        output_a = gr.Chatbot(
                            label="Question 1",
                            show_label=True,
                            height=300,
                            elem_id="chatbot_a"
                        )
                    with gr.Column():
                        output_b = gr.Chatbot(
                            label="Question 2",
                            show_label=True,
                            height=300,
                            elem_id="chatbot_b"
                        )
                    with gr.Column():
                        output_c = gr.Chatbot(
                            label="Question 3",
                            show_label=True,
                            height=300,
                            elem_id="chatbot_c"
                        )

        # Voting Section
        with gr.Row():
            with gr.Column():
                gr.Markdown("### Which question is better?")
                winner = gr.Radio(
                    choices=["Question 1", "Question 2", "Question 3", "All are equally good"],
                    label="",
                    show_label=False
                )
                tie = gr.Checkbox(label="I cannot decide between these questions")

        # Basic Evaluation Metrics
        with gr.Accordion("Essential Question Qualities", open=True):
            with gr.Row():
                with gr.Column():
                    clarity = gr.Radio(
                        choices=["1 (Poor)", "2", "3", "4", "5 (Excellent)"],
                        label="Clarity: Is the question well-formulated and easy to understand?",
                        show_label=True
                    )
                    relevance = gr.Radio(
                        choices=["1 (Poor)", "2", "3", "4", "5 (Excellent)"],
                        label="Relevance: Does the question relate to important aspects of the paper?",
                        show_label=True
                    )
                with gr.Column():
                    depth = gr.Radio(
                        choices=["1 (Poor)", "2", "3", "4", "5 (Excellent)"],
                        label="Depth: Does the question require deep understanding to answer?",
                        show_label=True
                    )
                    originality = gr.Radio(
                        choices=["1 (Poor)", "2", "3", "4", "5 (Excellent)"],
                        label="Originality: Does the question bring a fresh perspective?",
                        show_label=True
                    )
        
        # Advanced Evaluation Metrics
        with gr.Accordion("Research Impact Qualities", open=True):
            with gr.Row():
                with gr.Column():
                    usefulness = gr.Radio(
                        choices=["1 (Poor)", "2", "3", "4", "5 (Excellent)"],
                        label="Usefulness: Would this question be valuable for assessing understanding?",
                        show_label=True
                    )
                    discussion_potential = gr.Radio(
                        choices=["1 (Poor)", "2", "3", "4", "5 (Excellent)"],
                        label="Discussion Potential: Would this question generate meaningful debate?",
                        show_label=True
                    )
                with gr.Column():
                    understanding_check = gr.Radio(
                        choices=["1 (Poor)", "2", "3", "4", "5 (Excellent)"],
                        label="Comprehension: Does this question check for real understanding of the paper?",
                        show_label=True
                    )

        # Submit Button
        submit_btn = gr.Button(
            "Submit & Get New Sample",
            variant="primary"
        )

        # Event Handlers
        submit_btn.click(
            fn=record_vote,
            inputs=[winner, tie, clarity, relevance, depth, originality, 
                   usefulness, discussion_potential, understanding_check],
            outputs=[prompt, image_gallery, output_a, output_b, output_c]
        )

        # Initialize with first sample
        demo.load(
            fn=get_new_sample,
            outputs=[prompt, image_gallery, output_a, output_b, output_c]
        )

    return demo

if __name__ == "__main__":
    demo = create_interface()
    demo.launch(
        share=True,
        server_name="0.0.0.0",
        server_port=7860,
        show_error=True
    ) 