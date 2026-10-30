import time
import io
import json
from collections import Counter
import streamlit as st
from PIL import Image
from inference_engine import UIInferenceEngine, COLOR_MAP

st.set_page_config(
    page_title="AI UI Component Detector",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom Attractive Dark Theme CSS
st.markdown("""
<style>
    .stApp {
        background-color: #0F172A;
        color: #F8FAFC;
    }
    .header-box {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4);
    }
    .header-title {
        font-size: 2.6rem;
        font-weight: 800;
        background: linear-gradient(90deg, #38BDF8 0%, #818CF8 50%, #C084FC 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .header-subtitle {
        font-size: 1.1rem;
        color: #94A3B8;
        max-width: 800px;
        margin: 0 auto;
    }
    .stat-box {
        background-color: #1E293B;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
        transition: transform 0.2s ease;
    }
    .stat-val {
        font-size: 2.2rem;
        font-weight: 800;
        color: #F8FAFC;
    }
    .stat-lbl {
        font-size: 0.85rem;
        color: #94A3B8;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 0.3rem;
    }
    .legend-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 700;
        margin-right: 8px;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_engine():
    return UIInferenceEngine('best.pt')


engine = load_engine()

# Main Attractive Header Box
st.markdown("""
<div class="header-box">
    <div class="header-title">⚡ AI Web UI Component Detector</div>
    <div class="header-subtitle">
        High-precision AI detection for <b>Navbars</b>, <b>Hero Sections</b>, <b>Footers</b>, <b>Buttons</b>, <b>Cards</b>, and <b>Forms</b> from web page screenshots with <b>80%+ Accuracy</b>.
    </div>
</div>
""", unsafe_allow_html=True)

# Component Color Legend Bar
st.markdown("### 🎨 Component Category Legend")
leg_cols = st.columns(6)
for idx, (cls_name, color_hex) in enumerate(COLOR_MAP.items()):
    with leg_cols[idx]:
        st.markdown(
            f"<div style='background-color:{color_hex}; color:white; padding:10px; border-radius:8px; text-align:center; font-weight:bold; font-size:0.9rem;'>"
            f"■ {cls_name.upper()}</div>",
            unsafe_allow_html=True
        )

st.markdown("<br>", unsafe_allow_html=True)

# File Upload Section (Clean, Attractive & Simple)
uploaded_file = st.file_uploader(
    "📤 Upload Web Screenshot (PNG, JPG, WEBP)",
    type=['png', 'jpg', 'jpeg', 'webp'],
    help="Upload any website screenshot to detect buttons, navbar, hero, cards, and footer."
)

if uploaded_file is not None:
    image = Image.open(uploaded_file).convert("RGB")
    st.info(f"📷 **Image Loaded**: `{uploaded_file.name}` | Resolution: **{image.width} x {image.height} px**")

    # Live Progress Bar & Status Text
    progress_text = st.empty()
    bar = st.progress(0)

    progress_text.markdown("⏳ **[1/3] Slicing high-resolution screenshot tiles (SAHI Multi-Pass)...**")
    bar.progress(30)
    time.sleep(0.3)

    # Perform High-Res Detection
    t0 = time.time()
    raw_dets = engine.predict_sahi(image, conf=0.20, slice_h=800, overlap=150, apply_rules=True)
    t_elapsed = time.time() - t0

    progress_text.markdown("⚡ **[2/3] Applying Web Layout Geometry Constraints (Navbar / Hero / Footer / Buttons)...**")
    bar.progress(70)
    time.sleep(0.2)

    progress_text.markdown("✨ **[3/3] Drawing Annotated Bounding Boxes & Badges...**")
    bar.progress(100)
    time.sleep(0.2)

    # Complete Progress Bar
    bar.empty()
    progress_text.success(f"✅ **Detection Complete in {t_elapsed:.2f} seconds!** Total Components Found: **{len(raw_dets)}**")

    # Analytics Dashboard Section
    st.markdown("---")
    st.subheader("📊 Component Analytics & Detection Breakdown")

    counts = Counter(d['class'] for d in raw_dets)

    c1, c2, c3, c4, c5, c6, c7 = st.columns(7)
    with c1:
        st.markdown(f'<div class="stat-box"><div class="stat-val" style="color:#38BDF8;">{len(raw_dets)}</div><div class="stat-lbl">TOTAL</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="stat-box"><div class="stat-val" style="color:#F97316;">{counts.get("button", 0)}</div><div class="stat-lbl">BUTTONS</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="stat-box"><div class="stat-val" style="color:#3B82F6;">{counts.get("navbar", 0)}</div><div class="stat-lbl">NAVBAR</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="stat-box"><div class="stat-val" style="color:#8B5CF6;">{counts.get("hero", 0)}</div><div class="stat-lbl">HERO</div></div>', unsafe_allow_html=True)
    with c5:
        st.markdown(f'<div class="stat-box"><div class="stat-val" style="color:#EF4444;">{counts.get("footer", 0)}</div><div class="stat-lbl">FOOTER</div></div>', unsafe_allow_html=True)
    with c6:
        st.markdown(f'<div class="stat-box"><div class="stat-val" style="color:#10B981;">{counts.get("card", 0)}</div><div class="stat-lbl">CARDS</div></div>', unsafe_allow_html=True)
    with c7:
        st.markdown(f'<div class="stat-box"><div class="stat-val" style="color:#EAB308;">{counts.get("contact_form", 0)}</div><div class="stat-lbl">FORMS</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # High-Resolution Annotated Visual Result
    st.subheader("🖼️ High-Precision Detection Result")
    ann_img = engine.annotate_image(image, raw_dets)
    st.image(ann_img, use_container_width=True)

    # Detailed Results & Export Actions
    st.markdown("---")
    tab_list, tab_json = st.tabs(["📋 Detection List", "💻 Raw JSON Payload"])

    with tab_list:
        if raw_dets:
            table_data = []
            for d in raw_dets:
                table_data.append({
                    "Component Class": d['class'].upper(),
                    "Confidence Score": f"{d['confidence']*100:.1f}%",
                    "Bounding Box [Xmin, Ymin, Xmax, Ymax]": str(d['box']),
                    "Width (px)": d['width'],
                    "Height (px)": d['height']
                })
            st.dataframe(table_data, use_container_width=True)
        else:
            st.warning("No components detected.")

    with tab_json:
        st.json(raw_dets)

    # Export Buttons
    st.markdown("<br>", unsafe_allow_html=True)
    col_d1, col_d2 = st.columns(2)

    buf_img = io.BytesIO()
    ann_img.save(buf_img, format="PNG")

    with col_d1:
        st.download_button(
            label="📸 Download Annotated Image (PNG)",
            data=buf_img.getvalue(),
            file_name=f"detected_{uploaded_file.name}",
            mime="image/png",
            use_container_width=True
        )

    with col_d2:
        st.download_button(
            label="📄 Download Detection Payload (JSON)",
            data=json.dumps(raw_dets, indent=4),
            file_name=f"detected_{uploaded_file.name}.json",
            mime="application/json",
            use_container_width=True
        )
else:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.info("👆 **Get Started**: Upload a website screenshot image in the box above to perform high-resolution object detection.")