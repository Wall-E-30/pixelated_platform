import os

def create_gallery():
    assets_dir = "assets"
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Asset Gallery</title>
        <style>
            body { font-family: sans-serif; background: #222; color: #fff; padding: 20px; }
            h1 { color: #ff5e00; }
            .category { margin-bottom: 30px; border-bottom: 1px solid #444; padding-bottom: 10px; }
            .gallery { display: flex; flex-wrap: wrap; gap: 15px; }
            .card { background: #333; border: 1px solid #555; border-radius: 8px; padding: 10px; text-align: center; width: 300px; }
            .card img { max-width: 100%; height: auto; display: block; margin: 0 auto 10px; background: #444; image-rendering: pixelated; }
            .info { font-size: 12px; color: #ccc; word-break: break-all; }
        </style>
    </head>
    <body>
        <h1>Asset Gallery</h1>
    """
    
    for folder in sorted(os.listdir(assets_dir)):
        folder_path = os.path.join(assets_dir, folder)
        if not os.path.isdir(folder_path):
            continue
            
        html_content += f'<div class="category"><h2>{folder}</h2><div class="gallery">'
        
        files = sorted(os.listdir(folder_path))
        for f in files:
            if f.lower().endswith('.png'):
                file_path = os.path.join(assets_dir, folder, f)
                # Use relative path for web browser
                rel_path = f"assets/{folder}/{f}"
                html_content += f"""
                <div class="card">
                    <img src="{rel_path}" alt="{f}" />
                    <div class="info">
                        <strong>{f}</strong><br/>
                        Path: {rel_path}
                    </div>
                </div>
                """
        html_content += '</div></div>'
        
    html_content += """
    </body>
    </html>
    """
    
    with open("gallery.html", "w") as f:
        f.write(html_content)
    print("gallery.html generated successfully.")

if __name__ == "__main__":
    create_gallery()
