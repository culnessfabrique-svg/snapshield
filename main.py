import io
import zipfile
import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

# Configurazione pagina e Brand SnapShield
st.set_page_config(
    page_title="SnapShield | Protezione & Branding Immagini",
    page_icon="🛡️",
    layout="wide"
)

# Stile CSS personalizzato per renderlo un sito moderno
st.markdown("""
    <style>
    .main { padding: 2rem; }
    .stButton>button {
        width: 100%;
        background-color: #2563EB;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 0.75rem;
    }
    </style>
""", unsafe_allow_html=True)

# Header Principale
st.title("🛡️ SnapShield")
st.markdown("##### La piattaforma automatizzata per proteggere e firmare le tue immagini in alta qualità.")
st.write("---")
font_size = st.slider("Grandezza del testo", 10, 100, 30)
opacity = st.slider("Trasparenza", 10, 100, 80)

# Layout a due colonne
left_col, right_col = st.columns([1, 1])

with left_col:
    st.subheader("1. Carica le tue Immagini")
    uploaded_files = st.file_uploader(
        "Trascina qui le tue foto (JPG, PNG)", 
        type=["jpg", "jpeg", "png"], 
        accept_multiple_files=True
    )

    st.subheader("2. Impostazioni del Brand")
    watermark_type = st.radio("Tipo di protezione:", ["Testo / Copyright", "Logo personalizzato (PNG)"])
    
    watermark_text = ""
    logo_file = None
    
    if watermark_type == "Testo / Copyright":
        watermark_text = st.text_input("Testo da applicare:", value="© SnapShield")
        text_color = st.color_picker("Colore del testo:", "#FFFFFF")
    else:
        logo_file = st.file_uploader("Carica il tuo logo trasparente (PNG):", type=["png"])

with right_col:
    st.subheader("3. Posizione e Trasparenza")
    position = st.selectbox(
        "Posizione del marchio:",
        ["In basso a destra", "In basso a sinistra", "In alto a destra", "In alto a sinistra", "Al centro"]
    )
    opacity = st.slider("Opacità / Trasparenza:", min_value=10, max_value=100, value=80) / 100.0

st.write("---")

def apply_watermark(base_img, text, logo, pos_type, alpha):
    img = base_img.convert("RGBA")
    overlay = Image.new("RGBA", img.size, (255, 255, 255, 0))
    
    w, h = img.size
    
    if logo:
        logo_img = Image.open(logo).convert("RGBA")
        # Ridimensiona logo in base alla foto (max 20% della larghezza)
        max_logo_w = int(w * 0.2)
        ratio = max_logo_w / float(logo_img.size[0])
        logo_h = int((float(logo_img.size[1]) * float(ratio)))
        logo_img = logo_img.resize((max_logo_w, logo_h), Image.Resampling.LANCZOS)
        
        # Gestione opacità logo
        alpha_channel = logo_img.split()[3]
        alpha_channel = ImageEnhance.Brightness(alpha_channel).enhance(alpha)
        logo_img.putalpha(alpha_channel)
        
        lw, lh = logo_img.size
        positions = {
            "In basso a destra": (w - lw - 20, h - lh - 20),
            "In basso a sinistra": (20, h - lh - 20),
            "In alto a destra": (w - lw - 20, 20),
            "In alto a sinistra": (20, 20),
            "Al centro": ((w - lw) // 2, (h - lh) // 2)
        }
        overlay.paste(logo_img, positions.get(pos_type, (20, 20)))
    else:
        draw = ImageDraw.Draw(overlay)
        font_size = int(h * 0.04)
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
            
        bbox = draw.textbbox((0, 0), text, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        
        positions = {
            "In basso a destra": (w - tw - 30, h - th - 30),
            "In basso a sinistra": (30, h - th - 30),
            "In alto a destra": (w - tw - 30, 30),
            "In alto a sinistra": (30, 30),
            "Al centro": ((w - tw) // 2, (h - th) // 2)
        }
        
        r, g, b = int(text_color[1:3], 16), int(text_color[3:5], 16), int(text_color[5:7], 16)
        draw.text(positions.get(pos_type, (30, 30)), text, fill=(r, g, b, int(255 * alpha)), font=font)
        
    final_img = Image.alpha_composite(img, overlay)
    return final_img.convert("RGB")

# Sezione Risultato e Download
if uploaded_files:
    st.subheader(f"4. Anteprima & Download ({len(uploaded_files)} foto)")
    
    if st.button("🛡️ ELABORA IMMAGINI CON SNAPSHIELD"):
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
            for idx, uploaded_file in enumerate(uploaded_files):
                raw_img = Image.open(uploaded_file)
                processed_img = apply_watermark(raw_img, watermark_text, logo_file, position, opacity)
                
                # Salvataggio in memoria per lo ZIP
                img_byte_arr = io.BytesIO()
                processed_img.save(img_byte_arr, format='JPEG', quality=95)
                zip_file.writestr(f"SnapShield_{uploaded_file.name}", img_byte_arr.getvalue())
                
                if idx == 0:
                    st.image(processed_img, caption="Anteprima della prima immagine elaborata", use_column_width=True)
        
        st.success("Elaborazione completata con successo!")
        
        # Bottone Download ZIP
        st.download_button(
            label="📦 SCARICA TUTTE LE FOTO ELABORATE (.ZIP)",
            data=zip_buffer.getvalue(),
            file_name="SnapShield_Immagini.zip",
            mime="application/zip"
        )
else:
    st.info("Carica una o più immagini a sinistra per iniziare.")
