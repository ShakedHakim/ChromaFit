import html
import io
import os
import tempfile
from collections.abc import Callable
from pathlib import Path
from string import Template

import streamlit as st
from PIL import Image, ImageDraw, ImageFont

from models import NamedColor
from repository_factory import RepositoryFactory
from stylist_service import StylistService

CATEGORIES = ["top", "bottom", "shoes"]
# Product images cut from the design mockup, served by Streamlit from static/.
CATEGORY_IMAGES = {category: f"app/static/{category}.png" for category in CATEGORIES}
STEP_LABELS = ["Item", "Targets", "Upload", "Results"]
HOME = "home"
FIRST_SCREEN = 1
LAST_SCREEN = 4
HERO_IMAGE = Path(__file__).parent / "static" / "hero.png"
HOW_IT_WORKS = ["Upload your item", "Choose what you need", "Get your colors"]
TOP_N = 5

NAVY = "#1B2A4A"
CREAM = "#F7EFE3"
TAN = "#E8D4B8"
TEAL = "#2A9D8F"
LIGHT_TEAL = "#BFE6E1"
CARD = "#FFFCF7"
SELECTED_CARD = "#E7F3F0"

UPLOAD_ICON_SVG = (
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%232A9D8F' "
    "stroke-width='1.6' stroke-linecap='round' stroke-linejoin='round'>"
    "<path d='M14 4H6a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-6'/>"
    "<circle cx='9' cy='9' r='1.5'/><path d='M4 17l5-5 4 4 2-2 5 5'/><path d='M19 3v6M16 6h6'/></svg>"
)
CORNER_SVG = (
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 200 200'>"
    "<path d='M0 40 C70 50 110 120 95 200 L0 200Z' fill='%23E8D4B8'/>"
    "<path d='M0 105 C45 115 70 160 60 200 L0 200Z' fill='%232A9D8F'/></svg>"
)
CHECK_ICON_SVG = (
    '<svg viewBox="0 0 24 24" width="40" height="40" fill="none" stroke="#2A9D8F" stroke-width="1.6" '
    'stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/>'
    '<path d="M8 12.5l2.7 2.7L16 9.5"/></svg>'
)
PALETTE_ICON_SVG = (
    '<svg viewBox="0 0 24 24" width="30" height="30" fill="none" stroke="#2A9D8F" stroke-width="1.5" '
    'stroke-linecap="round" stroke-linejoin="round"><path d="M12 3a9 9 0 0 0 0 18c1 0 1.6-.7 1.6-1.5 '
    '0-.4-.2-.8-.4-1-.3-.3-.4-.6-.4-1 0-.9.7-1.5 1.5-1.5H16a5 5 0 0 0 5-5c0-4.4-4-8-9-8z"/>'
    '<circle cx="7.5" cy="11" r="1"/><circle cx="10" cy="7" r="1"/><circle cx="14.5" cy="7" r="1"/>'
    '<circle cx="17" cy="11" r="1"/></svg>'
)

