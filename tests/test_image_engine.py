"""
Tests for Image Processing Engine: Resize, rotate, flip, format conversions (PNG, JPEG, WebP).
"""
import unittest
import os
import tempfile
from pathlib import Path
from PIL import Image

from core.image_engine import ImageEngine

class TestImageEngine(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.d = Path(self.temp_dir.name)
        
        self.sample_png = str(self.d / "test.png")
        img = Image.new("RGBA", (400, 300), color=(255, 100, 50, 255))
        img.save(self.sample_png)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_resize_and_rotate(self):
        out_img = str(self.d / "resized.png")
        res = ImageEngine.process_image(
            input_path=self.sample_png,
            output_path=out_img,
            resize_mode="exact",
            target_width=200,
            target_height=150,
            keep_aspect=False,
            rotate_angle=90
        )
        self.assertTrue(os.path.exists(out_img))
        with Image.open(out_img) as processed:
            self.assertEqual(processed.size, (200, 150))

    def test_format_conversion_to_webp(self):
        out_webp = str(self.d / "test.webp")
        res = ImageEngine.process_image(
            input_path=self.sample_png,
            output_path=out_webp,
            target_format="WEBP",
            quality=80
        )
        self.assertTrue(os.path.exists(out_webp))
        with Image.open(out_webp) as img:
            self.assertEqual(img.format, "WEBP")

    def test_format_conversion_to_jpeg(self):
        out_jpg = str(self.d / "test.jpg")
        res = ImageEngine.process_image(
            input_path=self.sample_png,
            output_path=out_jpg,
            target_format="JPEG",
            quality=75
        )
        self.assertTrue(os.path.exists(out_jpg))
        with Image.open(out_jpg) as img:
            self.assertEqual(img.format, "JPEG")

    def test_batch_processing(self):
        # Create multiple images
        imgs = []
        for i in range(3):
            p = str(self.d / f"batch_{i}.png")
            Image.new("RGB", (200, 200), (i * 50, 100, 150)).save(p)
            imgs.append(p)
            
        out_dir = str(self.d / "batch_out")
        results = ImageEngine.batch_process(
            image_paths=imgs,
            output_dir=out_dir,
            settings={"target_format": "WEBP", "quality": 85}
        )
        self.assertEqual(len(results), 3)
        for r in results:
            self.assertIn("output_path", r)
            self.assertTrue(os.path.exists(r["output_path"]))

if __name__ == "__main__":
    unittest.main()
