import os
import streamlit as st
from rdkit import Chem
from rdkit.Chem import Draw
from rdkit.Chem import AllChem
import cohere
from groq import Groq
import py3Dmol

# Configure API keys
os.environ['GROQ_API_KEY'] = 'YOUR_API_KEY'

# Streamlit UI
st.title("Drug Discovery with AI")
st.write("Generate and visualize drug-like molecules using AI.")

# Input for amino acid sequence
# User customizable prompt for LLaMA3
amino_acid_sequence =st.text_area("Enter the amino acid sequence of the virus: ")
virus_name = st.text_area("Enter the name of the virus: ")
additional_features = st.text_area("Enter other characteristics of the virus: ")
if st.button("Generate SMILES"):
    llama3_user_prompt = f"""
    oops you can try .......
"""

    # Generate SMILES using Groq and LLaMA3
    client = Groq()
    completion = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role": "user", "content": llama3_user_prompt}],
        temperature=1,
        max_tokens=1024,
        top_p=1,
        stream=True,
        stop=None,
    )

    smile = ""
    for chunk in completion:
        smile += chunk.choices[0].delta.content or ""
    st.write("LLaMA3 Output SMILES:", smile)

    # Cohere part
    co = cohere.Client(api_key="YOUR_API_KEY")
    prompt = f"""
    Affinnement de la structure SMILE......
    """

    response = co.generate(
        model="command-r-plus",
        prompt=prompt,
        max_tokens=300,
        temperature=0.7,
        k=0,
        p=0.75,
        frequency_penalty=0,
        presence_penalty=0,
        stop_sequences=[]
    )

    st.write("Cohere Output:", response.generations[0].text)

    # Validate SMILES string
    def validate_smiles(smiles):
        try:
            mol = Chem.MolFromSmiles(smiles)
            if mol is None:
                return False
            return True
        except:
            return False

    smiles = smile.strip()
    if not validate_smiles(smiles):
        st.error("Invalid SMILES string")
    else:
        mol = Chem.MolFromSmiles(smiles)
        img = Draw.MolToImage(mol)
        st.image(img, caption="2D", use_column_width=True)

        # Add hydrogens and generate 3D coordinates
        mol = Chem.AddHs(mol)
        AllChem.EmbedMolecule(mol, randomSeed=42)

        with open('ligand_3d.pdb', 'w') as f:
            f.write(Chem.MolToPDBBlock(mol))

        # Create 3D visualization with Py3Dmol
        view = py3Dmol.view(width=800, height=400)
        with open('ligand_3d.pdb', 'r') as f:
            pdb_data = f.read()
        view.addModel(pdb_data, 'pdb')
        view.setStyle({'stick': {}})
        view.setBackgroundColor('white')
        view.zoomTo()

        # Render the view and get the HTML
        html = view._make_html()

        # Display the 3D visualization in Streamlit
        st.components.v1.html(html, height=400)
