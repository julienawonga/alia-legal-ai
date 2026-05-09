from unsloth import FastLanguageModel
import torch
import json
import os

# 1. Configuration des chemins
model_name = "unsloth/gemma-4-E4B-it-unsloth-bnb-4bit"
adapter_path = "solojunior22/gemma4-droit-ivoirien-lora"
output_dir = "./gemma-droit-ivoirien-fp16"

# 2. Chargement (Unsloth gère déjà le patch Gemma 4)
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = model_name,
    load_in_4bit = True,
)
model = FastLanguageModel.get_peft_model(model, lora_path = adapter_path)

# 3. Fusion réelle en 16-bit (C'est cette étape qui crée les 16GB de fichiers)
print("Fusion des poids en cours...")
model.save_pretrained_merged(
    output_dir,
    tokenizer,
    save_method = "merged_16bit"
)

# 4. NETTOYAGE CRITIQUE : Supprimer les traces LoRA du config.json
config_path = os.path.join(output_dir, "config.json")
with open(config_path, "r") as f:
    config = json.load(f)

# On retire TOUT ce qui fait croire à vLLM que c'est encore un adaptateur
keys_to_remove = [
    "quantization_config",
    "base_model_name_or_path",
    "peft_config",
    "_pre_quantization_dtype"
]
for key in keys_to_remove:
    config.pop(key, None)

# On s'assure que l'architecture est la bonne pour le moteur vLLM
config["architectures"] = ["Gemma4ForConditionalGeneration"]
config["torch_dtype"] = "bfloat16"

with open(config_path, "w") as f:
    json.dump(config, f, indent=2)

print(f"Fusion terminée et config.json nettoyé dans {output_dir}")