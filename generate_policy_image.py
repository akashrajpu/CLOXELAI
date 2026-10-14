from PIL import Image, ImageDraw, ImageFont
import textwrap

bg_path = "/Users/mrakash/.gemini/antigravity/brain/5f8dd979-890e-459f-be50-1b375fed88e9/privacy_bg_1791636460020.jpg"
img = Image.open(bg_path).convert("RGBA")

overlay = Image.new('RGBA', img.size, (0, 0, 0, 180))
img = Image.alpha_composite(img, overlay)
draw = ImageDraw.Draw(img)

# Fonts
font_title = ImageFont.truetype("/Library/Fonts/Arial Unicode.ttf", 43)
font_subtitle = ImageFont.truetype("/Library/Fonts/Arial Unicode.ttf", 18)
font_heading = ImageFont.truetype("/Library/Fonts/Arial Unicode.ttf", 23)
font_body = ImageFont.truetype("/Library/Fonts/Arial Unicode.ttf", 17)
font_signature = ImageFont.truetype("/System/Library/Fonts/Supplemental/Brush Script.ttf", 60)

color_white = (255, 255, 255, 255)
color_purple = (192, 132, 252, 255)
color_gray = (203, 213, 225, 255)

y = 80
margin = 80
width = img.width - (margin * 2)

# CENTER SUBTITLE
sub_text = "OFFICIAL LEGAL DOCUMENT • PRIVACY POLICY"
sub_bbox = draw.textbbox((0, 0), sub_text, font=font_subtitle)
sub_w = sub_bbox[2] - sub_bbox[0]
draw.text(((img.width - sub_w) / 2, y), sub_text, font=font_subtitle, fill=color_purple)
y += 35

# CENTER TITLE
title_text = "Privacy Policy & User Terms"
title_bbox = draw.textbbox((0, 0), title_text, font=font_title)
title_w = title_bbox[2] - title_bbox[0]
draw.text(((img.width - title_w) / 2, y), title_text, font=font_title, fill=color_white)
y += 55

draw.line([(margin, y), (img.width - margin, y)], fill=color_purple, width=2)
y += 40

content = [
    ("1. Advanced Binary Security Architecture", "Cloxel AI utilizes high-level Binary Cryptographic Hash Architecture & SHA-256 Protocol Encryption to eliminate vulnerabilities. Account authorization relies directly on binary token handshakes and encrypted credentials."),
    ("2. User Password Disclosure Disclaimer", "While Cloxel AI implements state-of-the-art Binary Encryption, users remain 100% solely and completely responsible for maintaining strict password secrecy. If a user voluntarily or accidentally discloses, shares, or reveals their account credentials to any third party, Cloxel AI, its website, infrastructure, servers, and Founder Akash Raj hold ZERO legal liability, financial responsibility, or obligation for any resulting account breach or data loss."),
    ("3. YouTube API & Third-Party Integration", "By connecting YouTube channels, users agree to YouTube Terms of Service and Google Privacy Policy. Cloxel AI accesses OAuth tokens strictly for automated video publishing initiated by the user."),
    ("4. Data Retention & Privacy", "We do not sell, rent, or share your personal data with third parties. All generated media and scripts are securely stored and tied exclusively to your authenticated account session.")
]

for heading, body in content:
    draw.text((margin, y), heading, font=font_heading, fill=color_white)
    y += 32
    
    lines = textwrap.wrap(body, width=88)
    for line in lines:
        draw.text((margin, y), line, font=font_body, fill=color_gray)
        y += 26
    y += 35

# Footer section placed dynamically after the text
y += 10
draw.line([(margin, y), (img.width - margin, y)], fill=(255, 255, 255, 50), width=1)
y += 30

draw.text((margin, y + 10), "✓ VERIFIED LEGAL POLICY DOC • REPUBLIC OF INDIA", font=font_subtitle, fill=color_purple)

sig_text = "Akash Raj"
sig_bbox = draw.textbbox((0, 0), sig_text, font=font_signature)
sig_width = sig_bbox[2] - sig_bbox[0]

# Draw signature on the right
sig_x = img.width - margin - sig_width - 20
draw.text((sig_x, y - 35), sig_text, font=font_signature, fill=color_purple)
draw.text((sig_x + 20, y + 35), "Akash Raj", font=ImageFont.truetype("/Library/Fonts/Arial Unicode.ttf", 20), fill=color_white)
draw.text((sig_x + 20, y + 60), "Founder & CEO, Cloxel AI", font=ImageFont.truetype("/Library/Fonts/Arial Unicode.ttf", 16), fill=color_gray)

img = img.convert("RGB")
img.save("frontend/public/privacy_policy_doc.jpg")
print("Image generated successfully!")