GLOBAL_CSS = Template("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Playfair+Display:wght@500;600;700&display=swap');

/* Page */
.stApp {
    background-color: $cream;
    color: $navy;
}
.stApp::before {
    content: "";
    position: fixed;
    left: 0;
    bottom: 0;
    width: 150px;
    height: 150px;
    background: url("data:image/svg+xml;utf8,$corner") no-repeat left bottom / contain;
    pointer-events: none;
    z-index: 0;
}
[data-testid="stHeader"] {
    background: transparent;
}
[data-testid="stMainBlockContainer"], .block-container {
    max-width: 480px;
    padding-top: 2.5rem;
}
.stApp p, .stApp li, .stApp label, .stApp button, .stApp input {
    font-family: 'Inter', sans-serif !important;
    color: $navy;
}
.stApp h1, .stApp h2, .stApp h3 {
    font-family: 'Playfair Display', serif !important;
    color: $navy !important;
}
.stApp h1 {
    text-align: center;
    font-size: 2rem !important;
    font-weight: 500 !important;
    padding-bottom: 0.25rem;
}
.stApp h2 {
    font-size: 1.75rem !important;
    font-weight: 500 !important;
    line-height: 1.2 !important;
    padding-bottom: 0;
}
.cf-subtitle {
    font-family: 'Inter', sans-serif;
    color: $navy;
    opacity: 0.75;
    font-size: 0.95rem;
    margin: -0.25rem 0 0.5rem;
}

/* Step indicator */
.cf-steps {
    display: flex;
    align-items: center;
    margin: 0.5rem 1rem 1.5rem;
}
.cf-dot {
    width: 30px;
    height: 30px;
    flex: none;
    border-radius: 50%;
    border: 1.5px solid $tan;
    background: $card;
    box-sizing: border-box;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'Inter', sans-serif;
    font-size: 0.8rem;
    color: $navy;
}
.cf-dot.reached {
    color: #FFFFFF;
    font-weight: 600;
}
.cf-dot.current {
    box-shadow: 0 0 0 4px rgba(42, 157, 143, 0.18);
}
.cf-line {
    flex: 1;
    height: 1.5px;
    background: $tan;
}

/* Keep the tile grid and the Back/Next row side by side on phones (Streamlit stacks columns below 640px) */
.st-key-category_grid [data-testid="stHorizontalBlock"], .st-key-nav_row [data-testid="stHorizontalBlock"] {
    flex-wrap: nowrap !important;
}
.st-key-category_grid [data-testid="stColumn"], .st-key-nav_row [data-testid="stColumn"] {
    width: auto !important;
    flex: 1 1 0 !important;
    min-width: 0 !important;
}

/* Home (landing) screen */
.cf-home-title {
    font-family: 'Playfair Display', serif;
    font-size: 2.6rem;
    font-weight: 500;
    color: $navy;
    text-align: center;
    line-height: 1.1;
    margin-top: 0.5rem;
}
.cf-home-tagline {
    font-family: 'Inter', sans-serif;
    font-size: 0.7rem;
    letter-spacing: 0.25em;
    text-transform: uppercase;
    text-align: center;
    color: $navy;
    opacity: 0.7;
    margin: 0.4rem 0 1.25rem;
}
.st-key-hero_card {
    background: linear-gradient(135deg, #FBF4EA 0%, #F1E2CC 100%);
    border: 1px solid $tan;
    border-radius: 20px;
    padding: 1.5rem 1.4rem;
    box-shadow: 0 2px 8px rgba(27, 42, 74, 0.05);
}
.cf-hero-dots {
    display: flex;
    margin-bottom: 0.9rem;
}
.cf-hero-dots span {
    width: 26px;
    height: 26px;
    border-radius: 50%;
    border: 2px solid #FBF4EA;
    margin-right: -9px;
}
.cf-hero-headline {
    font-family: 'Playfair Display', serif;
    font-size: 1.85rem;
    line-height: 1.15;
    color: $navy;
}
.cf-hero-sub {
    font-family: 'Inter', sans-serif;
    font-size: 0.95rem;
    color: $navy;
    opacity: 0.75;
    margin: 0.6rem 0 1rem;
}
.st-key-get_started button {
    background: $teal;
    border: none;
    border-radius: 999px;
    padding: 0.65rem 1.9rem;
}
.st-key-get_started button p {
    color: #FFFFFF;
    font-weight: 500;
    font-size: 1.05rem;
}
.st-key-get_started button:hover, .st-key-get_started button:focus:not(:active) {
    background: #238579;
    color: #FFFFFF;
}
.st-key-hero_card [data-testid="stHorizontalBlock"] {
    flex-wrap: nowrap !important;
    align-items: center;
}
.st-key-hero_card [data-testid="stColumn"] {
    min-width: 0 !important;
}
.cf-how-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.15rem;
    color: $navy;
    margin: 1.4rem 0 0.7rem;
}
.cf-how {
    display: flex;
    gap: 0.6rem;
}
.cf-how-step {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.4rem;
    padding: 0.8rem 0.4rem;
    background: $card;
    border: 1px solid $tan;
    border-radius: 14px;
    font-family: 'Inter', sans-serif;
    font-size: 0.8rem;
    text-align: center;
    color: $navy;
}
.cf-how-num {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background: $teal;
    color: #FFFFFF;
    font-weight: 600;
    display: flex;
    align-items: center;
    justify-content: center;
}

/* Back / Next */
.st-key-nav_back button {
    background: transparent;
    border: none;
    padding: 0.6rem 0.25rem;
}
.st-key-nav_back button:hover, .st-key-nav_back button:focus:not(:active) {
    background: transparent;
    color: $teal;
}
.st-key-nav_back button:hover p {
    color: $teal;
}
.st-key-nav_next {
    display: flex;
    justify-content: flex-end;
    align-self: flex-end;
}
.st-key-nav_next button, .st-key-save_palette button {
    background: $teal;
    border: none;
    border-radius: 999px;
    padding: 0.6rem 1.75rem;
}
.st-key-nav_next button p, .st-key-save_palette button p {
    color: #FFFFFF;
    font-weight: 500;
    font-size: 1.05rem;
}
.st-key-nav_next button:hover, .st-key-save_palette button:hover,
.st-key-nav_next button:focus:not(:active), .st-key-save_palette button:focus:not(:active) {
    background: #238579;
    color: #FFFFFF;
}
.st-key-nav_next button:disabled {
    background: $teal !important;
    border: none !important;
    opacity: 0.4;
}
.st-key-nav_next button:disabled p {
    color: #FFFFFF !important;
}

/* Category cards (shared) */
.st-key-category_list button, .st-key-category_grid button {
    position: relative;
    width: 100%;
    background: $card;
    border: 1px solid $tan;
    border-radius: 14px;
    box-shadow: 0 1px 3px rgba(27, 42, 74, 0.04);
}
.st-key-category_list button:hover, .st-key-category_grid button:hover,
.st-key-category_list button:focus:not(:active), .st-key-category_grid button:focus:not(:active) {
    background: $card;
    border-color: $teal;
    color: $navy;
}
.st-key-category_list button[data-testid="stBaseButton-primary"],
.st-key-category_grid button[data-testid="stBaseButton-primary"] {
    background: $selected_card;
    border: 2px solid $teal;
}
.st-key-category_list button > div, .st-key-category_list button > div > span,
.st-key-category_list [data-testid="stMarkdownContainer"],
.st-key-category_grid button > div, .st-key-category_grid button > div > span,
.st-key-category_grid [data-testid="stMarkdownContainer"] {
    width: 100%;
}
.st-key-category_list button p, .st-key-category_grid button p {
    font-size: 1.05rem;
    font-weight: 500;
}
.st-key-category_list button img, .st-key-category_grid button img {
    max-height: none !important;
    width: auto;
    object-fit: contain;
}

/* Screen 1: full-width rows with a radio circle */
.st-key-category_list button {
    height: 104px;
    padding: 0 1.25rem;
}
.st-key-category_list button p {
    display: flex;
    align-items: center;
    gap: 1.75rem;
    margin: 0;
}
.st-key-category_list button img {
    height: 80px !important;
    width: 90px;
}
.st-key-category_list button::after {
    content: "";
    position: absolute;
    right: 1.25rem;
    top: 50%;
    width: 22px;
    height: 22px;
    margin-top: -11px;
    border-radius: 50%;
    border: 1.5px solid #9AA0AC;
    box-sizing: border-box;
}
.st-key-category_list button[data-testid="stBaseButton-primary"]::after {
    border: 2px solid $teal;
    background: radial-gradient(circle, $teal 0 5.5px, #FFFFFF 6.5px);
}

/* Screen 2: grid tiles with a check circle */
.st-key-category_grid button {
    height: 140px;
    padding: 0.75rem;
}
.st-key-category_grid button p {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.4rem;
    margin: 0;
}
.st-key-category_grid button img {
    display: block;
    height: 82px !important;
}
.st-key-category_grid button::after {
    content: "";
    position: absolute;
    right: 10px;
    top: 10px;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    border: 1.5px solid #9AA0AC;
    box-sizing: border-box;
    color: #FFFFFF;
    font-size: 12px;
    line-height: 17px;
    text-align: center;
}
.st-key-category_grid button[data-testid="stBaseButton-primary"]::after {
    content: "\\2713";
    background: $teal;
    border-color: $teal;
}

/* Screen 3: upload box */
[data-testid="stFileUploaderDropzone"] {
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 170px;
    gap: 0 !important;
    padding: 1.5rem;
    background: $card url("data:image/svg+xml;utf8,$upload_icon") no-repeat center 30px / 40px 40px;
    border: 1.5px dashed $teal;
    border-radius: 14px;
}
[data-testid="stFileUploaderDropzone"]::before {
    content: "Tap to upload";
    margin-top: 48px;
    font-family: 'Inter', sans-serif;
    font-weight: 500;
    font-size: 1.05rem;
    color: $navy;
}
[data-testid="stFileUploaderDropzone"]::after {
    content: "or choose from your gallery";
    margin-top: 0.25rem;
    font-family: 'Inter', sans-serif;
    font-size: 0.85rem;
    color: $navy;
    opacity: 0.7;
}
[data-testid="stFileUploaderDropzoneInstructions"], [data-testid="stFileChips"] {
    display: none;
}
/* Streamlit's own upload / add button becomes an invisible layer over the whole box */
[data-testid="stFileUploaderDropzone"] > :not(input) {
    position: absolute;
    inset: 0;
    margin: 0;
    padding: 0;
}
[data-testid="stFileUploaderDropzone"] button {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    opacity: 0;
    z-index: 1;
}
/* Attached state: shown only while the .cf-attached overlay is rendered inside the upload zone */
.st-key-upload_zone {
    position: relative;
}
.st-key-upload_zone:has(.cf-attached) [data-testid="stFileUploaderDropzone"] {
    background: #E7F3F0;
    border: 1.5px solid $teal;
}
.st-key-upload_zone:has(.cf-attached) [data-testid="stFileUploaderDropzone"]::before,
.st-key-upload_zone:has(.cf-attached) [data-testid="stFileUploaderDropzone"]::after {
    content: none;
}
.st-key-upload_zone [data-testid="stElementContainer"]:has(.cf-attached) {
    position: absolute;
    inset: 0;
    margin: 0;
    pointer-events: none;      /* clicks fall through to the invisible upload button underneath */
    z-index: 2;
    display: flex;
    align-items: center;
    justify-content: center;
}
.cf-attached {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 0.2rem;
    font-family: 'Inter', sans-serif;
    color: $navy;
    text-align: center;
    padding: 0 1rem;
}
.cf-attached-title {
    margin-top: 0.4rem;
    font-weight: 500;
    font-size: 1.05rem;
}
.cf-attached-file {
    font-size: 0.85rem;
    max-width: 100%;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}
.cf-attached-hint {
    font-size: 0.8rem;
    opacity: 0.7;
}
.st-key-preview_card {
    position: relative;
    background: $card;
    border: 1px solid $tan;
    border-radius: 14px;
    padding: 1rem;
}
.st-key-preview_card img {
    border-radius: 10px;
}
.st-key-preview_card [data-testid="stElementToolbar"] {
    display: none;
}
.cf-preview-label {
    font-family: 'Inter', sans-serif;
    font-weight: 500;
    font-size: 0.9rem;
    color: $navy;
}
.st-key-remove_image {
    position: absolute;
    top: 3.25rem;
    right: 1.75rem;
    width: auto !important;
    z-index: 2;
}
.st-key-remove_image button {
    width: 32px;
    height: 32px;
    min-height: 0;
    padding: 0;
    border-radius: 50%;
    border: none;
    background: #FFFFFF;
    box-shadow: 0 1px 4px rgba(27, 42, 74, 0.2);
}
.st-key-remove_image button:hover {
    background: #FFFFFF;
}
.st-key-remove_image button p {
    color: $navy;
}

/* Screen 4: result cards */
.cf-card {
    background: $card;
    border: 1px solid $tan;
    border-radius: 14px;
    padding: 1rem;
    margin-bottom: 0.9rem;
    box-shadow: 0 1px 3px rgba(27, 42, 74, 0.04);
}
.cf-card summary {
    list-style: none;
    cursor: pointer;
}
.cf-card summary::-webkit-details-marker {
    display: none;
}
.cf-card-head {
    display: flex;
    align-items: center;
    gap: 1rem;
}
.cf-thumb {
    width: 64px;
    height: 64px;
    flex: none;
    border-radius: 10px;
    background: #F3ECE2;
    display: flex;
    align-items: center;
    justify-content: center;
}
.cf-thumb img {
    max-width: 54px;
    max-height: 54px;
}
.cf-card-text {
    flex: 1;
    font-family: 'Inter', sans-serif;
    color: $navy;
}
.cf-card-title {
    font-weight: 600;
    font-size: 1.05rem;
}
.cf-badge {
    display: inline-block;
    margin-top: 0.3rem;
    padding: 0.1rem 0.6rem;
    border-radius: 999px;
    background: $teal;
    color: #FFFFFF;
    font-size: 0.7rem;
}
.cf-chevron {
    width: 9px;
    height: 9px;
    margin-right: 0.4rem;
    border-right: 1.5px solid $navy;
    border-bottom: 1.5px solid $navy;
    transform: rotate(45deg);
    transition: transform 0.2s;
}
.cf-card[open] .cf-chevron {
    transform: rotate(-135deg);
}
.cf-swatches {
    display: flex;
    gap: 0.6rem;
    margin-top: 0.9rem;
    padding-left: 0.25rem;
}
.cf-circle {
    width: 38px;
    height: 38px;
    border-radius: 50%;
    border: 1px solid rgba(27, 42, 74, 0.12);
    box-sizing: border-box;
}
.cf-names {
    margin-top: 0.75rem;
    padding-top: 0.6rem;
    border-top: 1px solid $tan;
    font-family: 'Inter', sans-serif;
    font-size: 0.85rem;
    color: $navy;
}
.cf-name-row {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    padding: 0.2rem 0;
}
.cf-name-row .cf-circle {
    width: 16px;
    height: 16px;
}
.cf-tip {
    display: flex;
    gap: 0.9rem;
    align-items: center;
    background: #E3F0EC;
    border-radius: 14px;
    padding: 1rem 1.1rem;
    margin: 0.4rem 0 1rem;
    font-family: 'Inter', sans-serif;
    color: $navy;
}
.cf-tip-main {
    font-size: 0.9rem;
}
.cf-tip-sub {
    font-size: 0.75rem;
    opacity: 0.75;
    margin-top: 0.3rem;
}
.st-key-save_palette button {
    padding: 0.75rem;
}

/* ---------- Phones: screens 3 and 4 must fit one viewport (screens 1-2 and desktop untouched) ---------- */
@media (max-width: 600px) {
    /* Shared by screens 3 and 4 (identified by the upload zone / save button they contain) */
    .stApp:has(.st-key-upload_zone) [data-testid="stMainBlockContainer"],
    .stApp:has(.st-key-save_palette) [data-testid="stMainBlockContainer"] {
        padding-top: 0.75rem;
        padding-bottom: 0.75rem;
    }
    .stApp:has(.st-key-upload_zone) [data-testid="stVerticalBlock"],
    .stApp:has(.st-key-save_palette) [data-testid="stVerticalBlock"] {
        gap: 0.5rem;
    }
    .stApp:has(.st-key-upload_zone) h1, .stApp:has(.st-key-save_palette) h1 {
        font-size: 1.6rem !important;
        padding: 0.25rem 0 0.9rem !important;   /* Streamlit pulls headings up by 1rem, so keep some padding */
    }
    .stApp:has(.st-key-upload_zone) .cf-steps, .stApp:has(.st-key-save_palette) .cf-steps {
        margin: 0.25rem 1rem 0.5rem;
    }
    .stApp:has(.st-key-upload_zone) h2, .stApp:has(.st-key-save_palette) h2 {
        font-size: 1.4rem !important;
        padding: 0.25rem 0 0.9rem !important;
    }
    .stApp:has(.st-key-upload_zone) .cf-subtitle, .stApp:has(.st-key-save_palette) .cf-subtitle {
        font-size: 0.85rem;
        margin: 0 0 1rem;           /* offsets Streamlit's -1rem markdown margin */
    }

    /* Screen 3: compact "Photo added" box and a height-capped preview */
    .st-key-upload_zone:has(.cf-attached) [data-testid="stFileUploaderDropzone"] {
        min-height: 112px;
        padding: 0.5rem;
    }
    .cf-attached svg {
        width: 26px;
        height: 26px;
    }
    .cf-attached {
        gap: 0;
    }
    .cf-attached-title {
        margin-top: 0.1rem;
        font-size: 0.95rem;
    }
    .cf-attached-file, .cf-attached-hint {
        font-size: 0.75rem;
    }
    .st-key-preview_card {
        padding: 0.6rem;
    }
    .st-key-preview_card [data-testid="stFullScreenFrame"] {
        display: flex;
        justify-content: center;
    }
    .st-key-preview_card img {
        max-height: 28vh;
        width: auto !important;
        max-width: 100%;
        margin: 0 auto;
        object-fit: contain;
        object-position: center;
    }
    .st-key-remove_image {
        top: 2.4rem;
        right: 1.2rem;
    }

    /* Screen 4: one compact row per category */
    .cf-card {
        padding: 0.5rem 0.6rem;
        margin-bottom: 0.45rem;
    }
    .cf-card summary {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .cf-card-head {
        display: contents;          /* thumbnail, title and chevron join the summary's single row */
    }
    .cf-thumb {
        width: 40px;
        height: 40px;
        border-radius: 8px;
    }
    .cf-thumb img {
        max-width: 34px;
        max-height: 34px;
    }
    .cf-card-text {
        flex: 0 0 auto;
        min-width: 3.6rem;
    }
    .cf-card-title {
        font-size: 0.9rem;
    }
    .cf-badge {
        font-size: 0.6rem;
        padding: 0 0.4rem;
        margin-top: 0.15rem;
    }
    .cf-swatches {
        order: 1;
        flex: 1;
        margin: 0;
        padding: 0;
        gap: 0.3rem;
        justify-content: flex-end;
    }
    .cf-swatches .cf-circle {
        width: 34px;
        height: 34px;
        flex: none;
    }
    .cf-chevron {
        order: 2;
        flex: none;
        margin: 0 0.2rem 0 0.1rem;
    }
    [data-testid="stElementContainer"]:has(.cf-tip) {
        display: none;
    }
    /* Save My Palette and Back share one row pinned to the bottom of the screen */
    .stApp:has(.st-key-save_palette) [data-testid="stMainBlockContainer"] {
        padding-bottom: 4.5rem;
    }
    .stApp:has(.st-key-save_palette) .st-key-save_palette {
        position: fixed;
        left: 7.5rem;
        right: 1rem;
        bottom: 0.9rem;
        width: auto !important;
        z-index: 10;
    }
    .stApp:has(.st-key-save_palette) .st-key-save_palette button {
        padding: 0.6rem;
    }
    .stApp:has(.st-key-save_palette) .st-key-nav_row {
        position: fixed;
        left: 1rem;
        bottom: 0.9rem;
        width: 6rem !important;
        z-index: 10;
    }
    .stApp:has(.st-key-save_palette) .st-key-nav_row [data-testid="stColumn"]:last-child {
        display: none;               /* the empty Next column; Back gets the whole slot */
    }
}

/* ---------- Phones: the Home screen fits one viewport ---------- */
@media (max-width: 600px) {
    .stApp:has(.st-key-hero_card) [data-testid="stMainBlockContainer"] {
        padding-top: 1rem;
        padding-bottom: 0.75rem;
    }
    .stApp:has(.st-key-hero_card) [data-testid="stVerticalBlock"] {
        gap: 0.5rem;
    }
    .cf-home-title {
        font-size: 2.2rem;
        margin-top: 0;
    }
    .cf-home-tagline {
        margin-bottom: 0.9rem;
    }
    .st-key-hero_card {
        padding: 1.2rem 1.1rem;
    }
    .cf-hero-headline {
        font-size: 1.55rem;
    }
    .cf-hero-sub {
        font-size: 0.88rem;
        margin: 0.5rem 0 0.8rem;
    }
    .cf-how-title {
        margin: 1rem 0 0.5rem;
    }
    .cf-how-step {
        font-size: 0.75rem;
        padding: 0.7rem 0.3rem;
    }
}
</style>
""").substitute(
    navy=NAVY, cream=CREAM, tan=TAN, teal=TEAL, card=CARD, selected_card=SELECTED_CARD,
    corner=CORNER_SVG, upload_icon=UPLOAD_ICON_SVG,
)


def inject_css() -> None:
    """Apply the global ChromaFit theme to the page."""
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


def subtitle(text: str) -> None:
    """Show a short explanatory line under a screen heading."""
    st.markdown(f'<p class="cf-subtitle">{html.escape(text)}</p>', unsafe_allow_html=True)


def teal_shade(fraction: float) -> str:
    """Blend from LIGHT_TEAL (fraction 0) to TEAL (fraction 1) and return the hex color."""
    start = [int(LIGHT_TEAL[i:i + 2], 16) for i in (1, 3, 5)]
    end = [int(TEAL[i:i + 2], 16) for i in (1, 3, 5)]
    r, g, b = (round(s + (e - s) * fraction) for s, e in zip(start, end))
    return f"#{r:02X}{g:02X}{b:02X}"


def step_indicator(current: int) -> None:
    """Show numbered step circles joined by lines; reached steps deepen from light teal up to teal."""
    shades = {n: teal_shade(n / current) for n in range(1, current + 1)}
    parts = []
    for number, label in enumerate(STEP_LABELS, start=1):
        if number > 1:
            if number <= current:
                fill = f"linear-gradient(to right, {shades[number - 1]}, {shades[number]})"
                parts.append(f'<div class="cf-line" style="background: {fill};"></div>')
            else:
                parts.append('<div class="cf-line"></div>')
        if number <= current:
            classes = "cf-dot reached" + (" current" if number == current else "")
            style = f' style="background: {shades[number]}; border-color: {shades[number]};"'
        else:
            classes, style = "cf-dot", ""
        parts.append(f'<div class="{classes}"{style} title="{label}">{number}</div>')
    st.markdown(f'<div class="cf-steps">{"".join(parts)}</div>', unsafe_allow_html=True)


def category_label(category: str) -> str:
    """Return the button label: the product image followed by the category name."""
    return f"![{category.title()}]({CATEGORY_IMAGES[category]}) {category.title()}"


def category_list(options: list[str], selected: str | None, on_click: Callable[[str], None]) -> None:
    """Show full-width selectable rows (single choice), highlighting the selected one."""
    with st.container(key="category_list"):
        for category in options:
            st.button(
                category_label(category),
                key=f"source_{category}",
                type="primary" if category == selected else "secondary",
                on_click=on_click,
                args=(category,),
                width="stretch",
            )


def category_grid(options: list[str], selected: list[str], on_click: Callable[[str], None]) -> None:
    """Show a two-column grid of tiles (multiple choice), highlighting the selected ones."""
    with st.container(key="category_grid"):
        cols = st.columns(2)
        for i, category in enumerate(options):
            cols[i % 2].button(
                category_label(category),
                key=f"target_{category}",
                type="primary" if category in selected else "secondary",
                on_click=on_click,
                args=(category,),
                width="stretch",
            )


def result_card(category: str, colors: list[NamedColor], badge: str | None = None) -> None:
    """Show an expandable card: product thumbnail, title, swatch row, and color names when opened."""
    badge_html = f'<div class="cf-badge">{html.escape(badge)}</div>' if badge else ""
    circles = "".join(
        f'<div class="cf-circle" style="background-color: {c.to_hex()};" title="{html.escape(c.name)}"></div>'
        for c in colors
    )
    names = "".join(
        f'<div class="cf-name-row"><div class="cf-circle" style="background-color: {c.to_hex()};"></div>'
        f"{html.escape(c.name)}</div>"
        for c in colors
    )
    st.markdown(
        f'<details class="cf-card"><summary>'
        f'<div class="cf-card-head">'
        f'<div class="cf-thumb"><img src="{CATEGORY_IMAGES[category]}" alt=""></div>'
        f'<div class="cf-card-text"><div class="cf-card-title">{html.escape(category.title())}</div>'
        f'{badge_html}</div>'
        f'<div class="cf-chevron"></div></div>'
        f'<div class="cf-swatches">{circles}</div>'
        f'</summary><div class="cf-names">{names}</div></details>',
        unsafe_allow_html=True,
    )


def tip_box() -> None:
    """Show the closing tip card on the results screen."""
    st.markdown(
        f'<div class="cf-tip">{PALETTE_ICON_SVG}<div>'
        f'<div class="cf-tip-main">A simple color change can make a big difference!</div>'
        f'<div class="cf-tip-sub">Mix, match and feel your best.</div></div></div>',
        unsafe_allow_html=True,
    )


def palette_png(source: str, dominant: NamedColor, recommendations: dict) -> bytes:
    """Draw the dominant color and every recommended color with its name into a PNG image."""
    rows = [(f"Your {source}", [dominant])] + [
        (category.title(), [color for color, _score in matches])
        for category, matches in recommendations.items()
    ]
    width, row_height, circle = 640, 150, 64
    image = Image.new("RGB", (width, 90 + row_height * len(rows)), CREAM)
    draw = ImageDraw.Draw(image)
    title_font = ImageFont.load_default(size=30)
    label_font = ImageFont.load_default(size=18)
    small_font = ImageFont.load_default(size=13)

    draw.text((32, 28), "ChromaFit palette", fill=NAVY, font=title_font)
    for row, (label, colors) in enumerate(rows):
        top = 90 + row * row_height
        draw.text((32, top), label, fill=NAVY, font=label_font)
        for i, color in enumerate(colors):
            left = 32 + i * 112
            draw.ellipse((left, top + 32, left + circle, top + 32 + circle), fill=color.rgb, outline=TAN, width=2)
            draw.text((left + circle / 2, top + 108), color.name, fill=NAVY, font=small_font, anchor="mt")

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def init_state() -> None:
    """Set default session values on the first run."""
    defaults = {
        "screen": HOME,
        "source": None,
        "targets": [],
        "image_bytes": None,
        "image_suffix": None,
        "image_name": None,
        "uploader_version": 0,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def go_to(screen: int | str) -> None:
    """Switch to the given screen and rerun the script."""
    st.session_state["screen"] = screen
    st.rerun()


def nav_buttons(can_advance: bool) -> None:
    """Show Back/Next buttons; Next is disabled until the screen is complete."""
    screen = st.session_state["screen"]
    back_col, next_col = st.container(key="nav_row").columns(2)

    if back_col.button("←  Back", key="nav_back"):
        go_to(HOME if screen == FIRST_SCREEN else screen - 1)
    if screen < LAST_SCREEN and next_col.button("Next  →", key="nav_next", disabled=not can_advance):
        go_to(screen + 1)


def select_source(category: str) -> None:
    """Make the clicked category the item the user has."""
    st.session_state["source"] = category


def toggle_target(category: str) -> None:
    """Add the clicked category to the targets, or remove it if already chosen."""
    targets = st.session_state["targets"]
    if category in targets:
        st.session_state["targets"] = [t for t in targets if t != category]
    else:
        st.session_state["targets"] = targets + [category]


def uploader_key() -> str:
    """Return the current file uploader key; bumping the version gives a fresh, empty uploader."""
    return f"uploader_{st.session_state['uploader_version']}"


def store_upload() -> None:
    """Copy the uploaded file into session state so it survives screen changes."""
    uploaded = st.session_state.get(uploader_key())
    if uploaded is None:
        st.session_state["image_bytes"] = None
        st.session_state["image_suffix"] = None
        st.session_state["image_name"] = None
    else:
        st.session_state["image_bytes"] = uploaded.getvalue()
        st.session_state["image_suffix"] = os.path.splitext(uploaded.name)[1]
        st.session_state["image_name"] = uploaded.name


def remove_upload() -> None:
    """Forget the uploaded image and reset the uploader."""
    st.session_state["image_bytes"] = None
    st.session_state["image_suffix"] = None
    st.session_state["image_name"] = None
    st.session_state["uploader_version"] += 1


@st.cache_data(show_spinner=False)
def run_recommendation(image_bytes: bytes, suffix: str, targets: list[str], top_n: int) -> dict:
    """Write the image to a temp file and run the recommendation pipeline on it."""
    tmp = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
    try:
        tmp.write(image_bytes)
        tmp.close()
        service = StylistService(RepositoryFactory.create("sqlite"))
        return service.recommend(tmp.name, targets=targets, top_n=top_n)
    finally:
        tmp.close()
        os.remove(tmp.name)


def screen_source() -> None:
    """Screen 1: pick the item the user already has."""
    st.header("Which item do you have?", anchor=False)
    subtitle("Choose the main item you want to get color recommendations for.")
    choice = st.session_state["source"]
    category_list(CATEGORIES, choice, select_source)
    nav_buttons(can_advance=choice is not None)


def screen_targets() -> None:
    """Screen 2: pick the items to get color recommendations for."""
    st.header("Which items do you need colors for?", anchor=False)
    subtitle("Select all that apply.")
    options = [c for c in CATEGORIES if c != st.session_state["source"]]
    chosen = [t for t in st.session_state["targets"] if t in options]
    st.session_state["targets"] = chosen
    category_grid(options, chosen, toggle_target)
    nav_buttons(can_advance=len(chosen) > 0)


def attached_state(file_name: str | None) -> None:
    """Overlay the dropzone with the "Photo added" state: check icon, file name, replace hint."""
    st.markdown(
        f'<div class="cf-attached">{CHECK_ICON_SVG}'
        f'<div class="cf-attached-title">Photo added</div>'
        f'<div class="cf-attached-file">{html.escape(file_name or "")}</div>'
        f'<div class="cf-attached-hint">Tap to replace</div></div>',
        unsafe_allow_html=True,
    )


def screen_upload() -> None:
    """Screen 3: upload a photo of the item and preview it."""
    st.header("Upload a photo of your item", anchor=False)
    subtitle("Use a clear, well-lit photo for the best results.")
    image_bytes = st.session_state["image_bytes"]
    with st.container(key="upload_zone"):
        st.file_uploader(
            "Image", type=["jpg", "jpeg", "png"], key=uploader_key(),
            on_change=store_upload, label_visibility="collapsed",
        )
        if image_bytes is not None:
            attached_state(st.session_state["image_name"])
    if image_bytes is not None:
        with st.container(key="preview_card"):
            st.markdown('<div class="cf-preview-label">Preview</div>', unsafe_allow_html=True)
            st.button("✕", key="remove_image", on_click=remove_upload)
            st.image(image_bytes, width="stretch")
    nav_buttons(can_advance=image_bytes is not None)


def screen_results() -> None:
    """Screen 4: run the pipeline and show the recommendations as color cards."""
    st.header("Your Color Recommendations", anchor=False)
    subtitle("Here are the best colors for your selected items.")
    with st.spinner("Analyzing image..."):
        result = run_recommendation(
            st.session_state["image_bytes"],
            st.session_state["image_suffix"],
            st.session_state["targets"],
            TOP_N,
        )

    source = st.session_state["source"]
    dominant = NamedColor("dominant color", result["dominant"])
    result_card(source, [dominant], badge="Dominant color")

    for category, matches in result["recommendations"].items():
        colors = [color for color, _score in matches]
        result_card(category, colors)

    tip_box()
    st.download_button(
        "Save My Palette",
        data=palette_png(source, dominant, result["recommendations"]),
        file_name="chromafit_palette.png",
        mime="image/png",
        key="save_palette",
        on_click="ignore",
        width="stretch",
    )
    nav_buttons(can_advance=False)


def screen_home() -> None:
    """Landing screen: header, hero card with Get Started, and a short "How it works" row."""
    st.markdown(
        '<div class="cf-home-title">ChromaFit</div>'
        '<div class="cf-home-tagline">Better colors. Brighter you.</div>',
        unsafe_allow_html=True,
    )
    dots = "".join(f'<span style="background: {color};"></span>' for color in (TAN, TEAL, NAVY, CREAM))
    with st.container(key="hero_card"):
        text_col, image_col = st.columns([3, 2]) if HERO_IMAGE.exists() else (st.container(), None)
        with text_col:
            st.markdown(
                f'<div class="cf-hero-dots">{dots}</div>'
                '<div class="cf-hero-headline">Find the perfect colors for your style</div>'
                '<div class="cf-hero-sub">Upload your items, get personalized color suggestions.</div>',
                unsafe_allow_html=True,
            )
            if st.button("Get Started  →", key="get_started"):
                go_to(FIRST_SCREEN)
        if image_col is not None:
            image_col.image(str(HERO_IMAGE), width="stretch")

    steps = "".join(
        f'<div class="cf-how-step"><div class="cf-how-num">{number}</div>{html.escape(label)}</div>'
        for number, label in enumerate(HOW_IT_WORKS, start=1)
    )
    st.markdown(
        f'<div class="cf-how-title">How it works</div><div class="cf-how">{steps}</div>',
        unsafe_allow_html=True,
    )


SCREENS = {
    HOME: screen_home,
    1: screen_source,
    2: screen_targets,
    3: screen_upload,
    4: screen_results,
}


def main() -> None:
    """Render whichever screen the session is currently on."""
    inject_css()
    init_state()
    screen = st.session_state["screen"]
    if screen != HOME:
        st.title("ChromaFit", anchor=False)
        step_indicator(screen)
    SCREENS[screen]()


main()
