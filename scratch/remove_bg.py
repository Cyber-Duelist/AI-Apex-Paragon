from PIL import Image
import sys

def make_transparent(image_path):
    try:
        # Re-open the original generated image from the brain temp storage
        # Wait, the copy in the brain folder is unmodified, let's use that
        import glob
        original_images = glob.glob("C:\\Users\\adars\\.gemini\\antigravity\\brain\\c4b852cf-2429-4cfa-91b5-e9a76c341d65\\ultraman_sprite_*.png")
        if not original_images:
            print("No original image found!")
            return
        
        orig_path = original_images[0]
        img = Image.open(orig_path).convert("RGBA")
        datas = img.getdata()

        newData = []
        for item in datas:
            # More aggressive dark background removal (RGB < 60)
            if item[0] < 60 and item[1] < 60 and item[2] < 60:
                newData.append((255, 255, 255, 0))
            else:
                newData.append(item)

        img.putdata(newData)
        
        # Save back to the website folder
        dest_path = "D:\\Apex_Paragon\\AI-APEX-PARAGON\\portfolio_website\\ultraman.png"
        img.save(dest_path, "PNG")
        print(f"Successfully processed and saved to {dest_path}")
    except Exception as e:
        print(f"Error processing {image_path}: {e}")

if __name__ == "__main__":
    make_transparent("")
